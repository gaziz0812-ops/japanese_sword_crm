from rest_framework import serializers

from .models import Product


# Легенда комментариев:
# [DRF] имя/метод/атрибут, который ожидает Django REST Framework.
# [OUR] наше поле/метод или наша бизнес-логика.


# ModelSerializer строит JSON-представление на основе модели Product.
# [OUR] Название класса наше; [DRF] ModelSerializer связывает serializer с моделью Product.
class ProductSerializer(serializers.ModelSerializer):
    # SerializerMethodField говорит DRF взять значение поля из метода get_stock_status().
    # [DRF] SerializerMethodField ищет метод get_<field_name>(), то есть get_stock_status().
    stock_status = serializers.SerializerMethodField()

    # [DRF] Meta — специальное имя: DRF сам читает model и fields.
    class Meta:
        # model связывает serializer с моделью Product.
        # [DRF] model — специальный атрибут Meta.
        model = Product

        # fields перечисляет публичные поля, которые попадут в JSON-ответ API.
        # [DRF] fields — специальный атрибут Meta.
        fields = (
            'id',
            'sku',
            'name',
            'sale_price',
            'stock_status',
            'image'
        )

    # [DRF] get_stock_status() вызывается для поля stock_status.
    def get_stock_status(self, obj):
        # obj здесь конкретный Product, который DRF сейчас превращает в JSON.
        # [OUR] stock_balance — наше вычисляемое свойство модели Product.
        if obj.stock_balance > 1:
            return "В наличии"

        if obj.stock_balance == 1:
            return "Осталась 1 шт."

        return "Нет в наличии"


# Этот serializer используется для страницы одного товара: GET /api/products/<id>/
# [OUR] Название класса наше; наследуем короткий serializer и расширяем fields.
class ProductDetailSerializer(ProductSerializer):
    # Meta наследуется от ProductSerializer.Meta, чтобы не дублировать model = Product.
    # [DRF] Meta(ProductSerializer.Meta) — расширение настроек родительского serializer.
    class Meta(ProductSerializer.Meta):
        # В detail-ответ добавляем описание товара, которого нет в коротком списке.
        # [DRF] fields остается специальным атрибутом; [OUR] добавляем 'description'.
        fields = ProductSerializer.Meta.fields + (
            'description',
        )
