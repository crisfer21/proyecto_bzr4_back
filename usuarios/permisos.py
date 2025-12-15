from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'jefe venta'


class IsVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'vendedor'


class IsAdminOrVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['jefe venta', 'vendedor']
