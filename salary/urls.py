from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path("file/upload/", views.FileUpload.as_view()),
    path("beneficiary/all/", views.ViewBeneficiaryAll.as_view()),
    path("beneficiary/<int:id>/", views.ViewBeneficiary.as_view()),
    path("all/", views.SalaryViewAll.as_view()),
    path("<int:id>/", views.SalaryView.as_view()),
    path("beneficiary/<int:id>/approve/", views.ApproveBeneficiary.as_view()),
    path("transaction/all/", views.ViewTransactionAll.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)