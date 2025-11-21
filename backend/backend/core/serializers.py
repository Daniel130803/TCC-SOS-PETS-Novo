from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Animal, Adocao, Usuario, AnimalFoto, AnimalVideo, 
    Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico,
    AnimalParaAdocao, SolicitacaoAdocao, Notificacao, Contato,
    PetPerdido, PetPerdidoFoto, ReportePetEncontrado, ReportePetEncontradoFoto
)

class AnimalSerializer(serializers.ModelSerializer):
    imagem_absolute = serializers.SerializerMethodField()
    fotos_urls = serializers.SerializerMethodField()
    videos_urls = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = ['id','nome','tipo','porte','sexo','raca','idade_anos','descricao','estado','cidade','status','data_criacao','data_atualizacao','imagem_url','imagem_absolute','fotos_urls','videos_urls']

    def get_imagem_absolute(self, obj):
        request = self.context.get('request')
        if obj.imagem and hasattr(obj.imagem, 'url'):
            url = obj.imagem.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_fotos_urls(self, obj):
        urls = []
        request = self.context.get('request')
        for f in obj.fotos.all():
            if getattr(f, 'imagem', None) and hasattr(f.imagem, 'url') and f.imagem:
                url = f.imagem.url
                if request:
                    urls.append(request.build_absolute_uri(url))
                else:
                    urls.append(url)
            elif f.url:
                urls.append(f.url)
        return urls

    def get_videos_urls(self, obj):
        return [v.url for v in obj.videos.all()]

class AdocaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adocao
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    telefone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'telefone']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('E-mail já cadastrado.')
        return value

    def create(self, validated_data):
        # retira telefone do payload do User
        telefone = validated_data.pop('telefone', '')
        user = User.objects.create_user(**validated_data)
        Usuario.objects.create(user=user, telefone=telefone or '')
        return user

class UserMeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    telefone = serializers.CharField(read_only=True, allow_blank=True)

    def to_representation(self, instance):
        # instance é User
        perfil = getattr(instance, 'usuario', None)
        telefone = ''
        if perfil:
            telefone = perfil.telefone or ''
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email or '',
            'first_name': instance.first_name or '',
            'is_staff': instance.is_staff,
            'telefone': telefone,
        }

class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    telefone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        user = self.context['request'].user
        if value and User.objects.filter(email__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('Este e-mail já está em uso.')
        return value

    def update(self, instance, validated_data):
        # instance é User
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Atualiza telefone no perfil Usuario
        telefone = validated_data.get('telefone')
        if telefone is not None:
            perfil, created = Usuario.objects.get_or_create(user=instance)
            perfil.telefone = telefone
            perfil.save()

        return instance


class DenunciaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.user.get_full_name', read_only=True)
    moderador_nome = serializers.CharField(source='moderador.get_full_name', read_only=True)
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    imagem_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    imagens_urls = serializers.SerializerMethodField()
    videos_urls = serializers.SerializerMethodField()
    historico = serializers.SerializerMethodField()

    class Meta:
        model = Denuncia
        fields = [
            'id', 'titulo', 'categoria', 'categoria_display', 'descricao', 'localizacao', 
            'imagem', 'video', 'imagem_url', 'video_url', 'imagens_urls', 'videos_urls',
            'status', 'usuario', 'usuario_nome', 'moderador', 'moderador_nome',
            'observacoes_moderador', 'data_criacao', 'data_atualizacao', 'historico'
        ]
        read_only_fields = ['usuario', 'moderador', 'observacoes_moderador', 'data_criacao', 'data_atualizacao']

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and hasattr(obj.imagem, 'url'):
            url = obj.imagem.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video and hasattr(obj.video, 'url'):
            url = obj.video.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_imagens_urls(self, obj):
        request = self.context.get('request')
        urls = []
        for img in obj.imagens_adicionais.all():
            if img.imagem and hasattr(img.imagem, 'url'):
                url = img.imagem.url
                if request:
                    urls.append(request.build_absolute_uri(url))
                else:
                    urls.append(url)
        return urls
    
    def get_videos_urls(self, obj):
        request = self.context.get('request')
        urls = []
        for vid in obj.videos_adicionais.all():
            if vid.video and hasattr(vid.video, 'url'):
                url = vid.video.url
                if request:
                    urls.append(request.build_absolute_uri(url))
                else:
                    urls.append(url)
        return urls
    
    def get_historico(self, obj):
        historico_qs = obj.historico.all().order_by('-data_criacao')
        return DenunciaHistoricoSerializer(historico_qs, many=True).data

    def create(self, validated_data):
        # Associa automaticamente o usuário autenticado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Busca ou cria o perfil Usuario
            usuario, _ = Usuario.objects.get_or_create(user=request.user)
            validated_data['usuario'] = usuario
        
        # Cria a denúncia
        denuncia = super().create(validated_data)
        
        # Registra no histórico
        DenunciaHistorico.objects.create(
            denuncia=denuncia,
            tipo='criacao',
            usuario=request.user if request and request.user.is_authenticated else None,
            comentario='Denúncia criada'
        )
        
        return denuncia


class DenunciaHistoricoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = DenunciaHistorico
        fields = ['id', 'tipo', 'tipo_display', 'usuario', 'usuario_nome', 
                  'status_anterior', 'status_novo', 'comentario', 'data_criacao']
        read_only_fields = ['data_criacao']


class AnimalParaAdocaoSerializer(serializers.ModelSerializer):
    usuario_doador_nome = serializers.CharField(source='usuario_doador.user.get_full_name', read_only=True)
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)
    porte_display = serializers.CharField(source='get_porte_display', read_only=True)
    sexo_display = serializers.CharField(source='get_sexo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    imagem_principal_url = serializers.SerializerMethodField()
    imagens_adicionais = serializers.SerializerMethodField()
    # Endereço é oculto por padrão, será revelado apenas após aprovação da adoção
    endereco_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimalParaAdocao
        fields = [
            'id', 'usuario_doador', 'usuario_doador_nome', 'nome', 'especie', 
            'especie_display', 'porte', 'porte_display', 'sexo', 'sexo_display',
            'cor', 'idade', 'descricao', 'temperamento', 'historico_saude',
            'caracteristicas_especiais', 'estado', 'cidade', 'endereco_completo', 
            'telefone', 'email', 'imagem_principal', 'imagem_principal_url',
            'imagens_adicionais', 'status', 'status_display', 'data_cadastro', 
            'data_aprovacao'
        ]
        read_only_fields = ['usuario_doador', 'status', 'data_cadastro', 'data_aprovacao']
    
    def get_imagem_principal_url(self, obj):
        request = self.context.get('request')
        if obj.imagem_principal and hasattr(obj.imagem_principal, 'url'):
            url = obj.imagem_principal.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_imagens_adicionais(self, obj):
        # Placeholder para futuras imagens adicionais
        return []
    
    def get_endereco_completo(self, obj):
        # Oculta endereço por padrão
        # Será revelado apenas para solicitações aprovadas
        request = self.context.get('request')
        if request and hasattr(request, 'revelar_endereco') and request.revelar_endereco:
            return obj.endereco_completo
        return None
    
    def create(self, validated_data):
        # Associa automaticamente o usuário autenticado como doador
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            usuario, _ = Usuario.objects.get_or_create(user=request.user)
            validated_data['usuario_doador'] = usuario
        
        # Se selecionou "Outro" na cor, usa o valor do campo cor_outro
        cor_outro = request.data.get('cor_outro') if request else None
        if validated_data.get('cor') == 'Outro' and cor_outro:
            validated_data['cor'] = cor_outro
        
        return super().create(validated_data)


class SolicitacaoAdocaoSerializer(serializers.ModelSerializer):
    usuario_interessado_nome = serializers.CharField(source='usuario_interessado.user.get_full_name', read_only=True)
    animal_nome = serializers.CharField(source='animal.nome', read_only=True)
    animal_especie = serializers.CharField(source='animal.get_especie_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SolicitacaoAdocao
        fields = [
            'id', 'animal', 'animal_nome', 'animal_especie', 'usuario_interessado',
            'usuario_interessado_nome', 'mensagem', 'status', 'status_display',
            'data_solicitacao', 'data_aprovacao', 'notificado_doador', 'notificado_interessado'
        ]
        read_only_fields = ['usuario_interessado', 'status', 'data_solicitacao', 'data_aprovacao', 
                           'notificado_doador', 'notificado_interessado']
    
    def create(self, validated_data):
        # Associa automaticamente o usuário autenticado como interessado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            usuario, _ = Usuario.objects.get_or_create(user=request.user)
            validated_data['usuario_interessado'] = usuario
        
        return super().create(validated_data)


class NotificacaoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Notificacao
        fields = [
            'id', 'usuario', 'tipo', 'tipo_display', 'titulo', 'mensagem',
            'link', 'contato_telefone', 'contato_email', 'contato_endereco',
            'lida', 'data_criacao'
        ]
        read_only_fields = ['usuario', 'data_criacao']


class ContatoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.user.get_full_name', read_only=True)
    respondido_por_nome = serializers.CharField(source='respondido_por.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Contato
        fields = [
            'id', 'usuario', 'usuario_nome', 'nome', 'email', 'assunto', 'mensagem',
            'status', 'status_display', 'data_criacao', 'lido', 'data_leitura',
            'resposta', 'data_resposta', 'respondido_por', 'respondido_por_nome',
            'usuario_notificado'
        ]
        read_only_fields = ['usuario', 'data_criacao', 'lido', 'data_leitura', 
                           'data_resposta', 'respondido_por', 'usuario_notificado']
    
    def create(self, validated_data):
        # Associa o usuário autenticado se estiver logado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if hasattr(request.user, 'usuario'):
                validated_data['usuario'] = request.user.usuario
                # Preenche nome e email do usuário logado apenas se não foram fornecidos
                if not validated_data.get('nome'):
                    validated_data['nome'] = request.user.get_full_name() or request.user.username
                if not validated_data.get('email'):
                    validated_data['email'] = request.user.email or ''
        
        # Garante que nome e email existam (obrigatórios)
        if not validated_data.get('nome'):
            validated_data['nome'] = validated_data.get('email', '').split('@')[0] or 'Usuário Anônimo'
        
        return super().create(validated_data)


# ===== PET PERDIDO =====
class PetPerdidoFotoSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PetPerdidoFoto
        fields = ['id', 'imagem', 'imagem_url', 'descricao', 'data_criacao']
    
    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and hasattr(obj.imagem, 'url'):
            url = obj.imagem.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class PetPerdidoSerializer(serializers.ModelSerializer):
    """Serializer para pets perdidos"""
    fotos_adicionais = PetPerdidoFotoSerializer(many=True, read_only=True)
    imagem_principal_url = serializers.SerializerMethodField()
    usuario_nome = serializers.SerializerMethodField()
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)
    porte_display = serializers.CharField(source='get_porte_display', read_only=True)
    sexo_display = serializers.CharField(source='get_sexo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_reportes = serializers.SerializerMethodField()
    
    class Meta:
        model = PetPerdido
        fields = [
            'id', 'usuario', 'usuario_nome', 'nome', 'especie', 'especie_display',
            'raca', 'cor', 'porte', 'porte_display', 'sexo', 'sexo_display',
            'idade_aproximada', 'caracteristicas_distintivas', 'descricao',
            'data_perda', 'hora_perda', 'latitude', 'longitude', 'endereco',
            'bairro', 'cidade', 'estado', 'telefone_contato', 'email_contato',
            'whatsapp', 'oferece_recompensa', 'valor_recompensa',
            'imagem_principal', 'imagem_principal_url', 'fotos_adicionais',
            'status', 'status_display', 'ativo', 'visualizacoes',
            'data_criacao', 'data_atualizacao', 'data_encontrado',
            'total_reportes'
        ]
        read_only_fields = ['usuario', 'visualizacoes', 'data_criacao', 'data_atualizacao']
    
    def get_imagem_principal_url(self, obj):
        request = self.context.get('request')
        if obj.imagem_principal and hasattr(obj.imagem_principal, 'url'):
            url = obj.imagem_principal.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_usuario_nome(self, obj):
        if obj.usuario and obj.usuario.user:
            return obj.usuario.user.get_full_name() or obj.usuario.user.username
        return None
    
    def get_total_reportes(self, obj):
        """Retorna quantidade de reportes de pets encontrados relacionados"""
        return obj.reportes_relacionados.filter(status='pendente').count()
    
    def create(self, validated_data):
        # Associa automaticamente ao usuário logado
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(request.user, 'usuario'):
            validated_data['usuario'] = request.user.usuario
        return super().create(validated_data)


# ===== PET ENCONTRADO =====
class ReportePetEncontradoFotoSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportePetEncontradoFoto
        fields = ['id', 'imagem', 'imagem_url', 'descricao', 'data_criacao']
    
    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and hasattr(obj.imagem, 'url'):
            url = obj.imagem.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ReportePetEncontradoSerializer(serializers.ModelSerializer):
    """Serializer para reportes de pets encontrados"""
    fotos_adicionais = ReportePetEncontradoFotoSerializer(many=True, read_only=True)
    imagem_principal_url = serializers.SerializerMethodField()
    usuario_nome = serializers.SerializerMethodField()
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)
    porte_display = serializers.CharField(source='get_porte_display', read_only=True)
    sexo_display = serializers.CharField(source='get_sexo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    possiveis_matches_detalhes = serializers.SerializerMethodField()
    pet_perdido_confirmado_detalhes = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportePetEncontrado
        fields = [
            'id', 'usuario', 'usuario_nome', 'nome_pessoa', 'telefone_contato',
            'email_contato', 'especie', 'especie_display', 'cor', 'porte',
            'porte_display', 'sexo', 'sexo_display', 'descricao',
            'caracteristicas_distintivas', 'data_encontro', 'hora_encontro',
            'latitude', 'longitude', 'endereco', 'bairro', 'cidade', 'estado',
            'pet_com_usuario', 'local_temporario', 'imagem_principal',
            'imagem_principal_url', 'fotos_adicionais', 'possiveis_matches',
            'possiveis_matches_detalhes', 'pet_perdido_confirmado',
            'pet_perdido_confirmado_detalhes', 'status', 'status_display',
            'analisado_por', 'observacoes_admin', 'data_criacao', 'data_analise',
            'data_atualizacao', 'dono_notificado'
        ]
        read_only_fields = [
            'usuario', 'possiveis_matches', 'pet_perdido_confirmado',
            'analisado_por', 'data_criacao', 'data_analise', 'data_atualizacao',
            'dono_notificado'
        ]
    
    def get_imagem_principal_url(self, obj):
        request = self.context.get('request')
        if obj.imagem_principal and hasattr(obj.imagem_principal, 'url'):
            url = obj.imagem_principal.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
    
    def get_usuario_nome(self, obj):
        if obj.usuario and obj.usuario.user:
            return obj.usuario.user.get_full_name() or obj.usuario.user.username
        return obj.nome_pessoa
    
    def get_possiveis_matches_detalhes(self, obj):
        """Retorna detalhes resumidos dos possíveis matches"""
        matches = obj.possiveis_matches.all()[:5]  # Limita a 5 matches
        return [{
            'id': m.id,
            'nome': m.nome,
            'especie': m.get_especie_display(),
            'cor': m.cor,
            'cidade': m.cidade,
            'estado': m.estado,
            'distancia_km': self._calcular_distancia(obj.latitude, obj.longitude, m.latitude, m.longitude),
            'telefone_contato': m.telefone_contato if self.context.get('show_contact') else None
        } for m in matches]
    
    def get_pet_perdido_confirmado_detalhes(self, obj):
        """Retorna detalhes do pet perdido confirmado como match"""
        if obj.pet_perdido_confirmado:
            m = obj.pet_perdido_confirmado
            return {
                'id': m.id,
                'nome': m.nome,
                'especie': m.get_especie_display(),
                'cor': m.cor,
                'cidade': m.cidade,
                'estado': m.estado,
                'telefone_contato': m.telefone_contato,
                'email_contato': m.email_contato,
                'whatsapp': m.whatsapp
            }
        return None
    
    def _calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula distância aproximada em km entre duas coordenadas"""
        from math import radians, sin, cos, sqrt, atan2
        
        # Raio da Terra em km
        R = 6371.0
        
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distancia = R * c
        return round(distancia, 2)
    
    def create(self, validated_data):
        # Associa automaticamente ao usuário logado se houver
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(request.user, 'usuario'):
            validated_data['usuario'] = request.user.usuario
            # Se tem usuário, preenche dados do perfil
            if not validated_data.get('nome_pessoa'):
                validated_data['nome_pessoa'] = request.user.get_full_name() or request.user.username
            if not validated_data.get('email_contato'):
                validated_data['email_contato'] = request.user.email
            if not validated_data.get('telefone_contato') and request.user.usuario.telefone:
                validated_data['telefone_contato'] = request.user.usuario.telefone
        
        return super().create(validated_data)
