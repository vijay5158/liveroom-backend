from django.urls import include, path,re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
    TokenVerifyView
)
from .views import ContactView, RegistrationAPIView, UserViewSet, LoginView, GetTemplate

router = DefaultRouter()
router.register('user', UserViewSet, basename='users')
urlpatterns = [
        re_path('list/', include(router.urls)),
        path('register/', RegistrationAPIView.as_view(), name = 'Register' ),
        path('face/', GetTemplate.as_view(), name = 'Face' ),
        path('contact/', ContactView.as_view(), name = 'Contact' ),
        path("login/", LoginView.as_view(), name="login"),
        path("jwt/create/", TokenObtainPairView.as_view(), name="jwt_create"),
        path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("logout/", TokenBlacklistView.as_view(), name='token_blacklist'),
]
