from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('menu/', include('apps.recipes.urls')),
    path('users/', include('apps.users.urls')),
    path('cart/', include('apps.orders.urls')),
    path('partners/', include('apps.partners.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
