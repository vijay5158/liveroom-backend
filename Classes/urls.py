from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .views import ClassroomView, PostViewSet, CommentViewSet, AnnouncementView

router = DefaultRouter()
router.register(r'classes', ClassroomView, basename='classes')
router.register(r'post', PostViewSet, basename='post')
router.register(r'comment', CommentViewSet, basename='comment')
router.register(r'announcement', AnnouncementView, basename='announcement')

# urlpatterns = router.urls

urlpatterns = [
    url(r'', include(router.urls)),

]
