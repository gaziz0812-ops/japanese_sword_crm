from django.contrib import admin

from .forms import SaleAdminForm
from .models import Sale


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
    readonly_fields = ('unit_sale_price', 'total_sale_amount', 'profit', 'created_at')

    class Media:
        js = ('sales/admin_sale_calculator.js',)
