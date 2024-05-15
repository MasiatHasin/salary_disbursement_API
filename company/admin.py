from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import Company

admin.site.register(Company)
admin.site.register(Permission)