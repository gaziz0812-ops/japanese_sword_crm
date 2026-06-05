from django.urls import path

from .views import OrderCreateAPIView


urlpatterns = [
    # Этот URL принимает POST /api/orders/ и передает запрос в OrderCreateAPIView.
    path('', OrderCreateAPIView.as_view(), name='order-create'),
]