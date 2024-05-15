from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import SuperRegisterSerializer, RegisterSerializer, ProfileSerializer, PasswordSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsSuperuser, IsSameCompany, IsAdmin, IsVerified, IsSameUser
from .models import Profile as P
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator

class ResetPassword(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, format=None):
        user = request.user
        serializer = PasswordSerializer(data=request.data, context= {"request": request})
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        username = request.data.get('username')
        redirect_url = '/user/reset_password/'
        user = User.objects.get(username=username)
        if bool(user.is_verified) == False:
            return Response({'redirect_url': redirect_url, 'access': access_token, 'refresh': refresh_token}, status=status.HTTP_200_OK)
        return Response({'access': access_token, 'refresh': refresh_token}, status=status.HTTP_200_OK)
    
class RegisterSuper(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format = None):
        serializer = SuperRegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterMember(APIView):
    permission_classes = [IsAuthenticated & (IsSuperuser | (IsVerified & IsSameCompany & IsAdmin))]
    def post(self, request, format = None):
        serializer = RegisterSerializer(data = request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ViewProfile(APIView):
    permission_classes = [IsAuthenticated & (IsSameCompany | IsSuperuser) & IsVerified]
    authentication_classes = [JWTAuthentication]
    def get(self, request, id, format=None):
        p = P.objects.select_related('user').filter(user_id=id).first()
        try:
            data = {'id': p.user.id, 'username': p.user.username, 'email': p.user.email, 'company_id': p.user.company_id}
            serializer = ProfileSerializer(p, context={'id': id})
            data.update(serializer.data)
            if p is not None:
                return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'User does not exist.'}, status = status.HTTP_404_NOT_FOUND)
        
class UpdateUser(APIView):
    permission_classes = [IsAuthenticated & (IsSuperuser | (IsVerified & ((IsAdmin & IsSameCompany) | IsSameUser)))]
    authentication_classes = [JWTAuthentication]
    def patch(self, request, id, format=None):
        try:
            user = User.objects.get(id=id) or User.objects.get(id=request.user.id)
            serializer = RegisterSerializer(data=request.data, partial = True, context={"request": request})
            if serializer.is_valid():
                user = serializer.update(user, serializer.validated_data)
                p = P.objects.get(user_id=id)
                data = {'id': user.id, 'username': user.username, 'email': user.email, 'company_id': user.company_id}
                serializer = ProfileSerializer(p, context={'id': id})
                data.update(serializer.data)
                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except user.DoesNotExist:
            return Response({"detail":"User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class ViewUserAll(APIView):
    permission_classes = [IsAuthenticated & IsSuperuser]
    def get(self, request, format = None):
        page_no = self.request.query_params.get('page_no', 1)
        user = User.objects.all()
        page_size = self.request.query_params.get('page_size', 10)

        cache_key = f'user_all_{page_no}_{page_size}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        paginator = Paginator(user, page_size)
        serializer = RegisterSerializer(paginator.page(page_no), many=True)
        print(len(serializer.data))
        for row in serializer.data:
            try:
                p = P.objects.select_related('user').filter(user_id=row['id']).first()
                data = {'id': p.user.id, 'username': p.user.username, 'email': p.user.email, 'company_id': p.user.company_id}
                profile_serializer = ProfileSerializer(p, context={'id': row['id']})
                row.update(profile_serializer.data)
            except:
                row = row
        cache.set(cache_key, serializer.data, timeout= 60 * 60 * 24 * 1)
        if len(serializer.data)<1:
            return Response({"detail": "There are no users."}, status.HTTP_204_NO_CONTENT)
        return Response(serializer.data, status = status.HTTP_200_OK)
        