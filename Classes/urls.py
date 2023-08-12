from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import ClassroomView, PostViewSet, CommentViewSet, AnnouncementView, ClassroomDataView, AttendanceAPIView, ListAttendance, CreateAssignmentAPIView, GetAssignmentAPIView, CreateAssignmentSubmissionAPIView, AssignmentSubmissionAPIView, CheckAssignmentSubmissionAPIView

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
        path("get-attendance", ListAttendance.as_view(), name="list_attendance"),
        path("create-assignment/<slug:slug>/", CreateAssignmentAPIView.as_view(), name="create_assignment"),
        path("get-assignments/<slug:slug>/", GetAssignmentAPIView.as_view(), name="get_assignment"),
        path("submit-assignment/<slug:slug>/", CreateAssignmentSubmissionAPIView.as_view(), name="create_assignment_submission"),
        path("get-assignment-submission/<slug:slug>/", AssignmentSubmissionAPIView.as_view(), name="get_assignment_submissions"),
        path("check-assignment-submission/<slug:slug>/", CheckAssignmentSubmissionAPIView.as_view(), name="check_assignment_submission"),
]
