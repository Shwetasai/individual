from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsRetailer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_retailer

class IsCustomerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and request.user.is_customer
        return request.user.is_authenticated and request.user.is_retailer
