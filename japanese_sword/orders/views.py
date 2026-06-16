# csrf_exempt отключает Django CSRF-проверку для публичного API endpoint-а.
from django.utils.decorators import method_decorator

# csrf_exempt нужен, потому что заказ создает внешний клиент: Vue/Telegram Mini App, а не Django-форма.
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics

from .models import Order
from .serializers import OrderCreateSerializer


# Легенда комментариев:
# [DRF] имя/метод/атрибут, который ожидает Django REST Framework.
# [DJANGO] механизм Django.
# [OUR] наше имя, наша бизнес-логика.

# Для публичного API заказа CSRF отключаем: позже безопасность будет через проверку Telegram initData.
# [DJANGO] method_decorator применяет csrf_exempt к class-based view.
@method_decorator(csrf_exempt, name='dispatch')

# CreateAPIView дает endpoint только для создания объекта через POST.
# [OUR] Название класса наше; [DRF] CreateAPIView уже умеет принимать POST и вызывать serializer.save().
class OrderCreateAPIView(generics.CreateAPIView):
    # queryset нужен DRF как базовый набор объектов модели Order.
    # [DRF] queryset — специальный атрибут view-класса.
    queryset = Order.objects.all()

    # serializer_class говорит DRF, каким serializer проверять JSON и создавать Order.
    # [DRF] serializer_class — специальный атрибут view-класса.
    serializer_class = OrderCreateSerializer
