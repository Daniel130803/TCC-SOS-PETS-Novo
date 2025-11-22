from django.contrib import admin
from .models import (
    Usuario, Animal, Adocao, Denuncia, Donativo, Historia, Contato,
    AnimalParaAdocao, SolicitacaoAdocao, Notificacao,
    PetPerdido, PetPerdidoFoto, ReportePetEncontrado, ReportePetEncontradoFoto
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    Admin para perfis estendidos de usuários.
    
    Exibe informações complementares dos usuários cadastrados no sistema,
    como telefone, localização e data de cadastro.
    """
    list_display = ('user', 'telefone', 'cidade', 'data_criacao')
    search_fields = ('user__username', 'telefone')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar catálogo de animais da ONG.
    
    Permite administração completa dos animais cadastrados oficialmente
    pela ONG, incluindo filtros por tipo, status e busca por nome/raça.
    """
    list_display = ('nome', 'tipo', 'raca', 'status', 'data_criacao')
    list_filter = ('tipo', 'status')
    search_fields = ('nome', 'raca')

@admin.register(Adocao)
class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'usuario', 'status', 'data_solicitacao')
    list_filter = ('status', 'data_solicitacao')
    search_fields = ('animal__nome', 'usuario__user__username')

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar denúncias de maus-tratos.
    
    Permite moderação completa das denúncias com actions para:
    - Aprovar denúncias verificadas
    - Rejeitar denúncias inválidas
    - Marcar como em andamento durante investigação
    - Marcar como resolvidas após conclusão
    
    Inclui histórico automático de todas mudanças de status.
    """
    list_display = ('titulo', 'usuario', 'localizacao', 'status', 'moderador', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'localizacao')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    actions = ['aprovar_denuncias', 'rejeitar_denuncias', 'marcar_em_andamento', 'marcar_resolvidas']

    def aprovar_denuncias(self, request, queryset):
        """Action para aprovar múltiplas denúncias em lote."""
        # ATUALIZAÇÃO EM LOTE: Aprova todas as denúncias selecionadas
        # Registra quem aprovou (moderador) para auditoria
        # Mais eficiente que aprovar uma por uma manualmente
        updated = queryset.update(status='aprovada', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) aprovada(s).')
    aprovar_denuncias.short_description = 'Aprovar denúncias selecionadas'

    def rejeitar_denuncias(self, request, queryset):
        """Action para rejeitar múltiplas denúncias em lote."""
        # REJEIÇÃO EM LOTE: Marca denúncias como rejeitadas
        # Usado para denúncias falsas, duplicadas ou sem evidências
        updated = queryset.update(status='rejeitada', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) rejeitada(s).')
    rejeitar_denuncias.short_description = 'Rejeitar denúncias selecionadas'

    def marcar_em_andamento(self, request, queryset):
        """Action para marcar denúncias como em andamento."""
        # WORKFLOW: Status intermediário entre aprovada e resolvida
        # Indica que a ONG está investigando/tomando providências
        updated = queryset.update(status='em_andamento', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) marcada(s) como em andamento.')
    marcar_em_andamento.short_description = 'Marcar como em andamento'

    def marcar_resolvidas(self, request, queryset):
        """Action para marcar denúncias como resolvidas."""
        # FINALIZAÇÃO: Denúncia foi resolvida (animal resgatado, caso encerrado, etc)
        # Status final do workflow de moderação
        updated = queryset.update(status='resolvida', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) marcada(s) como resolvida(s).')
    marcar_resolvidas.short_description = 'Marcar como resolvidas'


@admin.register(PetPerdido)
class PetPerdidoAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar pets perdidos.
    
    Permite administração dos pets cadastrados como perdidos com:
    - Visualização de localização no mapa (lat/long)
    - Controle de visibilidade (ativar/desativar no mapa)
    - Marcação de pets encontrados
    - Filtros por espécie, porte, status, estado
    - Contador de visualizações
    
    Actions disponíveis:
    - Marcar como encontrado: Define status e data de encontro
    - Ativar/Desativar no mapa: Controla visibilidade pública
    """
    list_display = ('nome', 'especie', 'cidade', 'estado', 'status', 'ativo', 'data_perda', 'data_criacao')
    list_filter = ('especie', 'porte', 'status', 'ativo', 'estado', 'data_criacao')
    search_fields = ('nome', 'descricao', 'cidade', 'bairro', 'usuario__user__username')
    readonly_fields = ('visualizacoes', 'data_criacao', 'data_atualizacao', 'data_encontrado')
    actions = ['marcar_como_encontrado', 'ativar_pets', 'desativar_pets']
    
    def marcar_como_encontrado(self, request, queryset):
        """Action para marcar pets como encontrados."""
        from django.utils import timezone
        # FINALIZAÇÃO: Pet foi encontrado e reunido com o dono
        # Define data de encontro e remove do mapa (ativo=False)
        # Evita que continue aparecendo como perdido após reunião
        updated = queryset.update(status='encontrado', data_encontrado=timezone.now(), ativo=False)
        self.message_user(request, f'{updated} pet(s) marcado(s) como encontrado(s).')
    marcar_como_encontrado.short_description = 'Marcar como encontrado'
    
    def ativar_pets(self, request, queryset):
        """Action para ativar pets no mapa."""
        # VISIBILIDADE: Torna pets visíveis no mapa público
        # Usado quando pet ainda está perdido e precisa de divulgação
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} pet(s) ativado(s) no mapa.')
    ativar_pets.short_description = 'Ativar no mapa'
    
    def desativar_pets(self, request, queryset):
        """Action para desativar pets no mapa."""
        # OCULTAÇÃO: Remove pets do mapa sem deletar registro
        # Usado quando dono desiste de busca ou pet foi encontrado
        # Mantém registro no banco para histórico/estatísticas
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} pet(s) desativado(s) do mapa.')
    desativar_pets.short_description = 'Desativar do mapa'


@admin.register(ReportePetEncontrado)
class ReportePetEncontradoAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar reportes de pets encontrados.
    
    Interface para análise de pets encontrados e matching com pets perdidos:
    - Exibe possíveis matches automáticos (baseados em localização e características)
    - Permite confirmar match e notificar dono
    - Controle de status (pendente, em análise, aprovado, rejeitado)
    - Visualização de múltiplos matches simultâneos
    
    Actions disponíveis:
    - Marcar em análise: Inicia processo de verificação
    - Rejeitar reportes: Marca como falso positivo
    
    Note:
        Sistema de matching automático calcula distância e compara características
    """
    list_display = ('id', 'especie', 'cidade', 'estado', 'status', 'data_encontro', 'data_criacao', 'total_matches')
    list_filter = ('especie', 'porte', 'status', 'estado', 'data_criacao')
    search_fields = ('descricao', 'cidade', 'bairro', 'nome_pessoa', 'email_contato')
    readonly_fields = ('data_criacao', 'data_analise', 'data_atualizacao', 'possiveis_matches')
    filter_horizontal = ('possiveis_matches',)
    actions = ['marcar_em_analise', 'rejeitar_reportes']
    
    def total_matches(self, obj):
        return obj.possiveis_matches.count()
    total_matches.short_description = 'Possíveis Matches'
    
    def marcar_em_analise(self, request, queryset):
        updated = queryset.update(status='em_analise')
        self.message_user(request, f'{updated} reporte(s) marcado(s) como em análise.')
    marcar_em_analise.short_description = 'Marcar como em análise'
    
    def rejeitar_reportes(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='rejeitado', analisado_por=request.user, data_analise=timezone.now())
        self.message_user(request, f'{updated} reporte(s) rejeitado(s).')
    rejeitar_reportes.short_description = 'Rejeitar reportes'


@admin.register(Donativo)
class DonativoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'data_doacao')
    list_filter = ('data_doacao',)
    search_fields = ('usuario__user__username',)

@admin.register(Historia)
class HistoriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'animal', 'data_criacao')
    list_filter = ('data_criacao',)
    search_fields = ('titulo', 'conteudo')

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'assunto', 'lido', 'data_criacao')
    list_filter = ('lido', 'data_criacao')
    search_fields = ('nome', 'email', 'assunto')


@admin.register(AnimalParaAdocao)
class AnimalParaAdocaoAdmin(admin.ModelAdmin):
    """
    Admin para moderar animais cadastrados por usuários.
    
    Gerencia animais que usuários comuns cadastram para doação:
    - Aprovação antes de publicação (moderação)
    - Rejeição com motivo
    - Filtros por espécie, porte, status, localização
    - Visualização de dados do doador
    
    Actions disponíveis:
    - Aprovar pets: Libera para visualização pública
    - Rejeitar pets: Impede publicação
    
    Note:
        Endereço completo só é revelado após aprovação de solicitação
    """
    list_display = ('nome', 'especie', 'porte', 'usuario_doador', 'cidade', 'estado', 'status', 'data_cadastro')
    list_filter = ('especie', 'porte', 'status', 'estado', 'data_cadastro')
    search_fields = ('nome', 'descricao', 'cidade', 'usuario_doador__user__username')
    readonly_fields = ('data_cadastro', 'data_aprovacao')
    actions = ['aprovar_pets', 'rejeitar_pets']
    
    def aprovar_pets(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='aprovado', data_aprovacao=timezone.now())
        self.message_user(request, f'{updated} pet(s) aprovado(s) para adoção.')
    aprovar_pets.short_description = 'Aprovar pets selecionados'
    
    def rejeitar_pets(self, request, queryset):
        updated = queryset.update(status='rejeitado')
        self.message_user(request, f'{updated} pet(s) rejeitado(s).')
    rejeitar_pets.short_description = 'Rejeitar pets selecionados'


@admin.register(SolicitacaoAdocao)
class SolicitacaoAdocaoAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar solicitações de adoção.
    
    Permite moderação de pedidos de adoção de animais cadastrados por usuários:
    - Aprovação libera contatos de doador para interessado
    - Marca automaticamente animal como adotado ao aprovar
    - Rejeição com data registrada
    - Notificações automáticas para ambas partes
    
    Actions disponíveis:
    - Aprovar solicitações: Conecta doador e interessado
    - Rejeitar solicitações: Nega pedido de adoção
    
    Note:
        Ao aprovar, animal é automaticamente marcado como adotado
    """
    list_display = ('animal', 'usuario_interessado', 'status', 'data_solicitacao', 'data_aprovacao')
    list_filter = ('status', 'data_solicitacao')
    search_fields = ('animal__nome', 'usuario_interessado__user__username')
    readonly_fields = ('data_solicitacao', 'data_aprovacao')
    actions = ['aprovar_solicitacoes', 'rejeitar_solicitacoes']
    
    def aprovar_solicitacoes(self, request, queryset):
        from django.utils import timezone
        for solicitacao in queryset:
            solicitacao.status = 'aprovada'
            solicitacao.data_aprovacao = timezone.now()
            solicitacao.save()
            
            # Marca animal como adotado
            solicitacao.animal.status = 'adotado'
            solicitacao.animal.save()
        
        self.message_user(request, f'{queryset.count()} solicitação(ões) aprovada(s).')
    aprovar_solicitacoes.short_description = 'Aprovar solicitações selecionadas'
    
    def rejeitar_solicitacoes(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='rejeitada', data_aprovacao=timezone.now())
        self.message_user(request, f'{updated} solicitação(ões) rejeitada(s).')
    rejeitar_solicitacoes.short_description = 'Rejeitar solicitações selecionadas'


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'titulo', 'lida', 'data_criacao')
    list_filter = ('tipo', 'lida', 'data_criacao')
    search_fields = ('titulo', 'mensagem', 'usuario__user__username')
    readonly_fields = ('data_criacao',)
    actions = ['marcar_como_lidas']
    
    def marcar_como_lidas(self, request, queryset):
        updated = queryset.update(lida=True)
        self.message_user(request, f'{updated} notificação(ões) marcada(s) como lida(s).')
    marcar_como_lidas.short_description = 'Marcar como lidas'
