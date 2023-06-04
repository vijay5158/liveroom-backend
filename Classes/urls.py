from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import ClassroomView, PostViewSet, CommentViewSet, AnnouncementView, ClassroomDataView, AttendanceAPIView

router = DefaultRouter()
router.register(r'classes', ClassroomView, basename='classes')
router.register(r'class', ClassroomDataView, basename='class_data')
router.register(r'post', PostViewSet, basename='post')
router.register(r'comment', CommentViewSet, basename='comment')
router.register(r'announcement', AnnouncementView, basename='announcement')

# urlpatterns = router.urls

urlpatterns = [
        re_path(r'', include(router.urls)),
        path("mark-attendance/", AttendanceAPIView.as_view(), name="mark_attendance"),

]
