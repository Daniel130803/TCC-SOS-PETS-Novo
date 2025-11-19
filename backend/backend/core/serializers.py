from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Animal, Adocao, Usuario, AnimalFoto, AnimalVideo, Denuncia

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
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = Denuncia
        fields = [
            'id', 'titulo', 'descricao', 'localizacao', 'imagem', 'imagem_url',
            'status', 'usuario', 'usuario_nome', 'moderador', 'moderador_nome',
            'observacoes_moderador', 'data_criacao', 'data_atualizacao'
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

    def create(self, validated_data):
        # Associa automaticamente o usuário autenticado
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Busca ou cria o perfil Usuario
            usuario, _ = Usuario.objects.get_or_create(user=request.user)
            validated_data['usuario'] = usuario
        return super().create(validated_data)