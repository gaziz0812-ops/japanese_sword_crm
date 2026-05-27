from django.db import models


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        INBOUND = 'inbound', 'Приход'
        SALE = 'sale', 'Продажа'
        RETURN = 'return', 'Возврат'
        WRITE_OFF = 'write_off', 'Списание'
        RESERVE = 'reserve', 'Резерв'
        UNRESERVE = 'unreserve', 'Снятие резерва'

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='stock_movements',
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )
    quantity = models.IntegerField()
    source_type = models.CharField(max_length=50, blank=True)
    source_id = models.PositiveBigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product} | {self.movement_type} | {self.quantity}'