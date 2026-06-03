from rest_framework import viewsets # готовые классы DRF для API-представлений
from rest_framework import filters

from .models import Product
from .serializers import ProductSerializer

# Класс дает только чтение: список товаров и один товар
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    # Специальный метод DRF: возвращает queryset товаров для текущего HTTP-запроса
    def get_queryset(self):
        # Базовый queryset: публичный каталог показывает только активные товары
        queryset = Product.objects.filter(is_active=True)

        # query_params читает параметры URL после знака ?/&
        stock = self.request.query_params.get('stock')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        # stock=available показывает товары с остатком, stock=out — товары без остатка
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

            # id__in оставляет в queryset только товары, id которых есть в списке product_ids
            queryset = queryset.filter(id__in=product_ids)

        # sale_price__gte означает "цена больше или равна min_price"
        if min_price:
            queryset = queryset.filter(sale_price__gte=min_price)

        # sale_price__lte означает "цена меньше или равна max_price"
        if max_price:
            queryset = queryset.filter(sale_price__lte=max_price)

        # DRF ждет, что get_queryset вернет итоговый queryset для serializer
        return queryset

    # Специальный атрибут DRF: каким serializer превращать Product в JSON
    serializer_class = ProductSerializer

    # SearchFilter включает поиск через query-параметр ?search=
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)

    # Специальный атрибут SearchFilter: поля, по которым работает ?search=
    search_fields = ('sku', 'name')

    # Специальный атрибут OrderingFilter: поля, по которым разрешена сортировка
    ordering_fields = ('name', 'sale_price')

    # Специальный атрибут OrderingFilter: сортировка по умолчанию
    ordering = ('name',)
