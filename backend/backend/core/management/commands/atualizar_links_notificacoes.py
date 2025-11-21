from django.core.management.base import BaseCommand
from core.models import Notificacao


class Command(BaseCommand):
    help = 'Atualiza links das notificações para apontar para /minhas-solicitacoes/'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando atualização de links de notificações...')
        
        # Atualiza notificações de adoção aprovada do interessado
        count1 = Notificacao.objects.filter(
            tipo='adocao_aprovada',
            link__contains='/perfil/?tab=adocoes'
        ).update(link='/minhas-solicitacoes/')
        
        # Atualiza notificações de adoção aprovada do doador
        count2 = Notificacao.objects.filter(
            tipo='adocao_aprovada',
            link__contains='/perfil/?tab=pets'
        ).update(link='/minhas-solicitacoes/')
        
        # Atualiza notificações de rejeição sem link
        count3 = Notificacao.objects.filter(
            tipo='adocao_rejeitada',
            link__isnull=True
        ).update(link='/minhas-solicitacoes/')
        
        # Atualiza notificações de rejeição com link antigo
        count4 = Notificacao.objects.filter(
            tipo='adocao_rejeitada',
            link__contains='/perfil'
        ).update(link='/minhas-solicitacoes/')
        
        total = count1 + count2 + count3 + count4
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {total} notificações atualizadas com sucesso!\n'
                f'   - Adoções aprovadas (interessado): {count1}\n'
                f'   - Adoções aprovadas (doador): {count2}\n'
                f'   - Rejeições sem link: {count3}\n'
                f'   - Rejeições com link antigo: {count4}'
            )
        )
