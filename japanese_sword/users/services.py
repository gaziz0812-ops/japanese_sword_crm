# Импортируем нашу модель пользователя и набор ролей из приложения users.
from .models import User, UserRole


# Это наша обычная Python-функция: Django сам ее не вызывает, мы позже вызовем ее из serializer заказов.
def get_or_create_telegram_user(telegram_data):
    # Telegram ID — главный стабильный идентификатор пользователя в Telegram.
    telegram_id = telegram_data.get('id')

    # Если Telegram ID не пришел, мы не можем надежно связать заказ с пользователем.
    if not telegram_id:
        return None

    # Username в Telegram может отсутствовать, поэтому делаем технический username через telegram_id.
    username = telegram_data.get('username') or f'tg_{telegram_id}'

    # Имя и фамилия могут прийти из Telegram, но могут быть пустыми.
    first_name = telegram_data.get('first_name', '')
    last_name = telegram_data.get('last_name', '')

    # update_or_create ищет пользователя по telegram_id; если нашел — обновляет, если не нашел — создает.
    user, created = User.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            # username нужен стандартной модели Django User.
            'username': username,

            # first_name и last_name — стандартные поля AbstractUser.
            'first_name': first_name,
            'last_name': last_name,

            # Все пользователи из Telegram Mini App по умолчанию считаются покупателями.
            'role': UserRole.CUSTOMER,
        },
    )

    # Возвращаем объект User, чтобы позже привязать его к Order.customer.
    return user