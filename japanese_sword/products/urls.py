from django.urls import include, path
from rest_framework.routers import DefaultRouter # роутер DRF сам создает URL для ViewSet

from .views import ProductViewSet


# Легенда комментариев:
# [DRF] механизм Django REST Framework.
# [DJANGO] механизм Django.
# [OUR] наше имя view/router basename.

# [DRF] DefaultRouter сам генерирует URL для ViewSet: list и detail.
router = DefaultRouter()

# Регистрируем ProductViewSet на корне products.urls: /api/products/ и /api/products/<id>/.
# [DRF] router.register() связывает ViewSet с URL; [OUR] basename='product' — наше имя ресурса.
router.register('', ProductViewSet, basename='product')


# [DJANGO] urlpatterns — специальное имя: Django ищет здесь список URL приложения.
urlpatterns = [
    # Подключаем URL, которые автоматически создал DRF router.
    # [DJANGO] include() подключает сгенерированные router.urls.
    path('', include(router.urls)),
]
