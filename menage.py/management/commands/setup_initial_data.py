# management/commands/setup_initial_data.py
from django.core.management.base import BaseCommand
from core.models import TipoViolacao, Bairro
from django.contrib.auth import get_user_model

User = get_user_model()
class Command(BaseCommand):
    help = 'Configura dados iniciais do sistema'
    
    def handle(self, *args, **options):
        # Criar tipos de violação baseados no ECA
        tipos_violacao = [
            {'codigo': 'NEG', 'nome': 'Negligência', 'descricao': 'Omissão dos responsáveis em prover necessidades básicas'},
            {'codigo': 'ABN', 'nome': 'Abandono', 'descricao': 'Abandono material ou afetivo da criança/adolescente'},
            {'codigo': 'VFS', 'nome': 'Violência Física', 'descricao': 'Agressão física contra criança/adolescente'},
            {'codigo': 'VPS', 'nome': 'Violência Psicológica', 'descricao': 'Agressão verbal, humilhação, ameaças'},
            {'codigo': 'VSX', 'nome': 'Violência Sexual', 'descricao': 'Abuso sexual contra criança/adolescente'},
            {'codigo': 'ETI', 'nome': 'Exploração do Trabalho Infantil', 'descricao': 'Trabalho infantil irregular ou perigoso'},
            {'codigo': 'DRG', 'nome': 'Uso/Tráfico de Substâncias', 'descricao': 'Envolvimento com drogas lícitas ou ilícitas'},
            {'codigo': 'ESC', 'nome': 'Evasão Escolar', 'descricao': 'Abandono ou irregularidade escolar'},
            {'codigo': 'OUT', 'nome': 'Outros', 'descricao': 'Outras violações não especificadas acima'},
        ]
        
        for tipo_data in tipos_violacao:
            tipo, created = TipoViolacao.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults={
                    'nome': tipo_data['nome'],
                    'descricao': tipo_data['descricao']
                }
            )
            if created:
                self.stdout.write(f'Tipo de violação criado: {tipo.nome}')
        
        # Criar alguns bairros de Campo Grande, MS como exemplo
        bairros_exemplo = [
            {'nome': 'Centro', 'ceps': '79002-000,79003-000,79004-000'},
            {'nome': 'Amambaí', 'ceps': '79005-000,79006-000'},
            {'nome': 'São Francisco', 'ceps': '79010-000,79011-000'},
            {'nome': 'Vila Alba', 'ceps': '79016-000'},
            {'nome': 'Coophavila II', 'ceps': '79040-000,79041-000'},
            {'nome': 'Nova Lima', 'ceps': '79050-000,79051-000'},
            {'nome': 'Jardim dos Estados', 'ceps': '79020-000,79021-000'},
            {'nome': 'Vila Planalto', 'ceps': '79030-000'},
        ]
        
        for bairro_data in bairros_exemplo:
            bairro, created = Bairro.objects.get_or_create(
                nome=bairro_data['nome'],
                defaults={'ceps': bairro_data['ceps']}
            )
            if created:
                self.stdout.write(f'Bairro criado: {bairro.nome}')
        
        # Criar usuário administrador padrão
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@conselhotutelar.gov.br',
                password='admin123',
                perfil='admin',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write('Usuário administrador criado: admin/admin123')
        
        self.stdout.write(self.style.SUCCESS('Dados iniciais configurados com sucesso!'))
