from typing import Any, Dict, List, Optional, Union
from django.shortcuts import render
from django.utils import timezone
from django.db.models import QuerySet
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from math import radians, sin, cos, sqrt, atan2
from .throttling import (
    RegistroRateThrottle, LoginRateThrottle, ContatoRateThrottle,
    DenunciaRateThrottle, AdocaoRateThrottle, PetPerdidoRateThrottle,
    UploadRateThrottle, ListRateThrottle, DetailRateThrottle
)
from .models import (
    Animal, Adocao, Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico,
    AnimalParaAdocao, SolicitacaoAdocao, Notificacao, Usuario, Contato,
    PetPerdido, PetPerdidoFoto, ReportePetEncontrado, ReportePetEncontradoFoto
)
from .serializers import (
    AnimalSerializer, AdocaoSerializer, DenunciaSerializer,
    RegisterSerializer, UserMeSerializer, UserUpdateSerializer,
    AnimalParaAdocaoSerializer, SolicitacaoAdocaoSerializer, NotificacaoSerializer,
    ContatoSerializer, PetPerdidoSerializer, ReportePetEncontradoSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User

# Create your views here.

class AnimalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD do catálogo de animais da ONG.
    
    Endpoints disponíveis:
    - GET /api/animais/ - Lista animais disponíveis (por padrão)
    - POST /api/animais/ - Cria novo animal (staff only)
    - GET /api/animais/{id}/ - Detalhes de um animal
    - PUT/PATCH /api/animais/{id}/ - Atualiza animal (staff only)
    - DELETE /api/animais/{id}/ - Remove animal (staff only)
    
    Permissions:
        - List/Retrieve: Público (AllowAny)
        - Create/Update/Delete: Requer autenticação (IsAuthenticatedOrReadOnly)
    
    Filters:
        status: Filtrar por status (disponivel, adotado, indisponivel)
        tipo: Filtrar por tipo (cachorro, gato, cao como alias)
        porte: Filtrar por porte (pequeno, medio, grande)
        sexo: Filtrar por sexo (macho, femea)
        estado: Filtrar por estado (UF)
        cidade: Filtrar por cidade
        nome/q: Buscar por nome (case-insensitive, partial match)
    
    Methods:
        get_queryset: Aplica filtros e exibe apenas disponíveis por padrão
    
    Example:
        GET /api/animais/?tipo=cachorro&porte=medio&cidade=São%20Paulo
        GET /api/animais/?nome=rex
        GET /api/animais/?status=adotado
    """
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet:
        """Aplica filtros e retorna queryset de animais."""
        qs = Animal.objects.all()
        # Por padrão, só exibe disponíveis na listagem
        status_param = self.request.query_params.get('status')
        if self.action == 'list' and not status_param:
            qs = qs.filter(status='disponivel')
        elif status_param:
            qs = qs.filter(status__iexact=status_param)

        tipo = self.request.query_params.get('tipo')
        if tipo:
            # aceita "cao" como apelido para "cachorro"
            if tipo.lower() == 'cao':
                tipo = 'cachorro'
            qs = qs.filter(tipo__iexact=tipo)

        porte = self.request.query_params.get('porte')
        if porte:
            qs = qs.filter(porte__iexact=porte)

        sexo = self.request.query_params.get('sexo')
        if sexo:
            qs = qs.filter(sexo__iexact=sexo)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado__iexact=estado)

        cidade = self.request.query_params.get('cidade')
        if cidade:
            qs = qs.filter(cidade__iexact=cidade)

        nome = self.request.query_params.get('nome') or self.request.query_params.get('q')
        if nome:
            qs = qs.filter(nome__icontains=nome)

        return qs

class AdocaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitações de adoção do catálogo da ONG.
    
    Endpoints disponíveis:
    - GET /api/adocoes/ - Lista todas solicitações do usuário
    - POST /api/adocoes/ - Cria nova solicitação
    - GET /api/adocoes/{id}/ - Detalhes de uma solicitação
    - PUT/PATCH /api/adocoes/{id}/ - Atualiza solicitação
    - DELETE /api/adocoes/{id}/ - Cancela solicitação
    
    Permissions:
        - Todas operações: Requer autenticação (IsAuthenticated)
    """
    queryset = Adocao.objects.all()
    serializer_class = AdocaoSerializer
    permission_classes = [permissions.IsAuthenticated]

from rest_framework.generics import CreateAPIView

class RegisterView(CreateAPIView):
    """
    View para registro de novos usuários.
    
    Endpoint:
        POST /api/register/
    
    Permissions:
        AllowAny (público)
    
    Request Body:
        username (str): Nome de usuário único
        email (str): E-mail (valida duplicatas)
        password (str): Senha (será criptografada)
        first_name (str): Nome completo
        telefone (str): Telefone (opcional)
    
    Response:
        201: Usuário criado com sucesso
        400: Erros de validação
    
    Example:
        POST /api/register/
        {
            "username": "joao",
            "email": "joao@email.com",
            "password": "senha123",
            "first_name": "João Silva",
            "telefone": "11999999999"
        }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistroRateThrottle]

class MeView(APIView):
    """
    View para gerenciar dados do usuário autenticado.
    
    Endpoints:
        GET /api/me/ - Retorna dados do usuário
        PATCH /api/me/ - Atualiza dados do usuário
    
    Permissions:
        IsAuthenticated (requer login)
    
    GET Response:
        id: ID do usuário
        username: Nome de usuário
        email: E-mail
        first_name: Nome completo
        is_staff: Se é admin
        telefone: Telefone do perfil
    
    PATCH Request Body (todos opcionais):
        first_name: Nome completo
        email: E-mail (valida duplicatas)
        telefone: Telefone
    
    Methods:
        get: Retorna dados atuais do usuário
        patch: Atualiza first_name, email e telefone
    
    Example:
        GET /api/me/
        PATCH /api/me/ {"first_name": "João Silva", "telefone": "11988888888"}
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Retorna dados do usuário autenticado."""
        user: User = request.user
        # garante perfil Usuario
        if not hasattr(user, 'usuario'):
            Usuario.objects.get_or_create(user=user)
        data = UserMeSerializer(user).data
        return Response(data)

    def patch(self, request: Request) -> Response:
        """Atualiza dados do usuário autenticado."""
        user: User = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Retorna dados atualizados
            updated_data = UserMeSerializer(user).data
            return Response(updated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DenunciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para denúncias de maus-tratos e abandono.
    
    Endpoints disponíveis:
    - GET /api/denuncias/ - Lista denúncias (filtros disponíveis)
    - POST /api/denuncias/ - Cria nova denúncia
    - GET /api/denuncias/{id}/ - Detalhes de uma denúncia
    - PUT/PATCH /api/denuncias/{id}/ - Atualiza denúncia
    - DELETE /api/denuncias/{id}/ - Remove denúncia
    
    Permissions:
        - List/Retrieve: Público (AllowAny)
        - Create: Requer autenticação (IsAuthenticated)
        - Update/Delete: Requer ser dono ou staff (IsOwnerOrReadOnly)
    
    Throttling:
        - Create: 10 denúncias por hora (previne spam de denúncias falsas)
        - List/Retrieve: Throttling padrão
    
    Filters:
        status: Filtrar por status (pendente, aprovada, em_andamento, resolvida, rejeitada)
        categoria: Filtrar por categoria (maus_tratos, abandono, acumulacao, animal_perdido, animal_ferido, outros)
        usuario: Filtrar por ID do usuário
    
    Note:
        Cria automaticamente entrada no histórico ao criar denúncia
    """
    queryset = Denuncia.objects.all()
    serializer_class = DenunciaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [DenunciaRateThrottle]

    def get_queryset(self) -> QuerySet:
        """Filtra denúncias baseado no tipo de usuário."""
        qs = super().get_queryset()
        
        # Controle de visibilidade:
        # - Admins (is_staff): Acesso total a todas as denúncias para moderação
        # - Usuários autenticados: Veem apenas suas próprias denúncias para privacidade
        # - Não autenticados: Podem ver todas (read-only) conforme IsAuthenticatedOrReadOnly
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            if hasattr(self.request.user, 'usuario'):
                qs = qs.filter(usuario=self.request.user.usuario)
        return qs
    
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Cria denúncia e processa múltiplas mídias anexadas."""
        # PASSO 1: Cria a denúncia principal com dados básicos (texto, localização, etc)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        denuncia = serializer.save()
        
        # PASSO 2: Processa múltiplas imagens adicionais enviadas via FormData
        # getlist() captura todos os arquivos com o mesmo nome de campo
        imagens = request.FILES.getlist('imagens_adicionais')
        for imagem in imagens:
            # Cria registro separado para cada imagem (relacionamento 1:N)
            DenunciaImagem.objects.create(denuncia=denuncia, imagem=imagem)
        
        # PASSO 3: Processa múltiplos vídeos adicionais (mesmo processo das imagens)
        videos = request.FILES.getlist('videos_adicionais')
        for video in videos:
            # Armazena vídeos em registros separados para facilitar moderação
            DenunciaVideo.objects.create(denuncia=denuncia, video=video)
        
        # PASSO 4: Retorna a denúncia completa com todas as mídias anexadas
        # Serializer busca automaticamente imagens/vídeos via related_name
        output_serializer = self.get_serializer(denuncia)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request: Request, pk: Optional[int] = None) -> Response:
        """Endpoint para admin aprovar uma denúncia"""
        denuncia = self.get_object()
        
        # Captura status anterior para auditoria (histórico)
        status_anterior = denuncia.status
        
        # Atualiza status e registra quem moderou
        denuncia.status = 'aprovada'
        denuncia.moderador = request.user
        observacoes = request.data.get('observacoes', '')
        denuncia.observacoes_moderador = observacoes
        denuncia.save()
        
        # SISTEMA DE AUDITORIA: Registra mudança de status no histórico
        # Permite rastrear todas as ações de moderação (quem, quando, porquê)
        # Importante para transparência e accountability da ONG
        DenunciaHistorico.objects.create(
            denuncia=denuncia,
            tipo='status',
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo='aprovada',
            comentario=observacoes if observacoes else 'Denúncia aprovada'
        )
        
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request: Request, pk: Optional[int] = None) -> Response:
        """Endpoint para admin rejeitar uma denúncia"""
        denuncia = self.get_object()
        status_anterior = denuncia.status
        denuncia.status = 'rejeitada'
        denuncia.moderador = request.user
        observacoes = request.data.get('observacoes', 'Denúncia rejeitada.')
        denuncia.observacoes_moderador = observacoes
        denuncia.save()
        
        # Registra no histórico
        DenunciaHistorico.objects.create(
            denuncia=denuncia,
            tipo='status',
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo='rejeitada',
            comentario=observacoes
        )
        
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def em_andamento(self, request, pk=None):
        """Endpoint para admin marcar denúncia como em andamento"""
        denuncia = self.get_object()
        status_anterior = denuncia.status
        denuncia.status = 'em_andamento'
        denuncia.moderador = request.user
        observacoes = request.data.get('observacoes', 'Denúncia em análise.')
        denuncia.observacoes_moderador = observacoes
        denuncia.save()
        
        # Registra no histórico
        DenunciaHistorico.objects.create(
            denuncia=denuncia,
            tipo='status',
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo='em_andamento',
            comentario=observacoes
        )
        
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def resolver(self, request, pk=None):
        """Endpoint para admin marcar denúncia como resolvida"""
        denuncia = self.get_object()
        status_anterior = denuncia.status
        denuncia.status = 'resolvida'
        denuncia.moderador = request.user
        observacoes = request.data.get('observacoes', 'Denúncia resolvida.')
        denuncia.observacoes_moderador = observacoes
        denuncia.save()
        
        # Registra no histórico
        DenunciaHistorico.objects.create(
            denuncia=denuncia,
            tipo='status',
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo='resolvida',
            comentario=observacoes
        )
        
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def adicionar_comentario(self, request, pk=None):
        """Endpoint para admin adicionar comentário interno"""
        denuncia = self.get_object()
        comentario = request.data.get('comentario', '')
        
        if not comentario:
            return Response({'error': 'Comentário não pode ser vazio'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Registra no histórico
        DenunciaHistorico.objects.create(
            denuncia=denuncia,
            tipo='comentario',
            usuario=request.user,
            comentario=comentario
        )
        
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)


class AnimalParaAdocaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para animais cadastrados por usuários para adoção.
    
    Endpoints disponíveis:
    - GET /api/animais-para-adocao/ - Lista animais aprovados (público)
    - POST /api/animais-para-adocao/ - Cadastra novo animal (autenticado)
    - GET /api/animais-para-adocao/{id}/ - Detalhes de um animal
    - PUT/PATCH /api/animais-para-adocao/{id}/ - Atualiza animal (dono ou staff)
    - DELETE /api/animais-para-adocao/{id}/ - Remove animal (dono ou staff)
    
    Permissions:
        - List/Retrieve: Público para aprovados, autenticado para próprios
        - Create: Requer autenticação
        - Update/Delete: Dono ou staff
    
    Filters:
        especie: Filtrar por espécie (cachorro, gato, outro)
        porte: Filtrar por porte (pequeno, medio, grande)
        sexo: Filtrar por sexo (M, F, N)
        estado: Filtrar por estado (UF)
        cidade: Filtrar por cidade
        status: Filtrar por status (pendente, aprovado, rejeitado, adotado)
        meus: Listar apenas animais do usuário logado (meus=true)
    
    Custom Actions:
        @action aprovar: Aprova animal para publicação (staff only)
        @action rejeitar: Rejeita animal com motivo (staff only)
    
    Note:
        Endereço completo é oculto até aprovação da solicitação de adoção
    """
    queryset = AnimalParaAdocao.objects.all()
    serializer_class = AnimalParaAdocaoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtra animais para adoção baseado em permissões e status."""
        qs = super().get_queryset()
        
        # CONTROLE DE VISIBILIDADE MULTINÍVEL:
        # 1. Admins (is_staff): Acesso total para moderação
        # 2. Doadores: Veem seus próprios pets (qualquer status) + todos aprovados
        # 3. Usuários autenticados: Apenas pets aprovados (catálogo público)
        # 4. Não autenticados: Apenas pets aprovados (catálogo público)
        
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                # ADMIN: Vê tudo (pendente, aprovado, rejeitado, adotado)
                # Necessário para moderar cadastros de usuários
                pass
            elif hasattr(self.request.user, 'usuario'):
                # DOADOR: Vê pets aprovados + seus próprios (qualquer status)
                # Permite acompanhar status de moderação dos próprios pets
                usuario = self.request.user.usuario
                qs = qs.filter(
                    status='aprovado'
                ) | qs.filter(usuario_doador=usuario)
        else:
            # ANÔNIMO: Apenas pets aprovados
            # Catálogo público de adoção
            qs = qs.filter(status='aprovado')
        
        # Filtros de busca
        especie = self.request.query_params.get('especie')
        if especie:
            qs = qs.filter(especie__iexact=especie)
        
        porte = self.request.query_params.get('porte')
        if porte:
            qs = qs.filter(porte__iexact=porte)
        
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado__iexact=estado)
        
        cidade = self.request.query_params.get('cidade')
        if cidade:
            qs = qs.filter(cidade__icontains=cidade)
        
        nome = self.request.query_params.get('nome')
        if nome:
            qs = qs.filter(nome__icontains=nome)
        
        return qs.distinct()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request, pk=None):
        """Admin aprova pet para aparecer na galeria"""
        animal = self.get_object()
        animal.status = 'aprovado'
        animal.data_aprovacao = timezone.now()
        animal.save()
        
        # Notifica o doador
        Notificacao.objects.create(
            usuario=animal.usuario_doador,
            tipo='animal_aprovado',
            titulo='Pet aprovado!',
            mensagem=f'Seu pet "{animal.nome}" foi aprovado e agora está visível na galeria de adoção.',
            link=f'/adocao/?pet={animal.id}'
        )
        
        serializer = self.get_serializer(animal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request, pk=None):
        """Admin rejeita pet cadastrado"""
        animal = self.get_object()
        animal.status = 'rejeitado'
        animal.save()
        
        # Notifica o doador
        motivo = request.data.get('motivo', 'Não especificado')
        Notificacao.objects.create(
            usuario=animal.usuario_doador,
            tipo='animal_rejeitado',
            titulo='Pet rejeitado',
            mensagem=f'Seu pet "{animal.nome}" foi rejeitado. Motivo: {motivo}',
        )
        
        serializer = self.get_serializer(animal)
        return Response(serializer.data)


class SolicitacaoAdocaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitações de adoção de animais cadastrados por usuários.
    
    Endpoints disponíveis:
    - GET /api/solicitacoes-adocao/ - Lista solicitações do usuário
    - POST /api/solicitacoes-adocao/ - Cria nova solicitação
    - GET /api/solicitacoes-adocao/{id}/ - Detalhes
    - PUT/PATCH /api/solicitacoes-adocao/{id}/ - Atualiza (dono ou staff)
    - DELETE /api/solicitacoes-adocao/{id}/ - Cancela (dono)
    
    Permissions:
        - List: Apenas solicitações do usuário autenticado
        - Create: Requer autenticação
        - Update/Delete: Interessado ou staff
    
    Throttling:
        - Create: 5 solicitações por hora (previne spam de solicitações falsas)
        - List/Retrieve: Throttling padrão
    
    Filters:
        animal: Filtrar por ID do animal
        status: Filtrar por status (pendente, aprovada, rejeitada, cancelada)
    
    Custom Actions:
        @action aprovar: Aprova solicitação e cria notificações (doador ou staff)
        @action rejeitar: Rejeita com motivo (doador ou staff)
        @action cancelar: Cancela solicitação (interessado)
    
    Note:
        Cria notificações automáticas para doador e interessado
        Previne duplicatas com unique_together (animal, usuario_interessado)
    """
    queryset = SolicitacaoAdocao.objects.all()
    serializer_class = SolicitacaoAdocaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AdocaoRateThrottle]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Admins veem todas
        if self.request.user.is_staff:
            return qs
        
        # Usuários veem apenas suas próprias solicitações (como interessado ou doador)
        if hasattr(self.request.user, 'usuario'):
            usuario = self.request.user.usuario
            qs = qs.filter(
                usuario_interessado=usuario
            ) | qs.filter(animal__usuario_doador=usuario)
            return qs.distinct()
        
        return qs.none()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request: Request, pk: Optional[int] = None) -> Response:
        """Admin aprova solicitação de adoção"""
        from django.utils import timezone
        
        solicitacao = self.get_object()
        
        # PASSO 1: Aprova a solicitação e registra data
        solicitacao.status = 'aprovada'
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        # PASSO 2: Marca o animal como adotado (muda status, remove de listagens)
        # Animal adotado não aparece mais em buscas de adoção
        animal = solicitacao.animal
        animal.status = 'adotado'
        animal.save()
        
        # PASSO 3: Coleta dados de contato do doador (atual responsável pelo pet)
        # Usa cascata: animal.telefone > usuario.telefone > 'Não informado'
        # Essencial para interessado fazer contato e combinar entrega
        doador = animal.usuario_doador
        telefone_doador = animal.telefone or doador.telefone or 'Não informado'
        email_doador = animal.email or doador.user.email or 'Não informado'
        endereco_doador = animal.endereco_completo or 'Não informado'
        
        # PASSO 4: Coleta dados de contato do interessado (futuro dono)
        # Necessário para doador fazer contato e validar condições de adoção
        interessado = solicitacao.usuario_interessado
        telefone_interessado = interessado.telefone or 'Não informado'
        email_interessado = interessado.user.email or 'Não informado'
        
        # PASSO 5: Notifica o interessado com dados completos do doador
        # Notificação inclui telefone, email e endereço para facilitar coordenação
        Notificacao.objects.create(
            usuario=interessado,
            tipo='adocao_aprovada',
            titulo='Adoção aprovada!',
            mensagem=f'Sua solicitação para adotar "{animal.nome}" foi aprovada! Entre em contato com o doador.',
            link=f'/minhas-solicitacoes/',
            contato_telefone=telefone_doador,
            contato_email=email_doador,
            contato_endereco=endereco_doador
        )
        solicitacao.notificado_interessado = True
        
        # PASSO 6: Notifica o doador com dados do interessado
        # Permite doador validar e combinar detalhes da entrega do pet
        Notificacao.objects.create(
            usuario=doador,
            tipo='adocao_aprovada',
            titulo='Solicitação de adoção aprovada!',
            mensagem=f'A solicitação de adoção de "{animal.nome}" foi aprovada. Entre em contato com o interessado.',
            link=f'/minhas-solicitacoes/',
            contato_telefone=telefone_interessado,
            contato_email=email_interessado
        )
        solicitacao.notificado_doador = True
        solicitacao.save()
        
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request: Request, pk: Optional[int] = None) -> Response:
        """Admin rejeita solicitação de adoção"""
        from django.utils import timezone
        
        solicitacao = self.get_object()
        solicitacao.status = 'rejeitada'
        solicitacao.data_aprovacao = timezone.now()
        motivo = request.data.get('motivo', 'Não especificado')
        solicitacao.save()
        
        # Notifica o interessado
        Notificacao.objects.create(
            usuario=solicitacao.usuario_interessado,
            tipo='adocao_rejeitada',
            titulo='Solicitação rejeitada',
            mensagem=f'Sua solicitação para adotar "{solicitacao.animal.nome}" foi rejeitada. Motivo: {motivo}',
            link=f'/minhas-solicitacoes/'
        )
        
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request: Request, pk: Optional[int] = None) -> Response:
        """Usuário cancela sua própria solicitação"""
        from django.utils import timezone
        
        solicitacao = self.get_object()
        
        # Verifica se o usuário é o interessado
        if not hasattr(request.user, 'usuario') or solicitacao.usuario_interessado != request.user.usuario:
            return Response(
                {'detail': 'Você não tem permissão para cancelar esta solicitação.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Só pode cancelar se estiver pendente
        if solicitacao.status != 'pendente':
            return Response(
                {'detail': 'Apenas solicitações pendentes podem ser canceladas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitacao.status = 'cancelada'
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)


class NotificacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para notificações do usuário.
    
    Endpoints disponíveis:
    - GET /api/notificacoes/ - Lista notificações do usuário (ordenadas por data)
    - GET /api/notificacoes/{id}/ - Detalhes de uma notificação
    - PATCH /api/notificacoes/{id}/ - Marca como lida
    - DELETE /api/notificacoes/{id}/ - Remove notificação
    - POST /api/notificacoes/marcar-todas-lidas/ - Marca todas como lidas (action)
    
    Permissions:
        - Todas operações: Requer autenticação (IsAuthenticated)
        - Usuário só acessa suas próprias notificações
    
    Filters:
        lida: Filtrar por status de leitura (true/false)
        tipo: Filtrar por tipo de notificação
    
    Custom Actions:
        @action marcar_todas_lidas: Marca todas notificações do usuário como lidas
    
    Note:
        GET automáticamente filtra apenas notificações do usuário logado
    """
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Usuários veem apenas suas próprias notificações
        if hasattr(self.request.user, 'usuario'):
            qs = Notificacao.objects.filter(usuario=self.request.user.usuario).order_by('-data_criacao')
            
            # Filtro por lida/não lida
            lida = self.request.query_params.get('lida', None)
            if lida is not None:
                if lida.lower() == 'true':
                    qs = qs.filter(lida=True)
                elif lida.lower() == 'false':
                    qs = qs.filter(lida=False)
            
            return qs
        return Notificacao.objects.none()
    
    @action(detail=True, methods=['post'])
    def marcar_lida(self, request, pk=None):
        """Marca uma notificação como lida"""
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        
        serializer = self.get_serializer(notificacao)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def marcar_todas_lidas(self, request):
        """Marca todas as notificações do usuário como lidas"""
        if hasattr(request.user, 'usuario'):
            Notificacao.objects.filter(
                usuario=request.user.usuario,
                lida=False
            ).update(lida=True)
            
            return Response({'detail': 'Todas as notificações foram marcadas como lidas.'})
        
        return Response({'detail': 'Usuário sem perfil.'}, status=status.HTTP_400_BAD_REQUEST)


# Novos ViewSets para "Minhas Solicitações"
class MinhasSolicitacoesEnviadasView(APIView):
    """
    View para listar solicitações de adoção enviadas pelo usuário.
    
    Endpoint:
        GET /api/minhas-solicitacoes-enviadas/
    
    Permissions:
        IsAuthenticated (requer login)
    
    Response:
        Lista de solicitações feitas pelo usuário autenticado para adotar animais
    
    Filters:
        status: Filtrar por status (pendente, aprovada, rejeitada, cancelada)
    
    Example:
        GET /api/minhas-solicitacoes-enviadas/?status=pendente
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Lista todas as solicitações de adoção enviadas pelo usuário."""
        # VALIDAÇÃO: Retorna lista vazia se usuário não tem perfil Usuario
        if not hasattr(request.user, 'usuario'):
            return Response([], status=status.HTTP_200_OK)
        
        usuario = request.user.usuario
        
        # BUSCA OTIMIZADA: select_related evita N+1 queries
        # Carrega animal e doador em uma única query SQL (JOIN)
        # Ordenação por data (mais recentes primeiro)
        solicitacoes = SolicitacaoAdocao.objects.filter(
            usuario_interessado=usuario
        ).select_related('animal', 'animal__usuario_doador').order_by('-data_solicitacao')
        
        data = []
        for sol in solicitacoes:
            animal = sol.animal
            doador = animal.usuario_doador
            
            # MONTA ITEM BASE: Dados do animal e status da solicitação
            # Dados de contato do doador são ocultados por padrão (privacidade)
            # MONTA ITEM BASE: Dados do animal e status da solicitação
            # Dados de contato do doador são ocultados por padrão (privacidade)
            item = {
                'id': sol.id,
                'animal_id': animal.id,
                'animal_nome': animal.nome,
                'animal_especie': animal.get_especie_display(),
                'animal_porte': animal.get_porte_display(),
                'animal_sexo': animal.get_sexo_display() if hasattr(animal, 'sexo') else None,
                'animal_cor': animal.cor if hasattr(animal, 'cor') else None,
                'animal_idade': animal.idade if hasattr(animal, 'idade') else None,
                'animal_imagem': request.build_absolute_uri(animal.imagem_principal.url) if animal.imagem_principal else None,
                'status': sol.status,
                'mensagem': sol.mensagem,
                'data_solicitacao': sol.data_solicitacao,
                'doador_nome': doador.user.get_full_name() or doador.user.username,
                'doador_telefone': None,
                'doador_email': None,
                'doador_endereco': None,
                'motivo_rejeicao': None
            }
            
            # REVELAÇÃO CONDICIONAL: Dados de contato só aparecem após aprovação
            # Privacidade: doador não quer contato de interessados não aprovados
            # Permite interessado coordenar entrega do pet após aprovação
            if sol.status == 'aprovada':
                item['doador_telefone'] = animal.telefone or doador.telefone or None
                item['doador_email'] = animal.email or doador.user.email or None
                item['doador_endereco'] = animal.endereco_completo or None
            
            data.append(item)
        
        return Response({'results': data}, status=status.HTTP_200_OK)


class SolicitacoesRecebidasView(APIView):
    """
    View para listar solicitações de adoção recebidas nos animais do usuário.
    
    Endpoint:
        GET /api/solicitacoes-recebidas/
    
    Permissions:
        IsAuthenticated (requer login)
    
    Response:
        Lista de solicitações feitas por outros usuários para adotar
        os animais cadastrados pelo usuário autenticado
    
    Filters:
        animal: Filtrar por ID do animal
        status: Filtrar por status (pendente, aprovada, rejeitada, cancelada)
    
    Example:
        GET /api/solicitacoes-recebidas/?status=pendente
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Lista solicitações de adoção recebidas nos animais do doador."""
        # VALIDAÇÃO: Retorna lista vazia se usuário não tem perfil
        if not hasattr(request.user, 'usuario'):
            return Response([], status=status.HTTP_200_OK)
        
        usuario = request.user.usuario
        
        # BUSCA INVERSA: animal__usuario_doador filtra pelos pets DO USUÁRIO
        # Retorna pessoas que QUEREM adotar os pets cadastrados
        # select_related otimiza query com JOINs
        solicitacoes = SolicitacaoAdocao.objects.filter(
            animal__usuario_doador=usuario
        ).select_related('animal', 'usuario_interessado').order_by('-data_solicitacao')
        
        data = []
        for sol in solicitacoes:
            animal = sol.animal
            interessado = sol.usuario_interessado
            
            item = {
                'id': sol.id,
                'animal_id': animal.id,
                'animal_nome': animal.nome,
                'animal_especie': animal.get_especie_display(),
                'animal_porte': animal.get_porte_display(),
                'animal_sexo': animal.get_sexo_display() if hasattr(animal, 'sexo') else None,
                'animal_cor': animal.cor if hasattr(animal, 'cor') else None,
                'animal_idade': animal.idade if hasattr(animal, 'idade') else None,
                'animal_imagem': request.build_absolute_uri(animal.imagem_principal.url) if animal.imagem_principal else None,
                'status': sol.status,
                'mensagem': sol.mensagem,
                'data_solicitacao': sol.data_solicitacao,
                'interessado_nome': interessado.user.get_full_name() or interessado.user.username,
                'interessado_telefone': None,
                'interessado_email': None
            }
            
            # REVELAÇÃO CONDICIONAL: Dados do interessado só após aprovação
            # Permite doador entrar em contato para combinar entrega
            # Privacidade: interessado não quer ser contatado antes da aprovação
            if sol.status == 'aprovada':
                item['interessado_telefone'] = interessado.telefone or None
                item['interessado_email'] = interessado.user.email or None
            
            data.append(item)
        
        return Response({'results': data}, status=status.HTTP_200_OK)


class MeusPetsCadastradosView(APIView):
    """
    View para listar animais cadastrados pelo usuário para adoção.
    
    Endpoint:
        GET /api/meus-pets-cadastrados/
    
    Permissions:
        IsAuthenticated (requer login)
    
    Response:
        Lista de todos os animais cadastrados pelo usuário autenticado,
        independente do status (pendente, aprovado, rejeitado, adotado)
        Inclui contador de solicitações totais e pendentes por animal
    
    Filters:
        status: Filtrar por status de aprovação
    
    Example:
        GET /api/meus-pets-cadastrados/?status=aprovado
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """Lista todos os pets cadastrados pelo usuário com contadores."""
        # VALIDAÇÃO: Retorna lista vazia se usuário não tem perfil
        if not hasattr(request.user, 'usuario'):
            return Response([], status=status.HTTP_200_OK)
        
        usuario = request.user.usuario
        
        # BUSCA COMPLETA: Todos os pets do usuário (qualquer status)
        # Ordenação por data de cadastro (mais recentes primeiro)
        pets = AnimalParaAdocao.objects.filter(
            usuario_doador=usuario
        ).order_by('-data_cadastro')
        
        data = []
        for pet in pets:
            # ESTATÍSTICAS: Conta solicitações para cada pet
            # total_solicitacoes: Todas (pendente, aprovada, rejeitada, cancelada)
            # solicitacoes_pendentes: Apenas aguardando decisão
            # Útil para doador priorizar análise de pets com mais interesse
            total_solicitacoes = SolicitacaoAdocao.objects.filter(animal=pet).count()
            solicitacoes_pendentes = SolicitacaoAdocao.objects.filter(animal=pet, status='pendente').count()
            
            item = {
                'id': pet.id,
                'nome': pet.nome,
                'especie_display': pet.get_especie_display(),
                'porte_display': pet.get_porte_display() if pet.porte else 'Não informado',
                'sexo': pet.sexo if hasattr(pet, 'sexo') else None,
                'sexo_display': pet.get_sexo_display() if hasattr(pet, 'sexo') else None,
                'cor': pet.cor if hasattr(pet, 'cor') else None,
                'idade': pet.idade if hasattr(pet, 'idade') else None,
                'descricao': pet.descricao,
                'cidade': pet.cidade,
                'estado': pet.estado,
                'status': pet.status,
                'imagem_principal_url': request.build_absolute_uri(pet.imagem_principal.url) if pet.imagem_principal else None,
                'data_cadastro': pet.data_cadastro,
                'total_solicitacoes': total_solicitacoes,
                'solicitacoes_pendentes': solicitacoes_pendentes
            }
            
            data.append(item)
        
        return Response({'results': data}, status=status.HTTP_200_OK)


class ContatoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para mensagens de contato.
    
    Endpoints disponíveis:
    - GET /api/contatos/ - Lista contatos (staff: todos, user: próprios)
    - POST /api/contatos/ - Envia mensagem de contato (público)
    - GET /api/contatos/{id}/ - Detalhes de uma mensagem
    - PATCH /api/contatos/{id}/ - Atualiza status/resposta (staff)
    - DELETE /api/contatos/{id}/ - Remove mensagem (staff)
    - POST /api/contatos/{id}/responder/ - Responde mensagem (staff, action)
    
    Permissions:
        - Create: Público (AllowAny)
        - List: Autenticado (staff vê todos, user vê próprios)
        - Retrieve/Update/Delete: Staff apenas
    
    Throttling:
        - Create: 5 mensagens por hora (previne spam via formulário)
        - List/Retrieve: Throttling padrão
    
    Filters:
        status: Filtrar por status (pendente, em_atendimento, respondido, resolvido)
        lido: Filtrar por leitura (true/false)
    
    Custom Actions:
        @action responder: Responde mensagem e notifica usuário (staff only)
    
    Note:
        Usuários anônimos podem enviar mensagens
        Usuários autenticados têm dados pré-preenchidos
    """
    queryset = Contato.objects.all()
    serializer_class = ContatoSerializer
    permission_classes = [permissions.AllowAny]  # Permite contato anônimo
    throttle_classes = [ContatoRateThrottle]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Admins veem todos os contatos
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return qs
        
        # Usuários autenticados veem apenas seus próprios contatos
        if self.request.user.is_authenticated and hasattr(self.request.user, 'usuario'):
            return qs.filter(usuario=self.request.user.usuario)
        
        # Usuários não autenticados não veem nada no list
        return qs.none()
    
    def create(self, request, *args, **kwargs):
        """Criar novo contato e notificar administradores"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contato = serializer.save()
        
        # Notifica todos os administradores
        admin_users = User.objects.filter(is_staff=True)
        for admin in admin_users:
            if hasattr(admin, 'usuario'):
                Notificacao.objects.create(
                    usuario=admin.usuario,
                    tipo='contato_recebido',
                    titulo='Novo contato recebido',
                    mensagem=f'Nova mensagem de {contato.nome}: {contato.assunto}',
                    link='/admin-panel/?tab=contatos'
                )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def responder(self, request, pk=None):
        """Admin responde a um contato"""
        contato = self.get_object()
        resposta = request.data.get('resposta', '')
        
        if not resposta:
            return Response(
                {'error': 'Resposta não pode ser vazia'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Atualiza o contato
        contato.resposta = resposta
        contato.data_resposta = timezone.now()
        contato.respondido_por = request.user
        contato.status = 'respondido'
        contato.save()
        
        # Notifica o usuário que enviou o contato (se estiver registrado)
        if contato.usuario:
            Notificacao.objects.create(
                usuario=contato.usuario,
                tipo='contato_respondido',
                titulo='Resposta do administrador',
                mensagem=f'Sua mensagem "{contato.assunto}" foi respondida!',
                link='/minhas-solicitacoes/?tab=contatos'
            )
            contato.usuario_notificado = True
            contato.save()
        
        serializer = self.get_serializer(contato)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def marcar_lido(self, request, pk=None):
        """Admin marca contato como lido"""
        contato = self.get_object()
        contato.lido = True
        contato.data_leitura = timezone.now()
        if contato.status == 'pendente':
            contato.status = 'em_atendimento'
        contato.save()
        
        serializer = self.get_serializer(contato)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def resolver(self, request, pk=None):
        """Admin marca contato como resolvido"""
        contato = self.get_object()
        contato.status = 'resolvido'
        contato.save()
        
        serializer = self.get_serializer(contato)
        return Response(serializer.data)


# ===== PETS PERDIDOS =====
class PetPerdidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para pets perdidos com geolocalização.
    
    Endpoints disponíveis:
    - GET /api/pets-perdidos/ - Lista pets perdidos ativos no mapa (público)
    - POST /api/pets-perdidos/ - Cadastra pet perdido (autenticado)
    - GET /api/pets-perdidos/{id}/ - Detalhes de um pet (incrementa visualizações)
    - PUT/PATCH /api/pets-perdidos/{id}/ - Atualiza pet (dono)
    - DELETE /api/pets-perdidos/{id}/ - Remove pet (dono)
    - POST /api/pets-perdidos/{id}/marcar-encontrado/ - Marca como encontrado (action)
    - GET /api/pets-perdidos/cidades-disponiveis/ - Lista cidades com pets perdidos (action)
    
    Permissions:
        - List/Retrieve: Público (AllowAny)
        - Create: Requer autenticação
        - Update/Delete: Dono apenas
    
    Throttling:
        - Create: 10 cadastros por hora (previne spam de cadastros falsos)
        - List/Retrieve: Throttling padrão
    
    Filters:
        cidade: Filtrar por cidade
        estado: Filtrar por estado (UF)
        especie: Filtrar por espécie (cachorro, gato, outro)
        porte: Filtrar por porte (pequeno, medio, grande)
        status: Filtrar por status (perdido, encontrado, cancelado)
        ativo: Filtrar por visibilidade no mapa (true/false)
        oferece_recompensa: Filtrar pets com recompensa (true)
    
    Custom Actions:
        @action marcar_encontrado: Marca pet como encontrado e desativa no mapa
        @action cidades_disponiveis: Retorna lista de cidades com pets perdidos ativos
    
    Note:
        GET retrieve incrementa contador de visualizações automaticamente
        Lista ordenada por data_criacao descendente (mais recentes primeiro)
    """
    queryset = PetPerdido.objects.all()
    serializer_class = PetPerdidoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [PetPerdidoRateThrottle]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Admins veem todos
        if self.request.user.is_authenticated and self.request.user.is_staff:
            pass  # Vê tudo
        # Usuários autenticados veem ativos + seus próprios
        elif self.request.user.is_authenticated and hasattr(self.request.user, 'usuario'):
            qs = qs.filter(ativo=True, status='perdido') | qs.filter(usuario=self.request.user.usuario)
            qs = qs.distinct()
        else:
            # Não autenticados veem apenas ativos e perdidos
            qs = qs.filter(ativo=True, status='perdido')
        
        # Filtros de busca
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado__iexact=estado)
        
        cidade = self.request.query_params.get('cidade')
        if cidade:
            qs = qs.filter(cidade__icontains=cidade)
        
        especie = self.request.query_params.get('especie')
        if especie:
            qs = qs.filter(especie__iexact=especie)
        
        porte = self.request.query_params.get('porte')
        if porte:
            qs = qs.filter(porte__iexact=porte)
        
        cor = self.request.query_params.get('cor')
        if cor:
            qs = qs.filter(cor__icontains=cor)
        
        return qs.order_by('-data_criacao')
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementa visualizações ao visualizar detalhes"""
        instance = self.get_object()
        instance.visualizacoes += 1
        instance.save(update_fields=['visualizacoes'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Criar novo pet perdido e processar fotos adicionais"""
        # PASSO 1: Cria registro do pet perdido com dados básicos
        # (nome, espécie, porte, cor, local, coordenadas GPS)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pet_perdido = serializer.save()
        
        # PASSO 2: Processa múltiplas fotos adicionais do pet
        # getlist() captura todos os arquivos com o mesmo nome de campo
        # Múltiplas fotos aumentam chances de identificação visual
        fotos = request.FILES.getlist('fotos_adicionais')
        for foto in fotos:
            PetPerdidoFoto.objects.create(pet_perdido=pet_perdido, imagem=foto)
        
        # PASSO 3: Notifica administradores sobre novo cadastro
        # Admins podem monitorar pets perdidos e auxiliar em buscas
        # Sistema de divulgação e apoio da ONG
        admin_users = User.objects.filter(is_staff=True)
        for admin in admin_users:
            if hasattr(admin, 'usuario'):
                Notificacao.objects.create(
                    usuario=admin.usuario,
                    tipo='denuncia',  # Reutilizando tipo existente
                    titulo='Novo pet perdido cadastrado',
                    mensagem=f'Pet {pet_perdido.nome} perdido em {pet_perdido.cidade}/{pet_perdido.estado}',
                    link='/admin-panel/?tab=pets-perdidos'
                )
        
        output_serializer = self.get_serializer(pet_perdido)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def marcar_encontrado(self, request: Request, pk: Optional[int] = None) -> Response:
        """Marca pet como encontrado (apenas o dono pode fazer isso)"""
        pet_perdido = self.get_object()
        
        # Verifica se é o dono
        if not hasattr(request.user, 'usuario') or pet_perdido.usuario != request.user.usuario:
            if not request.user.is_staff:
                return Response(
                    {'detail': 'Apenas o dono pode marcar o pet como encontrado.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        pet_perdido.status = 'encontrado'
        pet_perdido.data_encontrado = timezone.now()
        pet_perdido.ativo = False
        pet_perdido.save()
        
        serializer = self.get_serializer(pet_perdido)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reativar(self, request: Request, pk: Optional[int] = None) -> Response:
        """Reativa pet perdido (caso tenha sido desativado por engano)"""
        pet_perdido = self.get_object()
        
        # Verifica se é o dono
        if not hasattr(request.user, 'usuario') or pet_perdido.usuario != request.user.usuario:
            if not request.user.is_staff:
                return Response(
                    {'detail': 'Apenas o dono pode reativar o pet.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        pet_perdido.status = 'perdido'
        pet_perdido.ativo = True
        pet_perdido.data_encontrado = None
        pet_perdido.save()
        
        serializer = self.get_serializer(pet_perdido)
        return Response(serializer.data)


class ReportePetEncontradoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para reportes de pets encontrados com matching automático.
    
    Endpoints disponíveis:
    - GET /api/reportes-pet-encontrado/ - Lista reportes
    - POST /api/reportes-pet-encontrado/ - Cria reporte com matching automático
    - GET /api/reportes-pet-encontrado/{id}/ - Detalhes
    - PUT/PATCH /api/reportes-pet-encontrado/{id}/ - Atualiza
    - DELETE /api/reportes-pet-encontrado/{id}/ - Remove
    - POST /api/reportes-pet-encontrado/{id}/confirmar-match/ - Confirma match (action)
    
    Permissions:
        - Create: Público (AllowAny)
        - List: Público para aprovados, autenticado para próprios
        - Retrieve/Update/Delete: Quem reportou ou staff
    
    Filters:
        cidade: Filtrar por cidade
        estado: Filtrar por estado (UF)
        especie: Filtrar por espécie
        status: Filtrar por status (pendente, aprovado, rejeitado, em_analise)
    
    Custom Actions:
        @action confirmar_match: Confirma match com pet perdido e notifica dono (staff only)
    
    Matching Automático:
        Ao criar reporte, busca pets perdidos similares usando:
        - Mesma espécie e porte
        - Cores semelhantes (case-insensitive partial match)
        - Proximidade geográfica (até 50km de distância)
        - Mesma cidade ou estado
        - Apenas pets com status 'perdido' e ativos no mapa
        - Máximo de 10 possíveis matches
    
    Note:
        Sistema calcula distância em km usando coordenadas (lat/long)
        Matching usa fórmula Haversine para distância geodésica
    """
    queryset = ReportePetEncontrado.objects.all()
    serializer_class = ReportePetEncontradoSerializer
    permission_classes = [permissions.AllowAny]  # Permite reporte anônimo
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Admins veem todos
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return qs
        
        # Usuários autenticados veem apenas seus próprios reportes
        if self.request.user.is_authenticated and hasattr(self.request.user, 'usuario'):
            return qs.filter(usuario=self.request.user.usuario)
        
        # Não autenticados não veem nada no list
        return qs.none()
    
    def create(self, request, *args, **kwargs):
        """Criar novo reporte de pet encontrado e buscar matches automáticos"""
        # PASSO 1: Cria o reporte base com dados do pet encontrado
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reporte = serializer.save()
        
        # PASSO 2: Processa múltiplas fotos adicionais do pet encontrado
        fotos = request.FILES.getlist('fotos_adicionais')
        for foto in fotos:
            ReportePetEncontradoFoto.objects.create(reporte=reporte, imagem=foto)
        
        # PASSO 3: MATCHING AUTOMÁTICO - Busca pets perdidos similares
        # Algoritmo compara: espécie, porte, cor, localização geográfica (até 50km)
        # e cria lista de possíveis matches baseado em score de similaridade
        self._buscar_matches_automaticos(reporte)
        
        # PASSO 4: Notifica todos os administradores sobre novo reporte
        # Admins precisam moderar/aprovar reportes antes de ficarem públicos
        admin_users = User.objects.filter(is_staff=True)
        for admin in admin_users:
            if hasattr(admin, 'usuario'):
                Notificacao.objects.create(
                    usuario=admin.usuario,
                    tipo='denuncia',
                    titulo='Pet encontrado - Novo reporte',
                    mensagem=f'Pet {reporte.get_especie_display()} encontrado em {reporte.cidade}/{reporte.estado}',
                    link='/admin-panel/?tab=pets-encontrados'
                )
        
        # PASSO 5: Se matching encontrou possíveis donos, notifica cada um deles
        # Aumenta chances de reunir pet perdido com seu dono rapidamente
        if reporte.possiveis_matches.exists():
            for pet_perdido in reporte.possiveis_matches.all():
                Notificacao.objects.create(
                    usuario=pet_perdido.usuario,
                    tipo='interesse_adocao',  # Reutilizando tipo existente
                    titulo='Possível match encontrado!',
                    mensagem=f'Um pet similar ao {pet_perdido.nome} foi encontrado em {reporte.cidade}/{reporte.estado}',
                    link=f'/minhas-solicitacoes/?tab=pets-perdidos'
                )
        
        output_serializer = self.get_serializer(reporte)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def _buscar_matches_automaticos(self, reporte: ReportePetEncontrado) -> None:
        """Busca automática de pets perdidos que podem ser matches"""
        from datetime import timedelta
        from math import radians, sin, cos, sqrt, atan2
        
        # FILTRO INICIAL: Reduz o escopo de busca para pets relevantes
        # Critérios obrigatórios:
        # - status='perdido': Apenas pets ainda não encontrados
        # - ativo=True: Visíveis no mapa (não removidos pelo usuário)
        # - mesma espécie: Cachorro só matcha com cachorro, gato com gato
        # - mesma cidade/estado: Filtra geograficamente (case-insensitive)
        pets_perdidos = PetPerdido.objects.filter(
            status='perdido',
            ativo=True,
            especie=reporte.especie,
            cidade__iexact=reporte.cidade,
            estado__iexact=reporte.estado
        )
        
        # FILTRO TEMPORAL: Pet encontrado hoje não pode ser pet perdido há 6 meses
        # Considera apenas pets perdidos nos últimos 60 dias antes do encontro
        data_limite = reporte.data_encontro - timedelta(days=60)
        pets_perdidos = pets_perdidos.filter(data_perda__gte=data_limite)
        
        matches = []
        
        # ALGORITMO DE SCORE: Calcula similaridade para cada pet perdido
        # Score máximo possível: 100 pontos
        # Score mínimo para match: 50 pontos
        for pet in pets_perdidos:
            score = 0
            
            # CRITÉRIO 1: Mesma espécie (30 pontos - já garantido pelo filtro)
            score += 30
            
            # CRITÉRIO 2: Mesmo porte (20 pontos)
            # Pequeno/Médio/Grande - importante para identificação visual
            if pet.porte == reporte.porte:
                score += 20
            
            # CRITÉRIO 3: Cor similar (25 pontos)
            # Busca parcial: "marrom" matcha "marrom claro" e vice-versa
            # Case-insensitive para evitar problemas de digitação
            if pet.cor and reporte.cor:
                if pet.cor.lower() in reporte.cor.lower() or reporte.cor.lower() in pet.cor.lower():
                    score += 25
            
            # CRITÉRIO 4: Proximidade geográfica (até 25 pontos)
            # Usa coordenadas GPS (lat/long) para calcular distância real em km
            # Fórmula Haversine considera curvatura da Terra
            distancia = self._calcular_distancia(
                float(pet.latitude), float(pet.longitude),
                float(reporte.latitude), float(reporte.longitude)
            )
            if distancia <= 10:  # Até 10km de distância
                score += 15
                if distancia <= 3:  # Muito próximo (até 3km)
                    score += 10  # Bonus extra - alta probabilidade de match
            
            # DECISÃO: Score >= 50 indica possível match (50% de similaridade mínima)
            # Exemplos de matches válidos:
            # - Mesma espécie + mesmo porte + cor similar = 75 pontos ✅
            # - Mesma espécie + mesmo porte + próximo (10km) = 65 pontos ✅
            # - Mesma espécie + cor similar + muito próximo (3km) = 80 pontos ✅
            if score >= 50:
                matches.append(pet)
        
        # Adiciona matches ao reporte (relacionamento ManyToMany)
        # Se houver matches, muda status para 'em_analise' (requer atenção admin)
        if matches:
            reporte.possiveis_matches.set(matches)
            reporte.status = 'em_analise'
            reporte.save()
    
    def _calcular_distancia(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância em km entre duas coordenadas usando fórmula Haversine"""
        # FÓRMULA HAVERSINE: Calcula distância geodésica (linha reta) entre dois pontos
        # Considera a curvatura da Terra (não é distância euclidiana simples)
        # Usado para calcular proximidade entre pet perdido e pet encontrado
        
        # Raio médio da Terra em quilômetros
        # (valor aproximado usado em cálculos geodésicos)
        R = 6371.0
        
        # Converte todas as coordenadas de graus para radianos
        # Necessário para funções trigonométricas (sin, cos)
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Calcula diferenças entre latitudes e longitudes
        dlat = lat2 - lat1  # Diferença de latitude
        dlon = lon2 - lon1  # Diferença de longitude
        
        # FÓRMULA HAVERSINE (parte 1): Calcula 'a' - área do triângulo esférico
        # sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        # Este valor representa a distância angular entre os dois pontos
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        
        # FÓRMULA HAVERSINE (parte 2): Calcula 'c' - ângulo central em radianos
        # 2 * arctan2(√a, √(1-a))
        # atan2 é usado em vez de asin para maior estabilidade numérica
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Distância final: Multiplica ângulo pelo raio da Terra
        # Resultado em quilômetros (mesma unidade do raio R)
        return R * c
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar_match(self, request: Request, pk: Optional[int] = None) -> Response:
        """Admin aprova o match entre pet encontrado e pet perdido"""
        reporte = self.get_object()
        pet_perdido_id = request.data.get('pet_perdido_id')
        
        # VALIDAÇÃO: Pet perdido é obrigatório para confirmar match
        if not pet_perdido_id:
            return Response(
                {'error': 'pet_perdido_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pet_perdido = PetPerdido.objects.get(id=pet_perdido_id)
        except PetPerdido.DoesNotExist:
            return Response(
                {'error': 'Pet perdido não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # PASSO 1: Atualiza reporte de pet encontrado
        # Registra qual pet perdido foi confirmado como match
        # Status vira 'aprovado' e registra quem aprovou + quando
        reporte.pet_perdido_confirmado = pet_perdido
        reporte.status = 'aprovado'
        reporte.analisado_por = request.user
        reporte.data_analise = timezone.now()
        reporte.save()
        
        # PASSO 2: Atualiza pet perdido para 'encontrado'
        # Remove do mapa (ativo=False) e registra data do encontro
        # Evita que o mesmo pet apareça em novos matches
        pet_perdido.status = 'encontrado'
        pet_perdido.data_encontrado = timezone.now()
        pet_perdido.ativo = False  # Remove do mapa
        pet_perdido.save()
        
        # PASSO 3: Notifica o dono do pet perdido (notificação principal)
        # Inclui dados de contato de quem encontrou para facilitar reunião
        if not reporte.dono_notificado:
            Notificacao.objects.create(
                usuario=pet_perdido.usuario,
                tipo='adocao_aprovada',  # Reutilizando tipo existente
                titulo='Seu pet foi encontrado!',
                mensagem=f'{pet_perdido.nome} foi encontrado! Entre em contato com quem encontrou.',
                link='/minhas-solicitacoes/?tab=pets-perdidos',
                contato_telefone=reporte.telefone_contato,
                contato_email=reporte.email_contato
            )
            reporte.dono_notificado = True
            reporte.save()
        
        # PASSO 4: Notifica quem encontrou o pet (se tiver cadastro)
        # Inclui dados de contato do dono para coordenar entrega
        if reporte.usuario:
            Notificacao.objects.create(
                usuario=reporte.usuario,
                tipo='adocao_aprovada',
                titulo='Match confirmado!',
                mensagem=f'O match foi confirmado. O dono do pet entrará em contato.',
                link='/minhas-solicitacoes/?tab=pets-encontrados',
                contato_telefone=pet_perdido.telefone_contato,
                contato_email=pet_perdido.email_contato
            )
        
        serializer = self.get_serializer(reporte)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request, pk=None):
        """Admin rejeita o reporte (não é match válido)"""
        reporte = self.get_object()
        observacoes = request.data.get('observacoes', '')
        
        reporte.status = 'rejeitado'
        reporte.analisado_por = request.user
        reporte.data_analise = timezone.now()
        reporte.observacoes_admin = observacoes
        reporte.save()
        
        serializer = self.get_serializer(reporte)
        return Response(serializer.data)



