from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    # Поле не хранится в БД, а считается методом get_stock_status()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product  # модель, с которой работает сериализатор
        fields = (  # поля/атрибуты, которые попадут в JSON-ответ API
            'id',
            'sku',
            'name',
            'sale_price',
            'stock_status',
        )

    def get_stock_status(self, obj):
        if obj.stock_balance > 1:
            return "В наличии"

        if obj.stock_balance == 1:
            return "Осталась 1 шт."

        return "Нет в наличии"
