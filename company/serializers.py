from rest_framework import serializers
from .models import Company
from user.models import CustomUser as User
import datetime

class CompanySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    organization = serializers.CharField(max_length=200, required = True)
    founded_year = serializers.IntegerField(required = True, max_value = datetime.date.today().year)
    description = serializers.CharField(required = True)
    is_active = serializers.BooleanField(required = True)
    industry = serializers.CharField(max_length=200, required = True)
    website = serializers.URLField(required = True)
    email = serializers.EmailField(required = True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'context' in kwargs:
            context = kwargs['context']
            if 'request' in context:
                request = context['request']
                if request.method == 'PATCH':
                    for name,field in self.fields.items():
                        field.required = False

    def create(self, validated_data):
        user = self.context['request'].user
        company = Company.objects.create(**validated_data)
        return company
    
    def update(self, instance, validated_data):
        for key,value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
