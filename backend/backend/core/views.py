from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from math import radians, sin, cos, sqrt, atan2
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
            link=f'/minhas-solicitacoes/',
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
            link=f'/minhas-solicitacoes/',
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
    def cancelar(self, request, pk=None):
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
    """Lista solicitações de adoção enviadas pelo usuário (como interessado)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'usuario'):
            return Response([], status=status.HTTP_200_OK)
        
        usuario = request.user.usuario
        solicitacoes = SolicitacaoAdocao.objects.filter(
            usuario_interessado=usuario
        ).select_related('animal', 'animal__usuario_doador').order_by('-data_solicitacao')
        
        data = []
        for sol in solicitacoes:
            animal = sol.animal
            doador = animal.usuario_doador
            
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
            
            # Se aprovada, revela dados de contato do doador
            if sol.status == 'aprovada':
                item['doador_telefone'] = animal.telefone or doador.telefone or None
                item['doador_email'] = animal.email or doador.user.email or None
                item['doador_endereco'] = animal.endereco_completo or None
            
            data.append(item)
        
        return Response({'results': data}, status=status.HTTP_200_OK)


class SolicitacoesRecebidasView(APIView):
    """Lista solicitações de adoção recebidas para os pets do usuário (como doador)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'usuario'):
            return Response([], status=status.HTTP_200_OK)
        
        usuario = request.user.usuario
        # Busca solicitações para pets cadastrados pelo usuário
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
            
            # Se aprovada, revela dados de contato do interessado
            if sol.status == 'aprovada':
                item['interessado_telefone'] = interessado.telefone or None
                item['interessado_email'] = interessado.user.email or None
            
            data.append(item)
        
        return Response({'results': data}, status=status.HTTP_200_OK)


class MeusPetsCadastradosView(APIView):
    """Lista pets cadastrados pelo usuário com contagem de solicitações"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'usuario'):
            return Response([], status=status.HTTP_200_OK)
        
        usuario = request.user.usuario
        pets = AnimalParaAdocao.objects.filter(
            usuario_doador=usuario
        ).order_by('-data_cadastro')
        
        data = []
        for pet in pets:
            # Conta solicitações
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
    """ViewSet para gerenciar contatos com o administrador"""
    queryset = Contato.objects.all()
    serializer_class = ContatoSerializer
    permission_classes = [permissions.AllowAny]  # Permite contato anônimo
    
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
    """ViewSet para gerenciar pets perdidos"""
    queryset = PetPerdido.objects.all()
    serializer_class = PetPerdidoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pet_perdido = serializer.save()
        
        # Processa múltiplas fotos adicionais
        fotos = request.FILES.getlist('fotos_adicionais')
        for foto in fotos:
            PetPerdidoFoto.objects.create(pet_perdido=pet_perdido, imagem=foto)
        
        # Notifica administradores
        admin_users = User.objects.filter(is_staff=True)
        for admin in admin_users:
            if hasattr(admin, 'usuario'):
                Notificacao.objects.create(
                    usuario=admin.usuario,
                    tipo='denuncia',  # Reutilizando tipo
                    titulo='Novo pet perdido cadastrado',
                    mensagem=f'Pet {pet_perdido.nome} perdido em {pet_perdido.cidade}/{pet_perdido.estado}',
                    link='/admin-panel/?tab=pets-perdidos'
                )
        
        output_serializer = self.get_serializer(pet_perdido)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def marcar_encontrado(self, request, pk=None):
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
    def reativar(self, request, pk=None):
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
    """ViewSet para gerenciar reportes de pets encontrados"""
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reporte = serializer.save()
        
        # Processa múltiplas fotos adicionais
        fotos = request.FILES.getlist('fotos_adicionais')
        for foto in fotos:
            ReportePetEncontradoFoto.objects.create(reporte=reporte, imagem=foto)
        
        # Busca matches automáticos
        self._buscar_matches_automaticos(reporte)
        
        # Notifica administradores
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
        
        # Se houver matches, notifica os donos dos pets perdidos
        if reporte.possiveis_matches.exists():
            for pet_perdido in reporte.possiveis_matches.all():
                Notificacao.objects.create(
                    usuario=pet_perdido.usuario,
                    tipo='interesse_adocao',  # Reutilizando tipo
                    titulo='Possível match encontrado!',
                    mensagem=f'Um pet similar ao {pet_perdido.nome} foi encontrado em {reporte.cidade}/{reporte.estado}',
                    link=f'/minhas-solicitacoes/?tab=pets-perdidos'
                )
        
        output_serializer = self.get_serializer(reporte)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def _buscar_matches_automaticos(self, reporte):
        """Busca automática de pets perdidos que podem ser matches"""
        from datetime import timedelta
        from math import radians, sin, cos, sqrt, atan2
        
        # Busca pets perdidos ativos na mesma cidade/estado e mesma espécie
        pets_perdidos = PetPerdido.objects.filter(
            status='perdido',
            ativo=True,
            especie=reporte.especie,
            cidade__iexact=reporte.cidade,
            estado__iexact=reporte.estado
        )
        
        # Filtra por proximidade temporal (até 60 dias antes do encontro)
        data_limite = reporte.data_encontro - timedelta(days=60)
        pets_perdidos = pets_perdidos.filter(data_perda__gte=data_limite)
        
        matches = []
        
        for pet in pets_perdidos:
            score = 0
            
            # Mesma espécie (já filtrado)
            score += 30
            
            # Mesmo porte
            if pet.porte == reporte.porte:
                score += 20
            
            # Cor similar (busca parcial)
            if pet.cor and reporte.cor:
                if pet.cor.lower() in reporte.cor.lower() or reporte.cor.lower() in pet.cor.lower():
                    score += 25
            
            # Proximidade geográfica (até 10km)
            distancia = self._calcular_distancia(
                float(pet.latitude), float(pet.longitude),
                float(reporte.latitude), float(reporte.longitude)
            )
            if distancia <= 10:
                score += 15
                if distancia <= 3:
                    score += 10  # Bonus para muito próximo
            
            # Se score >= 50, considera possível match
            if score >= 50:
                matches.append(pet)
        
        # Adiciona matches ao reporte
        if matches:
            reporte.possiveis_matches.set(matches)
            reporte.status = 'em_analise'
            reporte.save()
    
    def _calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula distância em km entre duas coordenadas"""
        R = 6371.0  # Raio da Terra em km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprovar_match(self, request, pk=None):
        """Admin aprova o match entre pet encontrado e pet perdido"""
        reporte = self.get_object()
        pet_perdido_id = request.data.get('pet_perdido_id')
        
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
        
        # Atualiza reporte
        reporte.pet_perdido_confirmado = pet_perdido
        reporte.status = 'aprovado'
        reporte.analisado_por = request.user
        reporte.data_analise = timezone.now()
        reporte.save()
        
        # Atualiza pet perdido
        pet_perdido.status = 'encontrado'
        pet_perdido.data_encontrado = timezone.now()
        pet_perdido.ativo = False
        pet_perdido.save()
        
        # Notifica o dono do pet perdido
        if not reporte.dono_notificado:
            Notificacao.objects.create(
                usuario=pet_perdido.usuario,
                tipo='adocao_aprovada',  # Reutilizando tipo
                titulo='Seu pet foi encontrado!',
                mensagem=f'{pet_perdido.nome} foi encontrado! Entre em contato com quem encontrou.',
                link='/minhas-solicitacoes/?tab=pets-perdidos',
                contato_telefone=reporte.telefone_contato,
                contato_email=reporte.email_contato
            )
            reporte.dono_notificado = True
            reporte.save()
        
        # Notifica quem encontrou
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



