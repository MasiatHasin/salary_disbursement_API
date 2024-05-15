from rest_framework import permissions
from django.contrib.auth import get_user_model
User = get_user_model()

class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
    
class IsSameUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return view.kwargs.get('id') == request.user.id

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()
    
class IsManager(permissions.BasePermission):
     def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
    
class IsVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_verified)

class IsSameCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            user = User.objects.filter(id = view.kwargs.get('id')).first()
            try:
                return request.user.company_id == user.company_id
            except:
                return False
        elif request.method=="POST":
            if request.data["company_id"]:
                return request.user.company_id == request.data["company_id"]
        return True