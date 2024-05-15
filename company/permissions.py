from rest_framework import permissions
from .models import Company

class IsSameCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.company_id == view.kwargs.get('id')
    