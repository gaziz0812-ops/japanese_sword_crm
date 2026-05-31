from django.contrib import admin

from .forms import SaleAdminForm
from .models import Sale, SaleCostAllocation


class SaleCostAllocationInline(admin.TabularInline):
    model = SaleCostAllocation
    verbose_name = 'Списание себестоимости'
    verbose_name_plural = 'Списания себестоимости'
    extra = 0
    can_delete = False
    readonly_fields = ('stock_batch', 'quantity', 'unit_cost', 'total_cost', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    form = SaleAdminForm
    list_display = (
        'id',
        'product',
        'customer',
        'quantity',
        'discount_percent',
        'unit_sale_price',
        'total_sale_amount',
        'cost_price',
        'profit',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('product__sku', 'product__name', 'customer__username')
    readonly_fields = ('unit_sale_price', 'total_sale_amount', 'cost_price', 'profit', 'created_at')
    inlines = (SaleCostAllocationInline,)
    fieldsets = (
        ('Продажа', {
            'fields': ('product', 'customer', 'quantity', 'discount_percent', 'comment'),
        }),
        ('Расчёт', {
            'fields': ('unit_sale_price', 'total_sale_amount', 'profit'),
        }),
        ('Служебные данные', {
            'fields': ('created_at',),
        }),
    )

    class Media:
        js = ('sales/admin_sale_calculator.js',)
