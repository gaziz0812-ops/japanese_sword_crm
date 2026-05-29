from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    MANAGER = 'manager', 'Менеджер'
    CUSTOMER = 'customer', 'Покупатель'


class User(AbstractUser):
    telegram_id = models.BigIntegerField('Telegram ID', unique=True, null=True, blank=True)
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
