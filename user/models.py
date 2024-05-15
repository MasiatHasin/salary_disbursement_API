from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache

class CustomUser(AbstractUser):
    company = models.ForeignKey(
        'company.Company',
        on_delete = models.SET_DEFAULT,
        default = 0
    )
    is_verified = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        cache_key_list = cache._cache.get_client().keys('*')
        for c in cache_key_list:
            cache_key = c.decode('utf-8')
            if 'user_all_' in cache_key:
                cache.delete(cache_key[3:])
        super(CustomUser, self).save(*args, **kwargs)

class Profile(models.Model):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    user = models.OneToOneField(
        'user.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    first_name = models.CharField(max_length=200, blank = False)
    last_name = models.CharField(max_length=200, blank = False)
    gender = models.CharField(choices = gender_choices, blank = False)
    dob = models.DateField(blank = False)
    mobile = models.CharField(max_length = 11, blank = False)
    address = models.CharField(max_length=200, blank = False)

    def __str__(self):
        return f'user: {self.user}'
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)