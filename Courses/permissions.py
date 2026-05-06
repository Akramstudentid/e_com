from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow admin users or staff to edit, allow others read-only access.
    Admin users have role='admin' or is_staff=True
    """
    def has_permission(self, request, view):
        # Allow read-only access for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, check if user is admin
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.role == 'admin'
        )


class IsAdmin(permissions.BasePermission):
    """
    Allow only admin users (role='admin' or is_staff=True).
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.role == 'admin')
        )


class IsAdminUser(permissions.BasePermission):
    """
    Allow only admin users. Similar to IsAdmin but more explicit.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.role == 'admin')
        )