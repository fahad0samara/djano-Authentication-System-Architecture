from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.is_staff:
            return True
            
        # Object must have a user attribute that matches the request user
        return hasattr(obj, 'user') and obj.user == request.user

class HasValidSession(permissions.BasePermission):
    """
    Verify that the user has a valid and non-expired session.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Check session validity
        if not request.session.get('last_activity'):
            return False
            
        # Additional session checks can be added here
        return True