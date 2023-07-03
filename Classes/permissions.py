from rest_framework import permissions

class IsRoleTeacher(permissions.BasePermission):
    message = 'You are not authorized.'

    def has_permission(self, request, view):
        if request.user.is_teacher:
            return True
        else:
            return False

class IsRoleStudent(permissions.BasePermission):
    message = 'You are not authorized.'

    def has_permission(self, request, view):
        if request.user.is_student:
            return True
        else:
            return False
