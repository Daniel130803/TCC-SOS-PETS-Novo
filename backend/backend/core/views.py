from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import Animal, Adocao, Denuncia
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar(self, request, pk=None):
        """Endpoint para admin aprovar uma denúncia"""
        denuncia = self.get_object()
        denuncia.status = 'aprovada'
        denuncia.moderador = request.user
        denuncia.observacoes_moderador = request.data.get('observacoes', '')
        denuncia.save()
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rejeitar(self, request, pk=None):
        """Endpoint para admin rejeitar uma denúncia"""
        denuncia = self.get_object()
        denuncia.status = 'rejeitada'
        denuncia.moderador = request.user
        denuncia.observacoes_moderador = request.data.get('observacoes', 'Denúncia rejeitada.')
        denuncia.save()
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def em_andamento(self, request, pk=None):
        """Endpoint para admin marcar denúncia como em andamento"""
        denuncia = self.get_object()
        denuncia.status = 'em_andamento'
        denuncia.moderador = request.user
        denuncia.observacoes_moderador = request.data.get('observacoes', 'Denúncia em análise.')
        denuncia.save()
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def resolver(self, request, pk=None):
        """Endpoint para admin marcar denúncia como resolvida"""
        denuncia = self.get_object()
        denuncia.status = 'resolvida'
        denuncia.moderador = request.user
        denuncia.observacoes_moderador = request.data.get('observacoes', 'Denúncia resolvida.')
        denuncia.save()
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

