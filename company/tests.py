from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from .models import Company
from django.contrib.auth import get_user_model
User = get_user_model()

class CompanyTests(APITestCase):
    def setUp(self):
        Company.objects.create(
            id = 0,
            organization = "Default",
            founded_year = 2024,
            description = "",
            is_active = True,
            industry = "",
            website = "",
            email = ""
        )
        Group.objects.create(name="Admin")
        Group.objects.create(name="Manager")
        Group.objects.create(name="Superuser")

        suser = User.objects.create(
            username = "Super",
            email = "super@gmail.com",
            is_verified = True,
            is_superuser = True
        )
        suser.set_password("drf@2024!")
        group = Group.objects.get(name='Superuser') 
        suser.groups.add(group)
        suser.save()

        user = User.objects.create(
            username = "Mashiat",
            email = "mashiat@gmail.com",
            is_verified = True  
        )
        user.set_password("drf@2024!")
        group = Group.objects.get(name='Admin') 
        user.groups.add(group)
        user.save()

    def registerCompanyBySuperuser(self):
        response = self.client.post('/user/login/', {"username": "Super", "password": "drf@2024!"}, format="json")
        token = response.data['access']

        data = {
            "organization": "Square",
            "founded_year": "1958",
            "description": "Square Pharmaceuticals Ltd. is a Bangladeshi multinational pharmaceutical company.",
            "is_active": "True",
            "industry": "Pharmaceuticals",
            "website": "https://www.squarepharma.com.bd/",
            "email": "contact@squarepharma.com"
        }
        response = self.client.post('/company/register/', data, format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def registerCompanyByAdmin(self):
        response = self.client.post('/user/login/', {"username": "Mashiat", "password": "drf@2024!"}, format="json")
        token = response.data['access']

        data = {
            "organization": "Square2",
            "founded_year": "1958",
            "description": "Square Pharmaceuticals Ltd. is a Bangladeshi multinational pharmaceutical company.",
            "is_active": "True",
            "industry": "Pharmaceuticals",
            "website": "https://www.squarepharma.com.bd/",
            "email": "contact@squarepharma.com"
        }
        response = self.client.post('/company/register/', data, format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_all(self):
        self.registerCompanyBySuperuser()
        self.registerCompanyByAdmin()