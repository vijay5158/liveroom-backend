
from Liveroom.views import index
from Accounts.views import UserViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', index),
    path('', include('rest_framework.urls')),
    path('api/', include('Accounts.urls')),
    path('api/class/', include('Classes.urls')),

] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)
if (settings.DEBUG):
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
