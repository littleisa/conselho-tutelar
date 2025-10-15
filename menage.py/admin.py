# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import User, Bairro, TipoViolacao
from ocorrencias.models import Ocorrencia, HistoricoOcorrencia, AnexoOcorrencia
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'perfil', 'ativo']
    list_filter = ['perfil', 'ativo', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('perfil', 'matricula', 'telefone', 'especialidades', 'ativo', 'carga_trabalho_atual')
        }),
    )

@admin.register(Bairro)
class BairroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade', 'estado', 'ativo']
    list_filter = ['ativo', 'cidade', 'estado']
    search_fields = ['nome']

@admin.register(TipoViolacao)
class TipoViolacaoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'codigo']

class HistoricoInline(admin.TabularInline):
    model = HistoricoOcorrencia
    extra = 0
    readonly_fields = ['data_alteracao']

class AnexoInline(admin.TabularInline):
    model = AnexoOcorrencia
    extra = 0
    readonly_fields = ['enviado_em']

@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ['protocolo', 'nome_crianca', 'bairro', 'status', 'prioridade', 'conselheira_responsavel', 'data_registro']
    list_filter = ['status', 'prioridade', 'bairro', 'conselheira_responsavel']
    search_fields = ['protocolo', 'nome_crianca', 'endereco']
    readonly_fields = ['protocolo', 'data_registro']
    inlines = [HistoricoInline, AnexoInline]
    
    fieldsets = (
        ('Identificação', {
            'fields': ('protocolo', 'data_ocorrencia', 'data_registro')
        }),
        ('Localização', {
            'fields': ('endereco', 'bairro', 'cep', 'complemento')
        }),
        ('Dados da Criança/Adolescente', {
            'fields': ('nome_crianca', 'idade_crianca', 'cpf_crianca', 'responsavel_legal')
        }),
        ('Ocorrência', {
            'fields': ('tipos_violacao', 'descricao', 'prioridade', 'status')
        }),
        ('Denunciante', {
            'fields': ('anonimo', 'nome_denunciante', 'telefone_denunciante')
        }),
        ('Atribuição', {
            'fields': ('conselheira_responsavel', 'registrado_por')
        }),
    )