# relatorios/urls.py
from django.urls import path
from . import views
app_name = 'relatorios'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
]
