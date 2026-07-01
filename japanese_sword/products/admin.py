from django import forms
from django.contrib import admin

from .models import Product, ProductImage


class MultipleFileInput(forms.ClearableFileInput):
    # [DJANGO] allow_multiple_selected разрешает одному file input принять сразу несколько файлов.
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    # [OUR] Поле формы для массовой загрузки фотографий; в модель Product оно не сохраняется напрямую.
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        # [DJANGO] clean() валидирует данные поля формы перед сохранением формы админки.
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]

        return single_file_clean(data, initial)


class ProductAdminForm(forms.ModelForm):
    # [OUR] Временное поле формы: позволяет выбрать пачку фото в админке товара.
    gallery_upload = MultipleFileField(
        label='Загрузить несколько фото',
        required=False,
        help_text='Можно выбрать несколько файлов сразу. Они добавятся в галерею товара после сохранения.',
    )

    class Meta:
        model = Product
        fields = '__all__'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# @admin.register связывает модель Product с настройками ProductAdmin в админке.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # form подключает нашу расширенную форму товара с полем массовой загрузки фото.
    form = ProductAdminForm

    # list_display определяет колонки в списке товаров админки.
    list_display = ('id', 'sku', 'name', 'manufacturer', 'sale_price', 'is_active', 'display_stock_balance')

    # list_filter добавляет боковые фильтры в админке.
    list_filter = ('is_active', 'manufacturer')

    # search_fields включает поиск по артикулу и названию товара.
    search_fields = ('sku', 'name')

    fieldsets = (
        ('Товар', {
            'fields': ('sku', 'name', 'manufacturer', 'description', 'image', 'sale_price', 'is_active'),
        }),
        ('Галерея', {
            'fields': ('gallery_upload',),
        }),
    )

    inlines = (ProductImageInline,)

    def save_model(self, request, obj, form, change):
        # [DJANGO] save_model() вызывается админкой при сохранении основного товара.
        super().save_model(request, obj, form, change)

        # [OUR] После сохранения Product создаем отдельные ProductImage для каждого файла из пачки.
        for image in form.cleaned_data.get('gallery_upload') or []:
            ProductImage.objects.create(product=obj, image=image)

    # admin.display задает название вычисляемой колонки в админке.
    @admin.display(description='Остаток')
    def display_stock_balance(self, obj):
        # obj здесь конкретный Product из строки админки, не ProductAdmin.
        return obj.stock_balance
