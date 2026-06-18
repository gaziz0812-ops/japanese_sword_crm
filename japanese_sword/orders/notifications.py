from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings


# [OUR] Отправляет текстовое сообщение в конкретный Telegram chat_id.
def send_telegram_message(chat_id, text):
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return

    query = urlencode({
        'chat_id': chat_id,
        'text': text,
    })

    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage?{query}'

    with urlopen(url, timeout=5) as response:
        response.read()


# Эта функция собирает текст уведомления о новом заказе.
def send_new_order_notification(order):
    # select_related подтягивает товар каждой позиции, чтобы не делать лишние запросы к БД.
    items = order.items.select_related('product')

    lines = [
        f'Новый заказ #{order.id}',
        f'Клиент: {order.customer_name or "-"}',
        f'Telegram: {order.telegram_username or "-"}',
        f'Телефон: {order.phone or "-"}',
        '',
        'Товары:',
    ]

    for item in items:
        lines.append(
            f'- {item.product} x {item.quantity} = {item.total_price} руб.'
        )

    lines.extend([
        '',
        f'Сумма: {order.total_amount} руб.',
    ])

    # "\n".join(lines) склеивает список строк в один текст сообщения.
    send_telegram_message(settings.TELEGRAM_ADMIN_CHAT_ID, '\n'.join(lines))


# [OUR] Отправляет клиенту подтверждение, если заказ связан с Telegram-пользователем.
def send_customer_order_created_notification(order):
    customer = order.customer

    if not customer or not customer.telegram_id:
        return

    text = (
        f'Заказ создан.\n'
        f'Сумма: {order.total_amount} руб.\n\n'
        'Скоро с Вами свяжусь.'
    )

    send_telegram_message(customer.telegram_id, text)


# [OUR] Отправляет клиенту трек-номер, когда заказ переведен в статус "Отправлен".
def send_customer_order_shipped_notification(order):
    customer = order.customer

    if not customer or not customer.telegram_id:
        return

    text = (
        f'Заказ #{order.id} отправлен.\n'
        f'Трек-номер: {order.tracking_number}\n\n'
        'Спасибо за покупку!'
    )

    send_telegram_message(customer.telegram_id, text)
