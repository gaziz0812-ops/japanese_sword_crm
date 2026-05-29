from django.db import models
from django.db.models import Sum


class Product(models.Model):
    sku = models.CharField('Артикул', max_length=64, unique=True)
    name = models.CharField('Название', max_length=255)
    manufacturer = models.ForeignKey(
        'manufacturers.Manufacturer',
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Производитель',
    )
    description = models.TextField('Описание', blank=True)
    sale_price = models.DecimalField('Цена продажи, руб.', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.sku} - {self.name} ({self.sale_price} руб.)'

    @property
    def stock_balance(self):
        totals = self.stock_movements.values('movement_type').annotate(
            total=Sum('quantity')
        )
        movement_totals = {item['movement_type']: item['total'] for item in totals}

        inbound = movement_totals.get('inbound', 0) or 0
        returned = movement_totals.get('return', 0) or 0
        sale = movement_totals.get('sale', 0) or 0
        write_off = movement_totals.get('write_off', 0) or 0
        reserve = movement_totals.get('reserve', 0) or 0
        unreserve = movement_totals.get('unreserve', 0) or 0

        return inbound + returned + unreserve - sale - write_off - reserve
