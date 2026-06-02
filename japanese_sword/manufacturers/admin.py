from django.contrib import admin
from django import forms
from django.db import models

from .models import Manufacturer

#  Регистрация модели в админке
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    formfield_overrides = {
        models.CharField: {
            'widget': forms.TextInput(attrs={'style': 'width: 350px;'}),
        },
    }