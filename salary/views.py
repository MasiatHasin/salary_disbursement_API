from .models import Transaction, Beneficiary, Salary
from user.models import CustomUser as User
from .serializers import TransactionSerializer, BeneficiarySerializer, SalarySerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.permissions import IsVerified
from .permissions import IsSameCompany
from user.permissions import IsManager, IsAdmin
from django.core.paginator import Paginator
from django.core.cache import cache

class FileUpload(APIView):
    permission_classes = [IsAuthenticated & IsManager & IsVerified] 
    def post(self, request, format=None):
        serializer = BeneficiarySerializer(data = request.data, context= {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ViewBeneficiaryAll(APIView):
    permission_classes = [IsAuthenticated & IsSameCompany & IsVerified]    
    def get(self, request, format = None):
        page_no = self.request.query_params.get('page_no', 1)
        files = Beneficiary.objects.filter(company_id = request.user.company_id)
        page_size = self.request.query_params.get('page_size', 10)

        cache_key = f'beneficiary_all_{page_no}_{page_size}_{request.user.company_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        paginator = Paginator(files, page_size)
        try:
            serializer = BeneficiarySerializer(paginator.page(page_no), many = True)
            cache.set(cache_key, serializer.data, 60 * 60 * 24 * 1)
            if len(serializer.data)<1:
                return Response({"detail": "Your organization has no associated beneficiaries."}, status.HTTP_204_NO_CONTENT)
            return Response(serializer.data, status.HTTP_200_OK)
        except:
            return Response({'detail':'This page does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class ViewBeneficiary(APIView):
    permission_classes = [IsAuthenticated & IsSameCompany & IsVerified]
    def get(self, request, id, format=None):
        try:
            beneficiary = Beneficiary.objects.get(id = id)
            serializer = BeneficiarySerializer(beneficiary, many=False)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Salary.DoesNotExist:
            return Response({"detail":"Record does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class ApproveBeneficiary(APIView):
    permission_classes = [IsAuthenticated & IsSameCompany & IsVerified & IsAdmin]
    def patch(self, request, id, format=None):
        beneficiary = Beneficiary.objects.get(id = id)
        serializer = BeneficiarySerializer(data=request.data, context= {"request": request})
        if serializer.is_valid():
                serializer.update(beneficiary, serializer.validated_data)
                serializer = BeneficiarySerializer(beneficiary, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SalaryViewAll(APIView):
    permission_classes = [IsAuthenticated & IsSameCompany & IsVerified]   
    def get(self, request, format = None):
        print("query params", request.query_params)
        page_no = self.request.query_params.get('page_no', 1)
        salary = Salary.objects.filter(company_id = request.user.company_id)
        page_size = self.request.query_params.get('page_size', 10)

        cache_key = f'salary_all_{page_no}_{page_size}_{request.user.company_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        paginator = Paginator(salary, page_size)
        try:
            serializer = SalarySerializer(paginator.page(page_no), many=True)
            cache.set(cache_key, serializer.data, 60 * 60 * 24 * 1)
            if len(salary)<1:
                return Response({"detail": "Your organization has no Employee data."}, status.HTTP_204_NO_CONTENT)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'detail':'This page does not exist.'}, status = status.HTTP_404_NOT_FOUND)
    
class SalaryView(APIView):
    permission_classes = [IsAuthenticated & IsSameCompany & IsVerified & IsAdmin]
    def get(self, request, id, format=None):
        try:
            employee = Salary.objects.get(id = id)
            serializer = SalarySerializer(employee, many=False)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Salary.DoesNotExist:
            return Response({"detail":"Record does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, id, format=None):
        try:
            employee = Salary.objects.get(id=id)
            serializer = SalarySerializer(data=request.data, partial = True)
            if serializer.is_valid():
                serializer.update(employee, serializer.validated_data)
                serializer = SalarySerializer(employee, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Salary.DoesNotExist:
            return Response({"detail":"Record does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id, format=None):
        try:
            Salary.objects.get(id=id).delete()
            return Response({"detail": "Successfully deleted record."}, status=status.HTTP_200_OK)
        except Salary.DoesNotExist:
            return Response({"detail": "Cannot delete non-existent record."}, status=status.HTTP_400_BAD_REQUEST)

class ViewTransactionAll(APIView):
    permission_classes = [IsSameCompany & IsAuthenticated & IsAdmin & IsVerified]
    def get(self, request, format=None):
        transaction = Transaction.objects.filter(company_id = request.user.company_id)
        serializer = TransactionSerializer(transaction, many=True)
        if len(serializer.data)<1:
            return Response({"detail": "Your organization has no associated transactions."}, status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status.HTTP_200_OK)