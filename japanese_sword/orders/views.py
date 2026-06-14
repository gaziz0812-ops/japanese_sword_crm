# csrf_exempt отключает Django CSRF-проверку для публичного API endpoint-а.
from django.utils.decorators import method_decorator

# csrf_exempt нужен, потому что заказ создает внешний клиент: Vue/Telegram Mini App, а не Django-форма.
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics

from .models import Order
from .serializers import OrderCreateSerializer

# Для публичного API заказа CSRF отключаем: позже безопасность будет через проверку Telegram initData.
@method_decorator(csrf_exempt, name='dispatch')

# CreateAPIView дает endpoint только для создания объекта через POST.
class OrderCreateAPIView(generics.CreateAPIView):
    # queryset нужен DRF как базовый набор объектов модели Order.
    queryset = Order.objects.all()

    # serializer_class говорит DRF, каким serializer проверять JSON и создавать Order.
    serializer_class = OrderCreateSerializer