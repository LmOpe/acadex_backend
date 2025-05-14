from rest_framework import permissions


class IsCourseInstructor(permissions.BasePermission):
    """
    Custom permission to only allow course instructors to perform operations on their courses.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'lecturer_profile') and obj.course.instructor == request.user.lecturer_profile
