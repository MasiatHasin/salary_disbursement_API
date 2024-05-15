from django.contrib import admin
from .models import Profile, CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(Profile)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email')
    search_fields = ('username',)
    fieldsets = (
        (None, {
            'classes': ['wide'],
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'classes': ['wide'],
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'classes': ['wide'],
            'fields': ('is_superuser', 'is_staff', 'is_active', 'is_verified', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'classes': ['wide'],
            'fields': ('last_login', 'date_joined')
        }),
        ('Company', {
            'classes': ['wide'],
            'fields': ('company',)
        })
    )
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(CustomUser, CustomUserAdmin)
