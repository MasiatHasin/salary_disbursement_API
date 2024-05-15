from rest_framework import serializers
from .models import Profile
from company.serializers import Company
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import Group
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from .permissions import IsAdmin, IsManager

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        else:
            if check_password(data['password'], self.context['request'].user.password):
                raise serializers.ValidationError({"password": "Password cannot be same as before."})
        return data
    
    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
    
class SuperRegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'context' in kwargs:
            context = kwargs['context']
            if 'request' in context:
                request = context['request']
                if request.method == 'PATCH':
                    for name,field in self.fields.items():
                        field.required = False
                    self.fields['password'].validators = []
    
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'], 
            email = validated_data['email'], 
            password = validated_data['password'],
            is_staff = True,
            is_superuser = True,
            is_verified = True
        )
        user.set_password(validated_data['password'])
        user.save()
        user.groups.add(Group.objects.get(name='Superuser') )
        return user

class RegisterSerializer(SuperRegisterSerializer):
    company_id = serializers.IntegerField(required = True)
    group = serializers.CharField(required = True, write_only = True)
    first_name = serializers.CharField(write_only = True, required = True)
    last_name = serializers.CharField(write_only = True, max_length=200, required = True)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], write_only=True, required = True)
    dob = serializers.DateField(write_only = True, required = True)
    mobile = serializers.CharField(write_only = True, max_length = 11, required = True)
    address = serializers.CharField(write_only = True, max_length=200, required = True)
        

    def create(self, validated_data):
        current_user = self.context['request'].user
        try:
            company_id = Company.objects.filter(id=validated_data['company_id']).first()
        except:
            if current_user.is_superuser:
                company_id = Company.objects.get(id=0)
            else:
                company_id = Company.objects.get(id=current_user.company_id)
        user = User.objects.create(
            username = validated_data['username'], 
            email = validated_data['email'], 
            password = validated_data['password'],
            company = company_id
        )
        user.set_password(validated_data['password'])
        user.save()
        group = Group.objects.get(name=validated_data['group']) 
        user.groups.add(group)
        id = user.id
        profile = Profile.objects.create(
            user_id = id,
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            mobile = validated_data['mobile'],
            gender = validated_data['gender'],
            dob = validated_data['dob'],
            address = validated_data['address']
        )
        profile.save()
        return user
    
    def update(self, instance, validated_data):
        profile = Profile.objects.get(user_id = instance.id)
        for key,value in validated_data.items():
            if key not in ['password', 'password2']:
                if key in ['username', 'email', 'company_id']:
                    setattr(instance, key, value)
                if key in ['first_name', 'last_name', 'gender', 'dob', 'mobile', 'address']:
                    setattr(profile, key, value)   
        profile.save() 
        instance.save()
        return instance

class ProfileSerializer(serializers.Serializer):
    group = serializers.SerializerMethodField(method_name='get_groups')
    first_name = serializers.CharField(max_length=200, required = True)
    last_name = serializers.CharField(max_length=200, required = True)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], required = True)
    dob = serializers.DateField(required = True)
    mobile = serializers.CharField(max_length = 11, required = True)
    address = serializers.CharField(max_length=200, required = True)

    def get_groups(self, request):
        groups = request.user.groups.values_list('name',flat = True)
        groups= list(groups)
        return groups