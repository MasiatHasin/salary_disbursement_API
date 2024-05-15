from django.contrib import admin
from .models import Transaction, Beneficiary
# Register your models here.
admin.site.register(Transaction)
admin.site.register(Beneficiary)