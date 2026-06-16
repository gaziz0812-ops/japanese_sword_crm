# Decimal нужен для безопасной работы с денежными значениями
# InvalidOperation возникает, если строку нельзя преобразовать в Decimal
from decimal import Decimal, InvalidOperation

# ValidationError DRF возвращает клиенту HTTP 400 Bad Request
from rest_framework.exceptions import ValidationError

# filters содержит готовые DRF-фильтры для поиска и сортировки.
# viewsets содержит готовые DRF-классы для API-представлений.
from rest_framework import filters, viewsets

from .models import Product
from .serializers import ProductDetailSerializer, ProductSerializer


# Легенда комментариев:
# [DRF] имя/метод/атрибут, который ожидает Django REST Framework.
# [ORM] запрос к базе через Django ORM.
# [OUR] наша переменная, наше условие или наша бизнес-логика.
# [PY] обычный Python / стандартная библиотека.


# ReadOnlyModelViewSet дает публичному API только чтение: список товаров и один товар.
# [OUR] Название класса наше; [DRF] ReadOnlyModelViewSet дает готовые actions list/retrieve.
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    # Специальный метод DRF: возвращает queryset товаров для текущего HTTP-запроса
    # [DRF] get_queryset() — hook, который DRF вызывает перед чтением объектов.
    def get_queryset(self):
        # Базовый queryset: публичный каталог показывает только активные товары
        # [ORM] Product.objects.filter(...) делает SQL-запрос к таблице товаров.
        queryset = Product.objects.filter(is_active=True)

        # query_params читает параметры URL после знака ? и после разделителей &.
        # [DRF] self.request.query_params — параметры текущего HTTP-запроса.
        stock = self.request.query_params.get('stock')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        # stock=available показывает товары с остатком, stock=out — товары без остатка
        if stock in ('available', 'out'):
            # [OUR] product_ids — наш список id товаров, отфильтрованных по вычисляемому stock_balance.
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
            # [ORM] id__in — lookup Django ORM: SQL-аналог WHERE id IN (...).
            queryset = queryset.filter(id__in=product_ids)

        # min_price приходит из URL строкой, поэтому преобразуем его в Decimal
        if min_price:
            try:
                # [PY] Decimal превращает строку из URL в денежное число без float-ошибок.
                min_price = Decimal(min_price)
            except InvalidOperation:
                # [DRF] ValidationError вернет клиенту HTTP 400 Bad Request.
                raise ValidationError({
                    'min_price': 'Минимальная цена должна быть числом.'
                })

        # max_price приходит из URL строкой, поэтому преобразуем его в Decimal
        if max_price:
            try:
                # [PY] Decimal превращает строку из URL в денежное число без float-ошибок.
                max_price = Decimal(max_price)
            except InvalidOperation:
                # [DRF] ValidationError вернет клиенту HTTP 400 Bad Request.
                raise ValidationError({
                    'max_price': 'Максимальная цена должна быть числом.'
                })

        # Если переданы обе цены, минимальная не должна быть больше максимальной
        if min_price and max_price and min_price > max_price:
            raise ValidationError({
                'max_price': 'Максимальная цена должна быть больше или равна минимальной.'
            })

        # sale_price__gte означает "цена больше или равна min_price"
        if min_price:
            queryset = queryset.filter(sale_price__gte=min_price)

        # sale_price__lte означает "цена меньше или равна max_price"
        if max_price:
            queryset = queryset.filter(sale_price__lte=max_price)

        # DRF ждет, что get_queryset вернет итоговый queryset для serializer
        # [DRF] return queryset — обязательный итог get_queryset().
        return queryset

    # Специальный метод DRF: выбирает serializer в зависимости от действия ViewSet.
    # [DRF] get_serializer_class() — hook выбора serializer-класса.
    def get_serializer_class(self):
        # self.action — специальный атрибут DRF: list для списка, retrieve для одного объекта.
        # [DRF] self.action заполняет ViewSet: 'list', 'retrieve' и т.д.
        if self.action == 'retrieve':
            return ProductDetailSerializer

        # Для списка товаров оставляем короткий публичный serializer.
        return ProductSerializer

    # Специальный атрибут DRF: каким serializer превращать Product в JSON.  Если есть get_serializer, то превращается
    # в атрибут по сериализатор по умолчанию
    # [DRF] serializer_class — fallback serializer, если get_serializer_class() не выбрал другой.
    serializer_class = ProductSerializer

    # Специальный атрибут DRF: эти backend-классы дополнительно обрабатывают queryset.
    # [DRF] filter_backends включает готовые механизмы search и ordering.
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)

    # Специальный атрибут SearchFilter: поля, по которым работает ?search=
    # [DRF] search_fields читает SearchFilter.
    search_fields = ('sku', 'name')

    # Специальный атрибут OrderingFilter: поля, по которым разрешена сортировка
    # [DRF] ordering_fields читает OrderingFilter.
    ordering_fields = ('name', 'sale_price')

    # Специальный атрибут OrderingFilter: сортировка по умолчанию
    # [DRF] ordering — сортировка по умолчанию, если клиент не передал ?ordering=.
    ordering = ('name',)
