from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage, default_storage
from salary_disbursement import settings
from .storage import OverwriteStorage
from django.core.cache import cache

class Salary(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.IntegerField(blank = False)
    wallet_no = models.IntegerField(blank = False)
    amount = models.IntegerField(blank = False)
    beneficiary = models.ForeignKey(
        'salary.Beneficiary',
        on_delete = models.CASCADE,
        default = 0
    )
    company = models.ForeignKey(
        'company.Company',
        on_delete = models.CASCADE,
        default = 0
    )

    def __str__(self):
        return f'ID: {self.id}, Company: {self.company}'
    
    def save(self, *args, **kwargs):
        cache_key_list = cache._cache.get_client().keys('*')
        for c in cache_key_list:
            cache_key = c.decode('utf-8')
            if 'salary_all_' in cache_key:
                cache.delete(cache_key[3:])
        super(Salary, self).save(*args, **kwargs)

class Beneficiary(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(blank = False, null = False, storage = OverwriteStorage())
    filepath = models.CharField(max_length=100, blank = False)
    uploader = models.ForeignKey(
        'user.CustomUser',
        on_delete=models.PROTECT)
    company = models.ForeignKey(
        'company.Company',
        on_delete = models.CASCADE,
        default = 0
    )
    schedule_time = models.DateTimeField(blank = True, null=True)
    created = models.DateTimeField(default = timezone.now)
    is_approved = models.BooleanField(default=False)
    is_complete = models.BooleanField(default = False)

    def __str__(self):
        return f'File: {self.file}'

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.IntegerField(blank = False, null= False)
    wallet_no = models.IntegerField(blank = False, null= False)
    amount = models.IntegerField(blank = False, null= False)
    created = models.DateTimeField(default = timezone.now)
    company = models.ForeignKey(
        'company.Company',
        on_delete = models.CASCADE,
        default = 0
    )

    def __str__(self):
        return f'ID: {self.id}, Wallet No: {self.wallet_no}, Amount: {self.amount}, Created: {self.created}'