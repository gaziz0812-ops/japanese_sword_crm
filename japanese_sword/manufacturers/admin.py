from django.contrib import admin

from .models import Manufacturer


@admin.register(Manufacturer) # регистрация модели Мануфактура в админке с настройками ниже
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
