# ocorrencias/urls.py
from django.urls import path
from . import views

app_name = 'ocorrencias'

urlpatterns = [
    path('', views.lista_ocorrencias, name='lista'),
    path('nova/', views.nova_ocorrencia, name='nova'),
    path('<uuid:pk>/', views.detalhe_ocorrencia, name='detalhe'),
    path('<uuid:pk>/editar/', views.editar_ocorrencia, name='editar'),
    path('api/verificar-duplicatas/', views.verificar_duplicatas, name='verificar_duplicatas'),
]

# urls.py (projeto principal)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ocorrencias.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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