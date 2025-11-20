from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import Animal, Adocao, Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico
from .serializers import AnimalSerializer, AdocaoSerializer, DenunciaSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserMeSerializer, UserUpdateSerializer
from django.contrib.auth.models import User
from .models import Usuario

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


