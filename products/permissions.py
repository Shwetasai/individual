from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsRetailer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'retailer'

class IsCustomerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Allow any user to perform safe methods like GET
        return request.user.is_authenticated and request.user.role == 'customer'

class IsRetailerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Allow any user to perform safe methods like GET
        return request.user.is_authenticated and request.user.role == 'retailer'