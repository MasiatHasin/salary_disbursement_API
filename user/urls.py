from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path("profile/<int:id>/", views.ViewProfile.as_view()),
    path("register_super/", views.RegisterSuper.as_view()),
    path("register/", views.RegisterMember.as_view()),
    path("login/", views.CustomTokenObtainPairView.as_view()),
    path("reset_password/", views.ResetPassword.as_view()),
    path('token_refresh/', TokenRefreshView.as_view()),
    path('profile/<int:id>/update/', views.UpdateUser.as_view()),
    path('profile/update/', views.UpdateUser.as_view()),
    path('profile/all/', views.ViewUserAll.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)