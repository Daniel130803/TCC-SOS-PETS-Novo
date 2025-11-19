from django.contrib import admin
from .models import Usuario, Animal, Adocao, Denuncia, AnimalPerdido, Donativo, Historia, Contato

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone', 'cidade', 'data_criacao')
    search_fields = ('user__username', 'telefone')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
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
    list_display = ('titulo', 'usuario', 'localizacao', 'status', 'moderador', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'localizacao')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    actions = ['aprovar_denuncias', 'rejeitar_denuncias', 'marcar_em_andamento', 'marcar_resolvidas']

    def aprovar_denuncias(self, request, queryset):
        updated = queryset.update(status='aprovada', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) aprovada(s).')
    aprovar_denuncias.short_description = 'Aprovar denúncias selecionadas'

    def rejeitar_denuncias(self, request, queryset):
        updated = queryset.update(status='rejeitada', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) rejeitada(s).')
    rejeitar_denuncias.short_description = 'Rejeitar denúncias selecionadas'

    def marcar_em_andamento(self, request, queryset):
        updated = queryset.update(status='em_andamento', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) marcada(s) como em andamento.')
    marcar_em_andamento.short_description = 'Marcar como em andamento'

    def marcar_resolvidas(self, request, queryset):
        updated = queryset.update(status='resolvida', moderador=request.user)
        self.message_user(request, f'{updated} denúncia(s) marcada(s) como resolvida(s).')
    marcar_resolvidas.short_description = 'Marcar como resolvidas'

@admin.register(AnimalPerdido)
class AnimalPerdidoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'localizacao', 'status', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('nome', 'localizacao')

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
