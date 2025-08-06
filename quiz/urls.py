# quiz/urls.py
from django.urls import path, re_path
from . import views

urlpatterns = [
    # API Yolları
    path('api/login/', views.api_login, name='api_login'),
    path('api/create_session/', views.create_game_session, name='api_create_session'),
    path('api/generate_questions/', views.api_generate_questions, name='api_generate_questions'),
    
    # Frontend'i sunan ana yol (her zaman en sonda olmalı)
    re_path(r'^.*$', views.index, name='frontend'),
]