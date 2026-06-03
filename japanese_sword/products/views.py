from rest_framework import viewsets # готовые классы DRF для API-представлений
from rest_framework import filters

from .models import Product
from .serializers import ProductSerializer

# Класс дает только чтение: список товаров и один товар
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    # Публичный каталог показывает только товары в наличии/не в наличии/все
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        stock = self.request.query_params.get('stock')

        if stock in ('available', 'out'):
            product_ids = [
                product.id
                for product in queryset
                if (
                    product.stock_balance > 0
                    if stock == 'available'
                    else product.stock_balance <= 0
                )
            ]

            queryset = queryset.filter(id__in=product_ids)

        return queryset

    # Каждый товар превращать в JSON через ProductSerializer
    serializer_class = ProductSerializer

    # SearchFilter включает поиск через query-параметр ?search=
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)

    # Специальный атрибут SearchFilter: поля, по которым работает ?search=
    search_fields = ('sku', 'name')

    # Специальный атрибут OrderingFilter: поля, по которым разрешена сортировка
    ordering_fields = ('name', 'sale_price')

    # Специальный атрибут OrderingFilter: сортировка по умолчанию
    ordering = ('name',)
