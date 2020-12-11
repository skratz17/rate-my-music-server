"""server URL Configuration"""
from django.urls import path
from rmmapi.views import login_user, register_user

urlpatterns = [
    path('register', register_user),
    path('login', login_user)
]
