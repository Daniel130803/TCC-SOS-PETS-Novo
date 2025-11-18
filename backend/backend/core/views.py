from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Animal, Adocao
from .serializers import AnimalSerializer, AdocaoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
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
