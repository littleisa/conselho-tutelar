# ocorrencias/models.py
from django.db import models
from django.contrib.auth import get_user_model
from core.models import Bairro, TipoViolacao
from django.core.validators import RegexValidator
import uuid
from datetime import datetime
User = get_user_model()

class Ocorrencia(models.Model):
    STATUS_CHOICES = [
        ('registrada', 'Registrada'),
        ('andamento', 'Em Andamento'),
        ('aguardando', 'Aguardando Documentos'),
        ('encaminhada', 'Encaminhada'),
        ('resolvida', 'Resolvida'),
        ('arquivada', 'Arquivada'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('emergencial', 'Emergencial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.CharField(max_length=20, unique=True, editable=False)
    data_ocorrencia = models.DateTimeField()
    data_registro = models.DateTimeField(auto_now_add=True)
    
    # Localização
    endereco = models.CharField(max_length=255)
    bairro = models.ForeignKey(Bairro, on_delete=models.PROTECT)
    cep = models.CharField(max_length=9, validators=[RegexValidator(r'^\d{5}-?\d{3}$')])
    complemento = models.CharField(max_length=100, blank=True)
    
    # Tipo e descrição
    tipos_violacao = models.ManyToManyField(TipoViolacao)
    descricao = models.TextField()
    prioridade = models.CharField(max_length=15, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='registrada')
    
    # Dados da criança/adolescente
    nome_crianca = models.CharField(max_length=200)
    idade_crianca = models.IntegerField()
    cpf_crianca = models.CharField(max_length=14, blank=True, validators=[RegexValidator(r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$')])
    responsavel_legal = models.CharField(max_length=200, blank=True)
    
    # Denunciante
    nome_denunciante = models.CharField(max_length=200, blank=True)
    telefone_denunciante = models.CharField(max_length=15, blank=True)
    anonimo = models.BooleanField(default=False)
    
    # Atribuição
    conselheira_responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'perfil': 'conselheira'})
    data_atribuicao = models.DateTimeField(null=True, blank=True)
    
    # Controle
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ocorrencias_registradas')
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.protocolo:
            ano = datetime.now().year
            count = Ocorrencia.objects.filter(data_registro__year=ano).count() + 1
            self.protocolo = f"CT{ano}{count:06d}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-data_registro']
    
    def __str__(self):
        return f"{self.protocolo} - {self.nome_crianca}"

class HistoricoOcorrencia(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    campo_alterado = models.CharField(max_length=50)
    valor_anterior = models.TextField()
    valor_novo = models.TextField()
    observacoes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-data_alteracao']

class AnexoOcorrencia(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='anexos/')
    nome_arquivo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255, blank=True)
    enviado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    enviado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome_arquivo
