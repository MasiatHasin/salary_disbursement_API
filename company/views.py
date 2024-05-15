from .models import Company
from .serializers import CompanySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse
from user.permissions import IsSuperuser, IsVerified, IsAdmin
from .permissions import IsSameCompany
from django.core.paginator import Paginator
from django.core.cache import cache
from user.models import CustomUser as User
from user.serializers import RegisterSerializer
from django.db import IntegrityError
    
class Register(APIView):
    permission_classes = [IsSuperuser]
    def post(self, request, format = None):
        try:
            serializer = CompanySerializer(data = request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"detail": "Organization with same name exists"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ViewAllCompanies(APIView):
    permission_classes = [IsAuthenticated & IsSuperuser]
    def get(self, request, format = None):
        page_no = self.request.query_params.get('page_no', 1)
        company = Company.objects.all().exclude(id=0)
        page_size = self.request.query_params.get('page_size', 10)

        cache_key = f'company_all_{page_no}_{page_size}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        paginator = Paginator(company, page_size)
        try:
            serializer = CompanySerializer(paginator.page(page_no), many=True)
            for row in serializer.data:
                admin = User.objects.filter(groups__name='Admin', company_id = row['id']).values_list('id', flat=True)
                manager = User.objects.filter(groups__name='Manager', company_id = row['id']).values_list('id', flat=True)
                row.update({"admin":admin})
                row.update({"manager":manager})
            cache.set(cache_key, serializer.data, 60 * 60 * 24 * 1)
            if len(serializer.data)<1:
                return Response({"detail": "Your organization has no Company data."}, status.HTTP_204_NO_CONTENT)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'detail':'This page does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class ViewCompany(APIView):
    permission_classes = [IsAuthenticated & ((IsVerified & IsSameCompany) | IsSuperuser)]
    def get(self, request, id, format=None):
        try:
            company = Company.objects.get(id = id)
            serializer = CompanySerializer(company)
            admin = User.objects.filter(groups__name='Admin', company_id = id).values_list('id', flat=True)
            manager = User.objects.filter(groups__name='Manager', company_id = id).values_list('id', flat=True)
            data = serializer.data
            data.update({"admin":admin})
            data.update({"manager":manager})
            if len(serializer.data)>0:
                return Response(data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except company.DoesNotExist:
            return Response({"detail":"Company does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
class UpdateCompany(APIView):
    permission_classes = [IsAuthenticated & (IsAdmin & IsVerified & IsSameCompany) | IsSuperuser]
    def patch(self, request, id, format=None):
        try:
            company = Company.objects.get(id=id)
            serializer = CompanySerializer(data = request.data, partial = True, context={"request":request})
            if serializer.is_valid():
                serializer.update(company, serializer.validated_data)
                serializer = CompanySerializer(company, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except company.DoesNotExist:
            return Response({"detail":"Company does not exist."}, status=status.HTTP_404_NOT_FOUND)
            
