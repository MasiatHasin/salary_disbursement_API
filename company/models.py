from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.core.cache import cache

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.CharField(max_length=200, blank = False, unique = True)
    founded_year = models.IntegerField(blank = False, validators=[MaxValueValidator(datetime.date.today().year)])
    description = models.TextField(blank = False)
    is_active = models.BooleanField(blank = True)
    industry = models.CharField(max_length=200, blank = False)
    website = models.URLField(blank = False)
    email = models.EmailField(blank = False)
    created = models.DateTimeField(default = timezone.now)
    updated = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return f'{self.organization}'
    
    def save(self, *args, **kwargs):
        cache_key_list = cache._cache.get_client().keys('*')
        for c in cache_key_list:
            cache_key = c.decode('utf-8')
            if 'company_all_' in cache_key:
                cache.delete(cache_key[3:])
        super(Company, self).save(*args, **kwargs)