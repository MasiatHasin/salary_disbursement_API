from rest_framework import permissions
from .models import Beneficiary, Salary

class IsSameCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.kwargs.get('id') is not None:
            try:
                salary = Salary.objects.get(id = view.kwargs.get('id'))
                return request.user.company_id == salary.company_id
            except:
                try:
                    beneficiary = Beneficiary.objects.get(id = view.kwargs.get('id'))
                    return request.user.company_id == beneficiary.company_id
                except:
                    return True
        return True