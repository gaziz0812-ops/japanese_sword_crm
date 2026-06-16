from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Легенда комментариев:
# [DJANGO] имя/функция, которые ожидает Django.
# [OUR] наши приложения и наши API-маршруты.

# [DJANGO] urlpatterns — специальное имя: Django ищет здесь главный список URL проекта.
urlpatterns = [
    # [DJANGO] admin.site.urls подключает стандартную Django admin.
    path('admin/', admin.site.urls),

    # Подключаем публичный API каталога товаров.
    # [OUR] products.urls — URL нашего приложения products.
    path('api/products/', include('products.urls')),

    # Подключаем публичный API создания заказов
    # [OUR] orders.urls — URL нашего приложения orders.
    path('api/orders/', include('orders.urls')),
]

# В режиме разработки Django сам раздает загруженные медиафайлы по MEDIA_URL.
# [DJANGO] settings.DEBUG — настройка Django; static() добавляет dev-маршруты для MEDIA.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
