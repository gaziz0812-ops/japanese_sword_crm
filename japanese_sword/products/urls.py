from django.urls import include, path
from rest_framework.routers import DefaultRouter # роутер DRF сам создает URL для ViewSet

from .views import ProductViewSet


router = DefaultRouter()
#
router.register('', ProductViewSet, basename='product') # /api/products/ и /api/products/<id>


urlpatterns = [
    path('', include(router.urls)), # подключаем URL, которые создал router
]