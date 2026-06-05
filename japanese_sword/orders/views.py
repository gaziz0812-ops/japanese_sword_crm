from rest_framework import generics

from .models import Order
from .serializers import OrderCreateSerializer


# CreateAPIView дает endpoint только для создания объекта через POST.
class OrderCreateAPIView(generics.CreateAPIView):
    # queryset нужен DRF как базовый набор объектов модели Order.
    queryset = Order.objects.all()

    # serializer_class говорит DRF, каким serializer проверять JSON и создавать Order.
    serializer_class = OrderCreateSerializer