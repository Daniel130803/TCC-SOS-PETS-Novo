from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import (
    Animal, Adocao, Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico,
    AnimalParaAdocao, SolicitacaoAdocao, Notificacao, Usuario
)
from .serializers import (
    AnimalSerializer, AdocaoSerializer, DenunciaSerializer,
    RegisterSerializer, UserMeSerializer, UserUpdateSerializer,
    AnimalParaAdocaoSerializer, SolicitacaoAdocaoSerializer, NotificacaoSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User

# Create your views here.

class AnimalViewSet(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
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
    queryset = Adocao.objects.all()
    serializer_class = AdocaoSerializer
    permission_classes = [permissions.IsAuthenticated]

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response({'detail': 'Usuário criado com sucesso.'}, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user: User = request.user
        # garante perfil Usuario
        if not hasattr(user, 'usuario'):
            Usuario.objects.get_or_create(user=user)
        data = UserMeSerializer(user).data
        return Response(data)

    def patch(self, request):
        user: User = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Retorna dados atualizados
            updated_data = UserMeSerializer(user).data
            return Response(updated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DenunciaViewSet(viewsets.ModelViewSet):
    queryset = Denuncia.objects.all()
    serializer_class = DenunciaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        # Admins veem tudo, usuários normais veem apenas as próprias denúncias
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            if hasattr(self.request.user, 'usuario'):
                qs = qs.filter(usuario=self.request.user.usuario)
        return qs
    
    def create(self, request, *args, **kwargs):
        # Cria a denúncia principal
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        denuncia = serializer.save()
        
        # Processa múltiplas imagens adicionais
        imagens = request.FILES.getlist('imagens_adicionais')
        for imagem in imagens:
            DenunciaImagem.objects.create(denuncia=denuncia, imagem=imagem)
        
        # Processa múltiplos vídeos adicionais
        videos = request.FILES.getlist('videos_adicionais')
        for video in videos:
            DenunciaVideo.objects.create(denuncia=denuncia, video=video)
        
        # Retorna a denúncia com todas as mídias
        output_serializer = self.get_serializer(denuncia)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request, pk=None):
        """Endpoint para admin aprovar uma denúncia"""
        denuncia = self.get_object()
        status_anterior = denuncia.status
        denuncia.status = 'aprovada'
        denuncia.moderador = request.user
        observacoes = request.data.get('observacoes', '')
        denuncia.observacoes_moderador = observacoes
        denuncia.save()
        
        # Registra no histórico
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
    def rejeitar(self, request, pk=None):
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
    queryset = AnimalParaAdocao.objects.all()
    serializer_class = AnimalParaAdocaoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Usuários normais veem apenas pets aprovados
        # Admins veem todos
        # Doadores veem seus próprios pets
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                # Admin vê tudo
                pass
            elif hasattr(self.request.user, 'usuario'):
                # Usuário normal vê apenas aprovados OU seus próprios pets
                usuario = self.request.user.usuario
                qs = qs.filter(
                    status='aprovado'
                ) | qs.filter(usuario_doador=usuario)
        else:
            # Não autenticado vê apenas aprovados
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
    queryset = SolicitacaoAdocao.objects.all()
    serializer_class = SolicitacaoAdocaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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
    def aprovar(self, request, pk=None):
        """Admin aprova solicitação de adoção"""
        from django.utils import timezone
        
        solicitacao = self.get_object()
        solicitacao.status = 'aprovada'
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        # Marca o animal como adotado
        animal = solicitacao.animal
        animal.status = 'adotado'
        animal.save()
        
        # Obtém dados de contato do doador
        doador = animal.usuario_doador
        telefone_doador = animal.telefone or doador.telefone or 'Não informado'
        email_doador = animal.email or doador.user.email or 'Não informado'
        endereco_doador = animal.endereco_completo or 'Não informado'
        
        # Obtém dados de contato do interessado
        interessado = solicitacao.usuario_interessado
        telefone_interessado = interessado.telefone or 'Não informado'
        email_interessado = interessado.user.email or 'Não informado'
        
        # Notifica o interessado com dados do doador
        Notificacao.objects.create(
            usuario=interessado,
            tipo='adocao_aprovada',
            titulo='Adoção aprovada!',
            mensagem=f'Sua solicitação para adotar "{animal.nome}" foi aprovada! Entre em contato com o doador.',
            link=f'/perfil/?tab=adocoes',
            contato_telefone=telefone_doador,
            contato_email=email_doador,
            contato_endereco=endereco_doador
        )
        solicitacao.notificado_interessado = True
        
        # Notifica o doador com dados do interessado
        Notificacao.objects.create(
            usuario=doador,
            tipo='adocao_aprovada',
            titulo='Solicitação de adoção aprovada!',
            mensagem=f'A solicitação de adoção de "{animal.nome}" foi aprovada. Entre em contato com o interessado.',
            link=f'/perfil/?tab=pets',
            contato_telefone=telefone_interessado,
            contato_email=email_interessado
        )
        solicitacao.notificado_doador = True
        solicitacao.save()
        
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request, pk=None):
        """Admin rejeita solicitação de adoção"""
        from django.utils import timezone
        
        solicitacao = self.get_object()
        solicitacao.status = 'rejeitada'
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        # Notifica o interessado
        motivo = request.data.get('motivo', 'Não especificado')
        Notificacao.objects.create(
            usuario=solicitacao.usuario_interessado,
            tipo='adocao_rejeitada',
            titulo='Solicitação rejeitada',
            mensagem=f'Sua solicitação para adotar "{solicitacao.animal.nome}" foi rejeitada. Motivo: {motivo}',
        )
        
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)


class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Usuários veem apenas suas próprias notificações
        if hasattr(self.request.user, 'usuario'):
            return Notificacao.objects.filter(usuario=self.request.user.usuario).order_by('-data_criacao')
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



