from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path("register/", views.Register.as_view()),
    path("all/", views.ViewAllCompanies.as_view()),
    path("<int:id>/", views.ViewCompany.as_view()),
    path("<int:id>/update/", views.UpdateCompany.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)