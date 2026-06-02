from django.db import models

#  определены поля для заполнения
class Manufacturer(models.Model):
    name = models.CharField('Название', max_length=255, unique=True)
    contacts = models.TextField('Контакты', blank=True)
    notes = models.TextField('Заметки', blank=True)

    class Meta:
        verbose_name = 'Производителя'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name
