# ocorrencias/forms.py
from django import forms
from django.forms import ModelMultipleChoiceField, CheckboxSelectMultiple
from .models import Ocorrencia, TipoViolacao
from core.models import Bairro, User
class OcorrenciaForm(forms.ModelForm):
    tipos_violacao = ModelMultipleChoiceField(
        queryset=TipoViolacao.objects.filter(ativo=True),
        widget=CheckboxSelectMultiple,
        required=True,
        label="Tipos de Violação"
    )
    
    class Meta:
        model = Ocorrencia
        fields = [
            'data_ocorrencia', 'endereco', 'bairro', 'cep', 'complemento',
            'tipos_violacao', 'descricao', 'prioridade', 'nome_crianca',
            'idade_crianca', 'cpf_crianca', 'responsavel_legal',
            'nome_denunciante', 'telefone_denunciante', 'anonimo'
        ]
        widgets = {
            'data_ocorrencia': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'nome_crianca': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_crianca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bairro'].queryset = Bairro.objects.filter(ativo=True)
        self.fields['bairro'].empty_label = "Selecione o bairro"

class OcorrenciaUpdateForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = [
            'status', 'prioridade', 'descricao', 'conselheira_responsavel'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conselheira_responsavel'].queryset = User.objects.filter(
            perfil='conselheira', ativo=True
        )
        self.fields['conselheira_responsavel'].empty_label = "Selecione a conselheira"
