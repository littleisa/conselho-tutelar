# ocorrencias/utils.py
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .models import Ocorrencia
from core.models import Bairro
import random
User = get_user_model()

def distribuir_ocorrencia(ocorrencia):
    """
    Distribui uma ocorrência para uma conselheira baseado em:
    - Balanceamento de carga
    - Especialidade vs tipo de violação
    - Rotatividade
    """
    conselheiras = User.objects.filter(
        perfil='conselheira',
        ativo=True
    ).annotate(
        casos_ativos=Count('ocorrencia', filter=Q(ocorrencia__status__in=['registrada', 'andamento']))
    ).order_by('casos_ativos')
    
    if not conselheiras.exists():
        return None
    
    # Selecionar entre as conselheiras com menor carga de trabalho
    min_casos = conselheiras.first().casos_ativos
    candidatas = conselheiras.filter(casos_ativos=min_casos)
    
    # Se há empate, usar rotatividade (random choice por enquanto)
    # Em implementação futura, pode-se usar um sistema de pontuação mais sofisticado
    conselheira_escolhida = random.choice(list(candidatas))
    
    return conselheira_escolhida

def buscar_ocorrencias_similares(endereco, bairro, nome_crianca, limite=5):
    """
    Busca ocorrências similares para evitar duplicatas
    """
    similaridade_queries = []
    
    # Mesmo endereço
    if endereco:
        similaridade_queries.append(Q(endereco__icontains=endereco))
    
    # Mesmo bairro e nome da criança
    if bairro and nome_crianca:
        similaridade_queries.append(
            Q(bairro=bairro) & Q(nome_crianca__icontains=nome_crianca)
        )
    
    if not similaridade_queries:
        return Ocorrencia.objects.none()
    
    # Combinar queries com OR
    combined_query = similaridade_queries[0]
    for query in similaridade_queries[1:]:
        combined_query |= query
    
    return Ocorrencia.objects.filter(
        combined_query
    ).exclude(
        status='arquivada'
    ).order_by('-data_registro')[:limite]