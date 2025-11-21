from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Animal, Adocao, Usuario, AnimalFoto, AnimalVideo, 
    Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico,
    AnimalParaAdocao, SolicitacaoAdocao, Notificacao
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