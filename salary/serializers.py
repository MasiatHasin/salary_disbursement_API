from rest_framework import serializers
from .models import Transaction, Beneficiary, Salary
from django.conf import settings
from user.models import CustomUser as User
import os
import csv
from .tasks import add_salary, disburse
from datetime import datetime, timedelta
from pytz import timezone

class SalarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    employee_id = serializers.CharField(max_length = 100)
    wallet_no = serializers.IntegerField()
    amount = serializers.IntegerField()
    beneficiary_id = serializers.IntegerField(read_only = True)

    def update(self, instance, validated_data):
        for key,value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class TransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    employee_id = serializers.IntegerField(read_only = True)
    wallet_no = serializers.IntegerField(read_only = True)
    amount = serializers.IntegerField(read_only = True)
    created = serializers.DateTimeField(read_only = True)
    company_id = serializers.IntegerField(read_only = True)

    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

class BeneficiarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    file = serializers.FileField(write_only = True, required = True)
    filepath = serializers.CharField(read_only = True)
    company_id = serializers.IntegerField(read_only = True)
    uploader_id = serializers.IntegerField(read_only = True)
    created = serializers.DateTimeField(read_only = True)
    is_approved = serializers.BooleanField(read_only = True)
    is_complete = serializers.BooleanField(read_only = True)
    schedule_time = serializers.DateTimeField(required=False, write_only = True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'context' in kwargs:
            context = kwargs['context']
            if 'request' in context:
                request = context['request']
                if request.method == 'PATCH':
                    self.fields['is_approved'].read_only = False
                    self.fields['is_approved'].required = True
                    self.fields['file'].write_only = False
                    self.fields['file'].required = False
                    self.fields['schedule_time'].required = True
                    
    """ def validate_file(self, value):
        if Beneficiary.objects.filter(file=value.name, company_id = self.context['request'].user.company_id).exists():
            raise serializers.ValidationError("File with the same name already exists.")
        return value """
    
    def create(self, validated_data):
        file = validated_data['file']
        user = self.context['request'].user
        file = Beneficiary.objects.create(
            file = file,
            filepath = str(settings.MEDIA_URL)+str(validated_data['file']).split('.')[0],
            uploader = user,
            company_id = self.context['request'].user.company_id
        )
        file.filepath = str(settings.MEDIA_URL)+str(file.file)
        file.save()
        res = add_salary.delay(file.filepath[1:], file.id, user.company_id)
        return file
    
    def update(self, instance, validated_data):
        if bool(validated_data['is_approved']) == True:
            schedule_time = validated_data['schedule_time']
            instance.schedule_time = schedule_time
            instance.is_approved = True
            instance.save()
            disburse.apply_async(args=(instance.id, instance.company_id,), eta=schedule_time)
            return instance
        else:
            return None
