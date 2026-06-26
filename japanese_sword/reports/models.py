from sales.models import Sale


# Proxy-модель нужна только для пункта "Сводка продаж" в левом меню админки.
# [DJANGO] proxy=True говорит Django не создавать отдельную таблицу в базе.
class SalesSummaryReport(Sale):
    class Meta:
        proxy = True
        verbose_name = 'Сводка продаж'
        verbose_name_plural = 'Сводка продаж'
        app_label = 'reports'