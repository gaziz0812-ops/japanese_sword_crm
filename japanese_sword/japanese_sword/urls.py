from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключаем публичный API каталога товаров.
    path('api/products/', include('products.urls')),
]

# В режиме разработки Django сам раздает загруженные медиафайлы по MEDIA_URL.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
