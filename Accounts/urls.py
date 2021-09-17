from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactView, RegistrationAPIView, UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet, basename='users')
urlpatterns = [
        path('register/', RegistrationAPIView.as_view(), name = 'Register' ),
        path('contact/', ContactView.as_view(), name = 'Contact' ),
        url('list/', include(router.urls)),
]
