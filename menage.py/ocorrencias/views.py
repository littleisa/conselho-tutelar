# ocorrencias/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Ocorrencia, HistoricoOcorrencia, TipoViolacao
from .forms import OcorrenciaForm, OcorrenciaUpdateForm
from .utils import distribuir_ocorrencia, buscar_ocorrencias_similares
from core.models import Bairro, User
import json
@login_required
def lista_ocorrencias(request):
    ocorrencias = Ocorrencia.objects.all().select_related('bairro', 'conselheira_responsavel')
    
    # Filtros
    status = request.GET.get('status')
    bairro_id = request.GET.get('bairro')
    prioridade = request.GET.get('prioridade')
    conselheira_id = request.GET.get('conselheira')
    
    if status:
        ocorrencias = ocorrencias.filter(status=status)
    if bairro_id:
        ocorrencias = ocorrencias.filter(bairro_id=bairro_id)
    if prioridade:
        ocorrencias = ocorrencias.filter(prioridade=prioridade)
    if conselheira_id:
        ocorrencias = ocorrencias.filter(conselheira_responsavel_id=conselheira_id)
    
    # Busca
    q = request.GET.get('q')
    if q:
        ocorrencias = ocorrencias.filter(
            Q(protocolo__icontains=q) | 
            Q(nome_crianca__icontains=q) |
            Q(endereco__icontains=q)
        )
    
    # Paginação
    paginator = Paginator(ocorrencias, 20)
    page = request.GET.get('page')
    ocorrencias = paginator.get_page(page)
    
    context = {
        'ocorrencias': ocorrencias,
        'bairros': Bairro.objects.filter(ativo=True),
        'conselheiras': User.objects.filter(perfil='conselheira', ativo=True),
        'status_choices': Ocorrencia.STATUS_CHOICES,
        'prioridade_choices': Ocorrencia.PRIORIDADE_CHOICES,
    }
    
    return render(request, 'ocorrencias/lista.html', context)

@login_required
def nova_ocorrencia(request):
    if request.method == 'POST':
        form = OcorrenciaForm(request.POST)
        if form.is_valid():
            # Verificar duplicidades
            endereco = form.cleaned_data['endereco']
            bairro = form.cleaned_data['bairro']
            nome_crianca = form.cleaned_data['nome_crianca']
            
            similares = buscar_ocorrencias_similares(endereco, bairro, nome_crianca)
            
            if similares and not request.POST.get('confirmar_duplicata'):
                context = {
                    'form': form,
                    'ocorrencias_similares': similares,
                    'confirmar_duplicata': True,
                }
                messages.warning(request, 'Encontradas ocorrências similares. Verifique antes de confirmar.')
                return render(request, 'ocorrencias/nova.html', context)
            
            # Salvar ocorrência
            ocorrencia = form.save(commit=False)
            ocorrencia.registrado_por = request.user
            
            # Verificar se bairro está na área de abrangência
            if not ocorrencia.bairro.ativo:
                messages.error(request, 'Este bairro não está na área de abrangência do conselho.')
                return render(request, 'ocorrencias/nova.html', {'form': form})
            
            ocorrencia.save()
            form.save_m2m()  # Salvar ManyToMany (tipos_violacao)
            
            # Distribuir automaticamente
            conselheira = distribuir_ocorrencia(ocorrencia)
            if conselheira:
                ocorrencia.conselheira_responsavel = conselheira
                ocorrencia.save()
                messages.success(request, f'Ocorrência {ocorrencia.protocolo} registrada e distribuída para {conselheira.get_full_name()}')
            else:
                messages.warning(request, f'Ocorrência {ocorrencia.protocolo} registrada, mas não foi possível distribuir automaticamente.')
            
            return redirect('ocorrencias:detalhe', pk=ocorrencia.pk)
    else:
        form = OcorrenciaForm()
    
    return render(request, 'ocorrencias/nova.html', {'form': form})

@login_required
def detalhe_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    historico = ocorrencia.historico.all()[:10]  # Últimos 10 registros
    
    context = {
        'ocorrencia': ocorrencia,
        'historico': historico,
    }
    
    return render(request, 'ocorrencias/detalhe.html', context)

@login_required
def editar_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    
    # Verificar permissão
    if request.user.perfil not in ['admin', 'coordenador'] and ocorrencia.conselheira_responsavel != request.user:
        messages.error(request, 'Você não tem permissão para editar esta ocorrência.')
        return redirect('ocorrencias:detalhe', pk=pk)
    
    if request.method == 'POST':
        form = OcorrenciaUpdateForm(request.POST, instance=ocorrencia)
        if form.is_valid():
            # Registrar alterações no histórico
            for field in form.changed_data:
                valor_anterior = getattr(ocorrencia, field, '')
                valor_novo = form.cleaned_data[field]
                
                HistoricoOcorrencia.objects.create(
                    ocorrencia=ocorrencia,
                    usuario=request.user,
                    campo_alterado=field,
                    valor_anterior=str(valor_anterior),
                    valor_novo=str(valor_novo)
                )
            
            form.save()
            messages.success(request, 'Ocorrência atualizada com sucesso.')
            return redirect('ocorrencias:detalhe', pk=pk)
    else:
        form = OcorrenciaUpdateForm(instance=ocorrencia)
    
    return render(request, 'ocorrencias/editar.html', {'form': form, 'ocorrencia': ocorrencia})

@login_required
def verificar_duplicatas(request):
    """API endpoint para verificar duplicatas via AJAX"""
    if request.method == 'POST':
        data = json.loads(request.body)
        endereco = data.get('endereco', '')
        bairro_id = data.get('bairro_id')
        nome_crianca = data.get('nome_crianca', '')
        
        if bairro_id:
            try:
                bairro = Bairro.objects.get(id=bairro_id)
                similares = buscar_ocorrencias_similares(endereco, bairro, nome_crianca)
                
                resultado = []
                for ocorrencia in similares:
                    resultado.append({
                        'protocolo': ocorrencia.protocolo,
                        'nome_crianca': ocorrencia.nome_crianca,
                        'endereco': ocorrencia.endereco,
                        'data_registro': ocorrencia.data_registro.strftime('%d/%m/%Y'),
                        'status': ocorrencia.get_status_display(),
                        'url': reverse('ocorrencias:detalhe', args=[ocorrencia.pk])
                    })
                
                return JsonResponse({'similares': resultado})
            except Bairro.DoesNotExist:
                pass
    
    return JsonResponse({'similares': []})

