from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission class to allow only administrators
    or the users themselves to access their own data.
    
    This permission is used for the UserViewSet to ensure that:
    - Administrators can view and edit any user's data
    - Regular users can only view and edit their own data
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the object.
        
        - Admins can access any user's data
        - Regular users can only access their own data
        """
        # Allow if the user is an admin
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Allow if the accessed object is the user themselves
        return obj.id == request.user.id
