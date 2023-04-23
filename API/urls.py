from django.contrib import admin
from django.urls import path, include

from .views import RegistrationAPIView, LoginApiView, UserRetrieveUpdateAPIView, CompetenceAPIView

urlpatterns = [
    path("users/", RegistrationAPIView.as_view()),
    path("users/login", LoginApiView.as_view()),
    path("user", UserRetrieveUpdateAPIView.as_view()),
    path("competencies", CompetenceAPIView.as_view()),
]