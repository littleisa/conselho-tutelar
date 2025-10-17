# usuarios/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from core.models import Bairro, TipoViolacao

User = get_user_model()

@login_required
def lista_usuarios(request):
    usuarios = User.objects.all().order_by('first_name')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

@login_required
def lista_bairros(request):
    bairros = Bairro.objects.all().order_by('nome')
    return render(request, 'usuarios/bairros.html', {'bairros': bairros})

@login_required
def lista_tipos_violacao(request):
    tipos = TipoViolacao.objects.all().order_by('codigo')
    return render(request, 'usuarios/tipos_violacao.html', {'tipos': tipos})

# relatorios/urls.py
from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
]
