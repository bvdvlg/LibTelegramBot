from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('', views.process_telegram_request)
]