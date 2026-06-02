from rest_framework import viewsets # готовые классы DRF для API-представлений

from .models import Product
from .serializers import ProductSerializer

# Класс дает только чтение: список товаров и один товар
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    # определяет, какие товары API будет брать из БД
    queryset = Product.objects.select_related('manufacturer').all()
    # Каждый товар превращать в JSON через ProductSerializer
    serializer_class = ProductSerializer