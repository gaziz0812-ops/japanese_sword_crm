from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'manufacturer', 'sale_price', 'is_active', 'display_stock_balance')
    list_filter = ('is_active', 'manufacturer')
    search_fields = ('sku', 'name')

    @admin.display(description='Остаток')
    def display_stock_balance(self, obj):
        return obj.stock_balance
