from rest_framework.test import APITestCase
from rest_framework import status
from company.models import Company
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()

class UserTests(APITestCase):
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
        Company.objects.create(
            id = 1,
            organization =  "Square",
            founded_year =  "1958",
            description = "Square Pharmaceuticals Ltd. is a Bangladeshi multinational pharmaceutical company.",
            is_active = True,
            industry = "Pharmaceuticals",
            website = "https://www.squarepharma.com.bd/",
            email = "contact@squarepharma.com"
        )
        Group.objects.create(name="Admin")
        Group.objects.create(name="Manager")
        Group.objects.create(name="Superuser")
        
    def createsuperuser(self):
        data = {
            "username": "Super",
            "email": "super@saldis.com",
            "password": "drf@2024!",
            "password2": "drf@2024!"
        }
        response = self.client.post('/user/register_super/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def login(self, username, password):
        data = {
            "username": username,
            "password": password
        }
        response = self.client.post('/user/login/', data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        access = response.data['access']
        refresh = response.data['refresh']
        return access, refresh
    
    def tokenRefresh(self, refresh):
        data = {
            "refresh": refresh
        }
        response = self.client.post('/user/token_refresh/', data, format = "json")
        access = response.data['access']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        return access

    def registerAdmin(self, token):
        data = {
            "username": "Mashiat",
            "email": "mashiat@gmail.com",
            "password": "drf@2024!",
            "password2": "drf@2024!",
            "first_name": "Mashiat",
            "last_name": "Hasin",
            "gender": "Female",
            "mobile": "01575176218",
            "dob": "2001-06-19",
            "address": "Ramna",
            "group": "Admin",
        }
        response = self.client.post('/user/register/', data, format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        user = User.objects.get(id=response.data['id'])
        group = Group.objects.get(name='Admin') 
        user.groups.add(group)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def resetPassword(self, token, username, password, password2):
        data = {
            "username" : username,
            "password" : password,
            "password2": password2
        }
        response = self.client.patch('/user/reset_password/', data, format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def registerManager(self, token):
        user = User.objects.get(username="Mashiat")
        user.company_id = 1
        user.save()
        data = {
            "username": "Samiha",
            "email": "samiha@gmail.com",
            "password": "drf@2024!",
            "password2": "drf@2024!",
            "first_name": "Samiha",
            "last_name": "Rahman",
            "gender": "Female",
            "mobile": "01575176218",
            "dob": "2001-06-19",
            "address": "Ramna",
            "group": "Manager",
            "company_id": 1
        }
        response = self.client.post('/user/register/', data, format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return User.objects.get(email="samiha@gmail.com").id

    def viewProfile(self, token, id):
        response = self.client.get(f'/user/profile/{id}/', format='json', **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all(self):
        self.createsuperuser()
        access_super, refresh_super = self.login("Super", "drf@2024!")
        self.registerAdmin(access_super)
        access_admin, refresh_admin= self.login("Mashiat", "drf@2024!")
        access_admin = self.tokenRefresh(refresh_admin)
        self.resetPassword(access_admin, "Mashiat", "apiFun<3!", "apiFun<3!")
        access_admin, refresh_admin = self.login("Mashiat", "apiFun<3!")
        id = self.registerManager(access_admin)
        self.viewProfile(access_admin, id)
        self.login('Samiha', 'drf@2024!')