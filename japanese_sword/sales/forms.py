from django import forms

from .models import Sale


class ProductPriceSelect(forms.Select):
    price_map = {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            product = getattr(value, 'instance', None)
            sale_price = product.sale_price if product else self.price_map.get(str(value), '')
            option['attrs']['data-sale-price'] = str(sale_price)

        return option


class SaleAdminForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'product': ProductPriceSelect,
        }
        labels = {
            'discount_percent': 'Discount, %',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        product_field = self.fields['product']
        product_field.widget.price_map = {
            str(product.pk): str(product.sale_price)
            for product in product_field.queryset
        }
