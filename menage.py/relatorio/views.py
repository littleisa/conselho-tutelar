# relatorios/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from ocorrencias.models import Ocorrencia
from core.models import TipoViolacao, User
from django.utils import timezone
from datetime import timedelta
@login_required
def dashboard(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    inicio_ano = hoje.replace(month=1, day=1)
    
    # Estatísticas gerais
    total_ocorrencias = Ocorrencia.objects.count()
    ocorrencias_mes = Ocorrencia.objects.filter(data_registro__date__gte=inicio_mes).count()
    ocorrencias_pendentes = Ocorrencia.objects.filter(status__in=['registrada', 'andamento']).count()
    ocorrencias_resolvidas = Ocorrencia.objects.filter(status='resolvida').count()
    
    # Ocorrências por status
    status_stats = Ocorrencia.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Ocorrências por tipo de violação
    tipo_stats = TipoViolacao.objects.annotate(
        count=Count('ocorrencia')
    ).order_by('-count')[:5]
    
    # Carga de trabalho por conselheira
    conselheiras_stats = User.objects.filter(
        perfil='conselheira',
        ativo=True
    ).annotate(
        casos_ativos=Count('ocorrencia', filter=Q(ocorrencia__status__in=['registrada', 'andamento'])),
        casos_resolvidos=Count('ocorrencia', filter=Q(ocorrencia__status='resolvida'))
    ).order_by('-casos_ativos')
    
    context = {
        'total_ocorrencias': total_ocorrencias,
        'ocorrencias_mes': ocorrencias_mes,
        'ocorrencias_pendentes': ocorrencias_pendentes,
        'ocorrencias_resolvidas': ocorrencias_resolvidas,
        'status_stats': status_stats,
        'tipo_stats': tipo_stats,
        'conselheiras_stats': conselheiras_stats,
    }
    
    return render(request, 'relatorios/dashboard.html', context)

@login_required
def estatisticas(request):
    # Relatório mais detalhado
    return render(request, 'relatorios/estatisticas.html')

