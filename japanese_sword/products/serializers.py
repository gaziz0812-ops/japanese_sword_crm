from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    # stock_balance не хранится в БД, а считается через @property в модели Product
    stock_balance = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product  # модель, с которой работает сериализатор
        fields = (  # поля/атрибуты, которые попадут в JSON-ответ API
            'id',
            'sku',
            'name',
            'manufacturer',
            'sale_price',
            'is_active',
            'stock_balance',
        )