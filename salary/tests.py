from rest_framework.test import APITestCase
from rest_framework import status
from company.models import Company
from django.contrib.auth.models import Group
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
from company.models import Company
from .models import Transaction

class SalaryTests(APITestCase):
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

        Company.objects.create(
            id = 1,
            organization= "Square",
            founded_year= "1958",
            description= "Square Pharmaceuticals Ltd. is a Bangladeshi multinational pharmaceutical company.",
            is_active= "True",
            industry = "Pharmaceuticals",
            website = "https://www.squarepharma.com.bd/",
            email = "contact@squarepharma.com"
        )

        user = User.objects.create(
            username = "Mashiat",
            email = "mashiat@gmail.com",
            is_verified = True,
            company_id = 1
        )
        user.set_password("drf@2024!")
        group = Group.objects.get(name='Admin') 
        user.groups.add(group)
        user.save()

        user2 = User.objects.create(
            username = "Noshin",
            email = "noshin@gmail.com",
            is_verified = True,
            company_id = 1
        )
        user2.set_password("drf@2024!")
        group = Group.objects.get(name='Manager') 
        user2.groups.add(group)
        user2.save()
    
    def fileUpload(self, token):
        file = open('./media/employee1.csv')
        response = self.client.post('/salary/file/upload/', {'file': file}, format='multipart', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def viewAllFiles(self, token):
        response = self.client.get('/salary/file/all/', format = 'json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def viewFileContents(self, token):
        response = self.client.get(f'/salary/file/1/', format="json", **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def approveFile(self, token):
        data = {
            'is_approved': True
        }
        response = self.client.patch('/salary/file/1/approve/', data, format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def transactionCount(self):
        count = Transaction.objects.all().count()
        self.assertGreaterEqual(count, 1)

    def test_all(self):
        response = self.client.post('/user/login/', {"username": "Noshin", "password": "drf@2024!"}, format="json")
        token_manager = response.data['access']
        response = self.client.post('/user/login/', {"username": "Mashiat", "password": "drf@2024!"}, format="json")
        token_admin = response.data['access']
        self.fileUpload(token_manager)
        self.viewAllFiles(token_manager)
        self.viewFileContents(token_manager)
        self.viewFileContents(token_admin)
        self.approveFile(token_admin)
        self.transactionCount()