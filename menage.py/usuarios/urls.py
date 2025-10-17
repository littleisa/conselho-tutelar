# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.lista_usuarios, name='lista'),
    path('perfil/', views.perfil, name='perfil'),
    path('bairros/', views.lista_bairros, name='bairros'),
    path('tipos-violacao/', views.lista_tipos_violacao, name='tipos_violacao'),
]
