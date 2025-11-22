from typing import Optional
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator,
    RegexValidator,
    FileExtensionValidator,
    EmailValidator
)
from django.core.exceptions import ValidationError
import re
from .validators import validate_image_file, validate_video_file


# ===== VALIDATORS CUSTOMIZADOS =====
# NOTA: Validators de imagem e vídeo estão em validators.py
# (validate_image_file e validate_video_file)

def validar_telefone_brasileiro(valor):
    """
    Valida formato de telefone brasileiro.
    Aceita: (11) 99999-9999 ou (11) 9999-9999 ou 11999999999
    """
    if not valor:  # Permite vazio se blank=True
        return
    
    # Remove caracteres não numéricos para validação
    apenas_numeros = re.sub(r'\D', '', valor)
    
    # Deve ter 10 ou 11 dígitos (com DDD)
    if len(apenas_numeros) < 10 or len(apenas_numeros) > 11:
        raise ValidationError(
            'Telefone deve ter 10 ou 11 dígitos (incluindo DDD). '
            'Exemplo: (11) 99999-9999'
        )


def validar_cpf(valor):
    """
    Valida formato e dígitos verificadores de CPF.
    """
    if not valor:  # Permite vazio se blank=True
        return
    
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', valor)
    
    # Deve ter exatamente 11 dígitos
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos')
    
    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido')
    
    # Validação dos dígitos verificadores
    def calcular_digito(cpf_parcial):
        soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Valida primeiro dígito
    if int(cpf[9]) != calcular_digito(cpf[:9]):
        raise ValidationError('CPF com dígitos verificadores inválidos')
    
    # Valida segundo dígito
    if int(cpf[10]) != calcular_digito(cpf[:10]):
        raise ValidationError('CPF com dígitos verificadores inválidos')


def validar_tamanho_imagem(arquivo):
    """
    Valida tamanho máximo de imagem (5MB).
    """
    if arquivo:
        tamanho_mb = arquivo.size / (1024 * 1024)
        if tamanho_mb > 5:
            raise ValidationError(
                f'Imagem muito grande ({tamanho_mb:.1f}MB). Tamanho máximo: 5MB'
            )


def validar_tamanho_video(arquivo):
    """
    Valida tamanho máximo de vídeo (20MB).
    """
    if arquivo:
        tamanho_mb = arquivo.size / (1024 * 1024)
        if tamanho_mb > 20:
            raise ValidationError(
                f'Vídeo muito grande ({tamanho_mb:.1f}MB). Tamanho máximo: 20MB'
            )


def validar_estado_brasil(valor):
    """
    Valida sigla de estado brasileiro (UF).
    """
    if not valor:
        return
    
    estados_validos = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    if valor.upper() not in estados_validos:
        raise ValidationError(
            f'Estado inválido. Use a sigla (AC, SP, RJ, etc.)'
        )

# ===== USUÁRIO (Estendido) =====
class Usuario(models.Model):
    """
    Perfil estendido do usuário do sistema S.O.S Pets.
    
    Estende o modelo User padrão do Django adicionando informações
    complementares necessárias para o sistema de adoção e pets perdidos.
    
    Attributes:
        user (User): Relacionamento OneToOne com usuário Django
        telefone (str): Telefone de contato do usuário
        endereco (str): Endereço completo
        cidade (str): Cidade de residência
        estado (str): Estado (sigla UF com 2 caracteres)
    
    Methods:
        __str__: Retorna o username do usuário associado
    
    Meta:
        verbose_name: 'Usuário'
        verbose_name_plural: 'Usuários'
    
    Example:
        >>> user = User.objects.create_user('joao', 'joao@email.com', 'senha123')
        >>> usuario = Usuario.objects.create(user=user, telefone='11999999999', cidade='São Paulo', estado='SP')
        >>> print(usuario)
        joao
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[validar_telefone_brasileiro],
        help_text='Formato: (11) 99999-9999'
    )
    endereco = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Endereço completo (Rua, número, bairro)'
    )
    cidade = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='Nome da cidade'
    )
    estado = models.CharField(
        max_length=2, 
        blank=True, 
        null=True,
        validators=[validar_estado_brasil],
        help_text='Sigla do estado (AC, SP, RJ, etc.)'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


# ===== ANIMAL =====
class Animal(models.Model):
    """
    Catálogo de animais cadastrados pela ONG para adoção.
    
    Modelo principal que representa os animais disponíveis no sistema,
    gerenciados diretamente pela equipe da ONG. Inclui informações
    completas sobre características físicas, comportamento e status.
    
    Attributes:
        nome (str): Nome do animal (max 100 caracteres)
        tipo (str): Tipo do animal - Cachorro ou Gato (choices)
        porte (str): Porte físico - Pequeno, Médio ou Grande (choices)
        sexo (str): Sexo - Macho ou Fêmea (choices)
        raca (str): Raça do animal (opcional)
        cor (str): Cor predominante da pelagem
        idade (int): Idade em anos (validador >= 0)
        descricao (str): Descrição detalhada do animal
        imagem_url (str): URL da imagem principal
        cidade (str): Cidade onde o animal se encontra
        estado (str): Estado (sigla UF)
        status (str): Status de disponibilidade - Disponível, Adotado ou Indisponível (choices)
        data_cadastro (datetime): Data de cadastro automática
    
    Methods:
        __str__: Retorna nome e tipo do animal
        delete: Limpa imagens associadas antes de deletar
        save: Override para lógica customizada ao salvar
    
    Meta:
        verbose_name: 'Animal'
        verbose_name_plural: 'Animais'
        ordering: ['-data_cadastro']
    
    Example:
        >>> animal = Animal.objects.create(
        ...     nome='Rex',
        ...     tipo='cachorro',
        ...     porte='medio',
        ...     sexo='macho',
        ...     idade=3,
        ...     cidade='São Paulo',
        ...     estado='SP'
        ... )
        >>> print(animal)
        Rex (Cachorro)
    """
    TIPO_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
    ]
    PORTE_CHOICES = [
        ('pequeno', 'Pequeno'),
        ('medio', 'Médio'),
        ('grande', 'Grande'),
    ]
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('femea', 'Fêmea'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível para Adoção'),
        ('adotado', 'Adotado'),
        ('indisponivel', 'Indisponível'),
    ]
    
    nome = models.CharField(
        max_length=100,
        help_text='Nome do animal (máximo 100 caracteres)'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, blank=True, null=True)
    raca = models.CharField(
        max_length=100, 
        blank=True,
        help_text='Raça do animal (opcional)'
    )
    idade_anos = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(30)], 
        blank=True, 
        null=True,
        help_text='Idade em anos (0-30)'
    )
    descricao = models.TextField(
        blank=True,
        max_length=2000,
        help_text='Descrição detalhada do animal (máximo 2000 caracteres)'
    )
    estado = models.CharField(
        max_length=2, 
        blank=True, 
        null=True,
        validators=[validar_estado_brasil]
    )
    cidade = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='Cidade onde o animal se encontra'
    )
    imagem = models.ImageField(
        upload_to='animais/', 
        blank=True, 
        null=True,
        validators=[
            validar_tamanho_imagem,
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
                message='Apenas imagens JPG, PNG ou WebP são permitidas'
            )
        ],
        help_text='Imagem do animal (máximo 5MB)'
    )
    imagem_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"
        ordering = ['-data_criacao']


class AnimalFoto(models.Model):
    """
    Galeria de fotos adicionais dos animais.
    
    Armazena múltiplas fotos de cada animal do catálogo, permitindo
    que os usuários visualizem diferentes ângulos e características.
    Suporta upload direto de arquivos ou URLs externas.
    
    Attributes:
        animal (Animal): Animal relacionado (ForeignKey)
        url (str): URL externa da imagem (opcional, max 500 caracteres)
        imagem (ImageField): Upload direto da imagem (opcional)
        data_criacao (datetime): Data de upload automática
    
    Methods:
        __str__: Retorna identificação da foto
    
    Meta:
        verbose_name: 'Foto do Animal'
        verbose_name_plural: 'Fotos dos Animais'
        ordering: ['id']
    
    Example:
        >>> animal = Animal.objects.get(nome='Rex')
        >>> foto = AnimalFoto.objects.create(
        ...     animal=animal,
        ...     imagem='animais/rex_foto2.jpg'
        ... )
        >>> print(foto)
        Foto de Rex
    """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='fotos')
    url = models.URLField(blank=True, null=True)
    imagem = models.ImageField(
        upload_to='animais/fotos/',
        blank=True,
        null=True,
        validators=[validate_image_file]
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.animal.nome}"

    class Meta:
        verbose_name = "Foto do Animal"
        verbose_name_plural = "Fotos do Animal"
        ordering = ['id']


class AnimalVideo(models.Model):
    """
    Vídeos complementares dos animais.
    
    Permite adicionar vídeos para mostrar o comportamento e personalidade
    dos animais, facilitando a decisão de adoção pelos usuários.
    
    Attributes:
        animal (Animal): Animal relacionado (ForeignKey)
        url (str): URL do vídeo (YouTube, Vimeo, etc.) - max 500 caracteres
        data_criacao (datetime): Data de cadastro automática
    
    Methods:
        __str__: Retorna identificação do vídeo
    
    Meta:
        verbose_name: 'Vídeo do Animal'
        verbose_name_plural: 'Vídeos dos Animais'
        ordering: ['id']
    
    Example:
        >>> animal = Animal.objects.get(nome='Rex')
        >>> video = AnimalVideo.objects.create(
        ...     animal=animal,
        ...     url='https://youtube.com/watch?v=abc123'
        ... )
        >>> print(video)
        Vídeo de Rex
    """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='videos')
    url = models.URLField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vídeo de {self.animal.nome}"

    class Meta:
        verbose_name = "Vídeo do Animal"
        verbose_name_plural = "Vídeos do Animal"
        ordering = ['id']


# ===== ADOÇÃO =====
class Adocao(models.Model):
    """
    Processo de adoção dos animais do catálogo da ONG.
    
    Gerencia as solicitações de adoção feitas pelos usuários para
    os animais do catálogo oficial da ONG. Controla o fluxo desde
    a solicitação até a aprovação ou rejeição.
    
    Attributes:
        usuario (Usuario): Usuário solicitante (ForeignKey)
        animal (Animal): Animal desejado (ForeignKey)
        data_solicitacao (datetime): Data/hora da solicitação (auto)
        data_atualizacao (datetime): Última atualização (auto)
        status (str): Status atual - Pendente, Aprovada, Rejeitada ou Cancelada (choices, default='pendente')
        motivo_rejeicao (str): Motivo caso rejeitada (opcional)
    
    Methods:
        __str__: Retorna resumo da adoção
    
    Meta:
        verbose_name: 'Adoção'
        verbose_name_plural: 'Adoções'
        ordering: ['-data_solicitacao']
        unique_together: ('usuario', 'animal') - Previne duplicatas
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> animal = Animal.objects.get(nome='Rex')
        >>> adocao = Adocao.objects.create(usuario=usuario, animal=animal)
        >>> print(adocao)
        Adoção de Rex por Usuario object (1)
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='adocoes')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='adocoes')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    motivo_rejeicao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Adoção de {self.animal.nome} por {self.usuario}"
    
    class Meta:
        verbose_name = "Adoção"
        verbose_name_plural = "Adoções"
        ordering = ['-data_solicitacao']
        unique_together = ('usuario', 'animal')


# ===== ANIMAL PARA ADOÇÃO (Cadastrado por Usuários) =====
class AnimalParaAdocao(models.Model):
    """
    Animais para adoção cadastrados pelos próprios usuários.
    
    Permite que usuários comuns cadastrem animais para doação,
    passando por um processo de moderação antes de serem aprovados
    e publicados no sistema. Inclui dados completos do animal e
    informações de contato do doador.
    
    Attributes:
        usuario_doador (Usuario): Usuário que cadastrou o animal
        nome (str): Nome do animal (max 100)
        especie (str): Cachorro, Gato ou Outro (choices)
        porte (str): Pequeno, Médio ou Grande (choices)
        sexo (str): M, F ou N (choices, default='N')
        cor (str): Cor da pelagem (opcional)
        idade (str): Idade aproximada (opcional)
        descricao (str): Descrição detalhada do temperamento
        temperamento (str): Características comportamentais (opcional)
        historico_saude (str): Vacinas, castração, doenças (opcional)
        caracteristicas_especiais (str): Informações extras (opcional)
        estado (str): Estado (sigla UF)
        cidade (str): Cidade (max 100)
        endereco_completo (str): Endereço completo protegido (max 255)
        telefone (str): Telefone de contato (max 15)
        email (str): E-mail de contato
        imagem_principal (ImageField): Foto principal (upload_to='adocao/pendentes/')
        status (str): Pendente, Aprovado, Rejeitado ou Adotado (choices, default='pendente')
        motivo_rejeicao (str): Motivo se rejeitado (opcional)
        moderador_aprovacao (User): Moderador que aprovou (opcional)
        data_cadastro (datetime): Data de cadastro (auto)
        data_aprovacao (datetime): Data de aprovação (opcional)
        data_atualizacao (datetime): Última atualização (auto)
    
    Methods:
        __str__: Retorna nome, espécie e status do animal
    
    Meta:
        verbose_name: 'Animal para Adoção'
        verbose_name_plural: 'Animais para Adoção'
        ordering: ['-data_cadastro']
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='maria')
        >>> animal = AnimalParaAdocao.objects.create(
        ...     usuario_doador=usuario,
        ...     nome='Bella',
        ...     especie='gato',
        ...     porte='pequeno',
        ...     sexo='F',
        ...     cidade='Rio de Janeiro',
        ...     estado='RJ',
        ...     telefone='21988888888',
        ...     email='maria@email.com',
        ...     descricao='Gata dócil e carinhosa'
        ... )
        >>> print(animal)
        Bella (Gato) - Aguardando Aprovação
    """
    ESPECIE_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('outro', 'Outro'),
    ]
    
    PORTE_CHOICES = [
        ('pequeno', 'Pequeno (até 10kg)'),
        ('medio', 'Médio (10kg a 25kg)'),
        ('grande', 'Grande (acima de 25kg)'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
        ('N', 'Não informado'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Aguardando Aprovação'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('adotado', 'Adotado'),
    ]
    
    # Dados do pet
    usuario_doador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='animais_para_adocao', verbose_name='Usuário que cadastrou')
    nome = models.CharField(max_length=100, verbose_name='Nome do Animal')
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES, verbose_name='Espécie')
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, verbose_name='Porte')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='N', verbose_name='Sexo')
    cor = models.CharField(max_length=50, verbose_name='Cor', blank=True, null=True)
    idade = models.CharField(max_length=50, verbose_name='Idade', blank=True, null=True, help_text='Ex: 2 anos, 6 meses, filhote')
    descricao = models.TextField(verbose_name='Descrição do Animal', help_text='Descreva o temperamento, cuidados especiais, etc.')
    temperamento = models.TextField(blank=True, null=True, verbose_name='Temperamento', help_text='Ex: dócil, brincalhão, calmo')
    historico_saude = models.TextField(blank=True, null=True, verbose_name='Histórico de Saúde', help_text='Vacinas, castração, doenças, etc.')
    caracteristicas_especiais = models.TextField(blank=True, null=True, verbose_name='Características Especiais')
    
    # Localização (endereço oculto até aprovação de adoção)
    estado = models.CharField(max_length=2, verbose_name='Estado')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    endereco_completo = models.CharField(max_length=255, verbose_name='Endereço Completo', help_text='Será compartilhado apenas após aprovação da adoção')
    
    # Contatos do doador
    telefone = models.CharField(
        max_length=20, 
        verbose_name='Telefone para Contato',
        validators=[validar_telefone_brasileiro],
        help_text='Formato: (11) 99999-9999'
    )
    email = models.EmailField(
        verbose_name='E-mail para Contato',
        validators=[EmailValidator(message='Digite um e-mail válido')],
        help_text='E-mail válido para contato'
    )
    
    # Mídia
    imagem_principal = models.ImageField(
        upload_to='adocao/pendentes/', 
        blank=True, 
        null=True, 
        verbose_name='Foto Principal',
        validators=[
            validate_image_file,  # Validação completa: MIME, dimensões, tamanho
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
                message='Apenas imagens JPG, PNG ou WebP são permitidas'
            )
        ],
        help_text='Foto principal do animal (máximo 5MB, mínimo 200x200px)'
    )
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    motivo_rejeicao = models.TextField(blank=True, null=True, verbose_name='Motivo da Rejeição')
    moderador_aprovacao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='animais_aprovados', verbose_name='Moderador que Aprovou')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Aprovação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    def __str__(self):
        return f"{self.nome} ({self.get_especie_display()}) - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Animal para Adoção"
        verbose_name_plural = "Animais para Adoção"
        ordering = ['-data_cadastro']


# ===== SOLICITAÇÃO DE ADOÇÃO =====
class SolicitacaoAdocao(models.Model):
    """
    Solicitações de adoção para animais cadastrados por usuários.
    
    Gerencia os pedidos de adoção feitos para os AnimaisParaAdocao,
    conectando interessados com doadores. Passa por aprovação do
    doador e/ou moderador antes de liberar contatos.
    
    Attributes:
        animal (AnimalParaAdocao): Animal desejado (ForeignKey)
        usuario_interessado (Usuario): Usuário interessado em adotar (ForeignKey)
        mensagem (str): Mensagem do interessado (opcional)
        status (str): Pendente, Aprovada, Rejeitada ou Cancelada (choices, default='pendente')
        motivo_rejeicao (str): Motivo se rejeitada (opcional)
        moderador_aprovacao (User): Moderador responsável (opcional)
        notificado_doador (bool): Se doador foi notificado (default=False)
        notificado_interessado (bool): Se interessado foi notificado (default=False)
        data_solicitacao (datetime): Data da solicitação (auto)
        data_aprovacao (datetime): Data de aprovação (opcional)
        data_atualizacao (datetime): Última atualização (auto)
    
    Methods:
        __str__: Retorna resumo da solicitação
    
    Meta:
        verbose_name: 'Solicitação de Adoção'
        verbose_name_plural: 'Solicitações de Adoção'
        ordering: ['-data_solicitacao']
        unique_together: ('animal', 'usuario_interessado') - Previne duplicatas
    
    Example:
        >>> animal = AnimalParaAdocao.objects.get(nome='Bella')
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> solicitacao = SolicitacaoAdocao.objects.create(
        ...     animal=animal,
        ...     usuario_interessado=usuario,
        ...     mensagem='Tenho experiência com gatos e casa adequada'
        ... )
        >>> print(solicitacao)
        Solicitação de Usuario object (2) para adotar Bella
    """
    STATUS_CHOICES = [
        ('pendente', 'Aguardando Aprovação'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    ]
    
    animal = models.ForeignKey(AnimalParaAdocao, on_delete=models.CASCADE, related_name='solicitacoes', verbose_name='Animal')
    usuario_interessado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitacoes_adocao', verbose_name='Interessado em Adotar')
    mensagem = models.TextField(blank=True, null=True, verbose_name='Mensagem do Interessado', help_text='Conte um pouco sobre você e por que quer adotar')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    motivo_rejeicao = models.TextField(blank=True, null=True, verbose_name='Motivo da Rejeição')
    moderador_aprovacao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_aprovadas', verbose_name='Moderador que Aprovou')
    
    # Notificações
    notificado_doador = models.BooleanField(default=False, verbose_name='Doador Notificado')
    notificado_interessado = models.BooleanField(default=False, verbose_name='Interessado Notificado')
    
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Solicitação')
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Aprovação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    def __str__(self):
        return f"Solicitação de {self.usuario_interessado} para adotar {self.animal.nome}"
    
    class Meta:
        verbose_name = "Solicitação de Adoção"
        verbose_name_plural = "Solicitações de Adoção"
        ordering = ['-data_solicitacao']
        unique_together = ('animal', 'usuario_interessado')


# ===== NOTIFICAÇÃO =====
class Notificacao(models.Model):
    """
    Sistema de notificações do usuário.
    
    Centraliza todas as notificações enviadas aos usuários sobre
    ações relevantes no sistema (adoções, denúncias, contatos).
    Suporta diferentes tipos de notificação e links de ação.
    
    Attributes:
        usuario (Usuario): Usuário destinatário (ForeignKey)
        tipo (str): Tipo de notificação (choices - 8 opções disponíveis)
        titulo (str): Título da notificação (max 200)
        mensagem (str): Mensagem completa
        link (str): URL de ação (opcional, max 255)
        lida (bool): Se foi visualizada (default=False)
        data_criacao (datetime): Data de criação (auto)
        contato_telefone (str): Telefone de contato (opcional, max 15)
        contato_email (str): E-mail de contato (opcional)
        contato_endereco (str): Endereço completo (opcional, max 255)
    
    Methods:
        __str__: Retorna título e usuário
    
    Meta:
        verbose_name: 'Notificação'
        verbose_name_plural: 'Notificações'
        ordering: ['-data_criacao']
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> notificacao = Notificacao.objects.create(
        ...     usuario=usuario,
        ...     tipo='adocao_aprovada',
        ...     titulo='Sua adoção foi aprovada!',
        ...     mensagem='Parabéns! Você pode buscar o Rex na ONG.',
        ...     contato_telefone='1133334444'
        ... )
        >>> print(notificacao)
        Sua adoção foi aprovada! - Usuario object (1)
    """
    TIPO_CHOICES = [
        ('adocao_aprovada', 'Adoção Aprovada'),
        ('adocao_rejeitada', 'Adoção Rejeitada'),
        ('animal_aprovado', 'Animal Aprovado para Doação'),
        ('animal_rejeitado', 'Animal Rejeitado'),
        ('interesse_adocao', 'Novo Interesse em Adoção'),
        ('denuncia', 'Denúncia'),
        ('contato_recebido', 'Contato Recebido'),
        ('contato_respondido', 'Contato Respondido'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes', verbose_name='Usuário')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensagem = models.TextField(verbose_name='Mensagem')
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name='Link de Ação')
    lida = models.BooleanField(default=False, verbose_name='Lida')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data')
    
    # Dados de contato (para adoções aprovadas)
    contato_telefone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefone de Contato')
    contato_email = models.EmailField(blank=True, null=True, verbose_name='E-mail de Contato')
    contato_endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name='Endereço')
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario}"
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']


# ===== DENÚNCIA =====
class Denuncia(models.Model):
    """
    Denúncias de maus-tratos e abandono de animais.
    
    Permite que usuários reportem casos de abuso animal, abandono,
    acumulação e outras situações que requerem intervenção. Inclui
    sistema de moderação e acompanhamento de status.
    
    Attributes:
        usuario (Usuario): Usuário denunciante (ForeignKey, opcional)
        moderador (User): Moderador responsável (ForeignKey, opcional)
        titulo (str): Título da denúncia (max 200)
        categoria (str): Categoria - Maus-tratos, Abandono, Acumulação, Animal Perdido, Animal Ferido, Outros (choices)
        descricao (str): Descrição detalhada
        localizacao (str): Local do ocorrido (max 255)
        imagem (ImageField): Imagem principal (upload_to='denuncias/', opcional)
        video (FileField): Vídeo principal (upload_to='denuncias/videos/', opcional)
        status (str): Pendente, Aprovada, Em Andamento, Resolvida ou Rejeitada (choices, default='pendente')
        observacoes_moderador (str): Notas do moderador (opcional)
        data_criacao (datetime): Data de criação (auto)
        data_atualizacao (datetime): Última atualização (auto)
    
    Methods:
        __str__: Retorna título e status
    
    Meta:
        verbose_name: 'Denúncia'
        verbose_name_plural: 'Denúncias'
        ordering: ['-data_criacao']
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> denuncia = Denuncia.objects.create(
        ...     usuario=usuario,
        ...     titulo='Cachorro abandonado na Rua X',
        ...     categoria='abandono',
        ...     descricao='Animal sem comida há dias',
        ...     localizacao='Rua das Flores, 123 - Centro'
        ... )
        >>> print(denuncia)
        Cachorro abandonado na Rua X - Pendente
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('em_andamento', 'Em Andamento'),
        ('resolvida', 'Resolvida'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    CATEGORIA_CHOICES = [
        ('maus_tratos', 'Maus-tratos'),
        ('abandono', 'Abandono'),
        ('acumulacao', 'Acumulação de Animais'),
        ('animal_perdido', 'Animal Perdido'),
        ('animal_ferido', 'Animal Ferido'),
        ('outros', 'Outros'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='denuncias')
    moderador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='denuncias_moderadas', verbose_name='Moderador')
    titulo = models.CharField(
        max_length=200, 
        verbose_name='Título',
        help_text='Título resumido da denúncia (máximo 200 caracteres)'
    )
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='outros', verbose_name='Categoria')
    descricao = models.TextField(
        verbose_name='Descrição',
        max_length=3000,
        help_text='Descrição detalhada do caso (máximo 3000 caracteres)'
    )
    localizacao = models.CharField(
        max_length=255, 
        verbose_name='Localização',
        help_text='Endereço ou referência do local (máximo 255 caracteres)'
    )
    imagem = models.ImageField(
        upload_to='denuncias/', 
        blank=True, 
        null=True, 
        verbose_name='Imagem Principal',
        validators=[
            validate_image_file,  # Validação completa: MIME, dimensões, tamanho
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
                message='Apenas imagens JPG, PNG ou WebP são permitidas'
            )
        ],
        help_text='Imagem principal (máximo 5MB, mínimo 200x200px)'
    )
    video = models.FileField(
        upload_to='denuncias/videos/', 
        blank=True, 
        null=True, 
        verbose_name='Vídeo Principal',
        validators=[
            validate_video_file,  # Validação completa: MIME, tamanho (20MB)
            FileExtensionValidator(
                allowed_extensions=['mp4', 'avi', 'mov', 'wmv', 'webm'],
                message='Apenas vídeos MP4, AVI, MOV, WMV ou WebM são permitidos'
            )
        ],
        help_text='Vídeo principal (máximo 20MB)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes_moderador = models.TextField(
        blank=True, 
        null=True, 
        max_length=2000,
        verbose_name='Observações do Moderador',
        help_text='Observações internas da moderação (máximo 2000 caracteres)'
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"
        ordering = ['-data_criacao']


class DenunciaImagem(models.Model):
    """
    Imagens adicionais de denúncias.
    
    Permite anexar múltiplas imagens como evidências para uma denúncia,
    complementando a imagem principal.
    
    Attributes:
        denuncia (Denuncia): Denúncia relacionada (ForeignKey)
        imagem (ImageField): Arquivo de imagem (upload_to='denuncias/imagens/')
        data_criacao (datetime): Data de upload (auto)
    
    Methods:
        __str__: Retorna identificação da imagem
    
    Meta:
        verbose_name: 'Imagem da Denúncia'
        verbose_name_plural: 'Imagens da Denúncia'
        ordering: ['id']
    """
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='imagens_adicionais')
    imagem = models.ImageField(
        upload_to='denuncias/imagens/',
        validators=[validate_image_file]
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagem de denúncia #{self.denuncia.id}"

    class Meta:
        verbose_name = "Imagem da Denúncia"
        verbose_name_plural = "Imagens da Denúncia"
        ordering = ['id']


class DenunciaVideo(models.Model):
    """
    Vídeos adicionais de denúncias.
    
    Permite anexar múltiplos vídeos como evidências para uma denúncia,
    complementando o vídeo principal.
    
    Attributes:
        denuncia (Denuncia): Denúncia relacionada (ForeignKey)
        video (FileField): Arquivo de vídeo (upload_to='denuncias/videos/')
        data_criacao (datetime): Data de upload (auto)
    
    Methods:
        __str__: Retorna identificação do vídeo
    
    Meta:
        verbose_name: 'Vídeo da Denúncia'
        verbose_name_plural: 'Vídeos da Denúncia'
        ordering: ['id']
    """
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='videos_adicionais')
    video = models.FileField(
        upload_to='denuncias/videos/',
        validators=[validate_video_file]
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vídeo de denúncia #{self.denuncia.id}"

    class Meta:
        verbose_name = "Vídeo da Denúncia"
        verbose_name_plural = "Vídeos da Denúncia"
        ordering = ['id']


class DenunciaHistorico(models.Model):
    """
    Histórico de ações e mudanças de status das denúncias.
    
    Registra todas as ações realizadas em uma denúncia, criando
    um log de auditoria para rastreamento completo do processo.
    
    Attributes:
        denuncia (Denuncia): Denúncia relacionada (ForeignKey)
        tipo (str): Tipo de ação - Criação, Status, Comentário ou Atribuição (choices)
        usuario (User): Usuário que executou a ação (ForeignKey, opcional)
        status_anterior (str): Status antes da mudança (opcional)
        status_novo (str): Novo status (opcional)
        comentario (str): Comentário adicional (opcional)
        data_criacao (datetime): Data da ação (auto)
    
    Methods:
        __str__: Retorna tipo e ID da denúncia
    
    Meta:
        verbose_name: 'Histórico da Denúncia'
        verbose_name_plural: 'Histórico das Denúncias'
        ordering: ['-data_criacao']
    
    Example:
        >>> denuncia = Denuncia.objects.get(id=1)
        >>> historico = DenunciaHistorico.objects.create(
        ...     denuncia=denuncia,
        ...     tipo='status',
        ...     status_anterior='pendente',
        ...     status_novo='em_andamento'
        ... )
        >>> print(historico)
        Mudança de Status - Denúncia #1
    """
    TIPO_CHOICES = [
        ('criacao', 'Denúncia Criada'),
        ('status', 'Mudança de Status'),
        ('comentario', 'Comentário Adicionado'),
        ('atribuicao', 'Moderador Atribuído'),
    ]
    
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='historico')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Ação')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuário')
    status_anterior = models.CharField(max_length=20, blank=True, null=True, verbose_name='Status Anterior')
    status_novo = models.CharField(max_length=20, blank=True, null=True, verbose_name='Status Novo')
    comentario = models.TextField(blank=True, null=True, verbose_name='Comentário')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data')
    
    def __str__(self):
        return f"{self.get_tipo_display()} - Denúncia #{self.denuncia.id}"
    
    class Meta:
        verbose_name = "Histórico da Denúncia"
        verbose_name_plural = "Histórico das Denúncias"
        ordering = ['-data_criacao']


# ===== ANIMAL PERDIDO =====
class PetPerdido(models.Model):
    """
    Pets perdidos cadastrados pelos donos.
    
    Gerencia o cadastro de animais perdidos com geolocalização para
    exibição em mapa interativo. Permite matching automático com reportes
    de pets encontrados através de proximidade geográfica e características.
    
    Attributes:
        usuario (Usuario): Dono do pet (ForeignKey)
        nome (str): Nome do pet (max 100)
        especie (str): Cachorro, Gato ou Outro (choices)
        raca (str): Raça (opcional, max 100)
        cor (str): Cor da pelagem (max 100)
        porte (str): Pequeno, Médio ou Grande (choices)
        sexo (str): M, F ou N (choices, default='N')
        idade_aproximada (str): Idade (opcional, max 50)
        caracteristicas_distintivas (str): Manchas, cicatrizes, coleira
        descricao (str): Descrição detalhada do ocorrido
        data_perda (date): Data em que o pet se perdeu
        hora_perda (time): Hora aproximada (opcional)
        latitude (Decimal): Coordenada latitude (max_digits=9, decimal_places=6)
        longitude (Decimal): Coordenada longitude (max_digits=9, decimal_places=6)
        endereco (str): Endereço aproximado (max 255)
        bairro (str): Bairro (max 100)
        cidade (str): Cidade (max 100)
        estado (str): Estado (sigla UF)
        telefone_contato (str): Telefone (max 15)
        email_contato (str): E-mail
        whatsapp (str): WhatsApp (opcional, max 15)
        oferece_recompensa (bool): Se oferece recompensa (default=False)
        valor_recompensa (Decimal): Valor em R$ (opcional, max_digits=10, decimal_places=2)
        imagem_principal (ImageField): Foto principal (upload_to='pets_perdidos/')
        status (str): Perdido, Encontrado ou Cancelado (choices, default='perdido')
        ativo (bool): Se está ativo no mapa (default=True)
        visualizacoes (int): Contador de visualizações (default=0)
        data_criacao (datetime): Data de cadastro (auto)
        data_atualizacao (datetime): Última atualização (auto)
        data_encontrado (datetime): Data que foi encontrado (opcional)
    
    Methods:
        __str__: Retorna nome, espécie e localização
    
    Meta:
        verbose_name: 'Pet Perdido'
        verbose_name_plural: 'Pets Perdidos'
        ordering: ['-data_criacao']
        indexes: [status+ativo, cidade+estado, lat+long] - Para performance
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> pet = PetPerdido.objects.create(
        ...     usuario=usuario,
        ...     nome='Rex',
        ...     especie='cachorro',
        ...     cor='Marrom',
        ...     porte='medio',
        ...     sexo='M',
        ...     data_perda='2024-01-15',
        ...     latitude=-23.5505,
        ...     longitude=-46.6333,
        ...     cidade='São Paulo',
        ...     estado='SP',
        ...     telefone_contato='11999999999',
        ...     email_contato='joao@email.com'
        ... )
        >>> print(pet)
        Rex (Cachorro) - São Paulo/SP
    """
    STATUS_CHOICES = [
        ('perdido', 'Perdido'),
        ('encontrado', 'Encontrado'),
        ('cancelado', 'Cancelado'),
    ]
    
    ESPECIE_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('outro', 'Outro'),
    ]
    
    PORTE_CHOICES = [
        ('pequeno', 'Pequeno'),
        ('medio', 'Médio'),
        ('grande', 'Grande'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
        ('N', 'Não informado'),
    ]
    
    # Dados do usuário que perdeu o pet
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pets_perdidos', verbose_name='Dono do Pet')
    
    # Características do pet
    nome = models.CharField(max_length=100, verbose_name='Nome do Pet')
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES, verbose_name='Espécie')
    raca = models.CharField(max_length=100, blank=True, null=True, verbose_name='Raça')
    cor = models.CharField(max_length=100, verbose_name='Cor/Pelagem')
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, verbose_name='Porte')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='N', verbose_name='Sexo')
    idade_aproximada = models.CharField(max_length=50, blank=True, null=True, verbose_name='Idade Aproximada')
    caracteristicas_distintivas = models.TextField(verbose_name='Características Distintivas', help_text='Manchas, cicatrizes, coleira, etc.')
    
    # Informações da perda
    descricao = models.TextField(verbose_name='Descrição Detalhada', help_text='Conte o que aconteceu e onde o pet foi visto pela última vez')
    data_perda = models.DateField(verbose_name='Data da Perda')
    hora_perda = models.TimeField(blank=True, null=True, verbose_name='Hora Aproximada')
    
    # Localização (coordenadas para exibir no mapa)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude')
    endereco = models.CharField(max_length=255, verbose_name='Endereço Aproximado')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado')
    
    # Contato
    telefone_contato = models.CharField(max_length=15, verbose_name='Telefone para Contato')
    email_contato = models.EmailField(verbose_name='E-mail para Contato')
    whatsapp = models.CharField(max_length=15, blank=True, null=True, verbose_name='WhatsApp')
    
    # Recompensa
    oferece_recompensa = models.BooleanField(default=False, verbose_name='Oferece Recompensa')
    valor_recompensa = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Valor da Recompensa')
    
    # Mídia
    imagem_principal = models.ImageField(
        upload_to='pets_perdidos/',
        verbose_name='Foto Principal',
        validators=[
            validate_image_file,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
        help_text='Foto principal do pet perdido (máximo 5MB)'
    )
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='perdido', verbose_name='Status')
    ativo = models.BooleanField(default=True, verbose_name='Ativo no Mapa')
    visualizacoes = models.IntegerField(default=0, verbose_name='Visualizações')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    data_encontrado = models.DateTimeField(blank=True, null=True, verbose_name='Data que foi Encontrado')
    
    def __str__(self):
        return f"{self.nome} ({self.get_especie_display()}) - {self.cidade}/{self.estado}"
    
    class Meta:
        verbose_name = "Pet Perdido"
        verbose_name_plural = "Pets Perdidos"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['status', 'ativo']),
            models.Index(fields=['cidade', 'estado']),
            models.Index(fields=['latitude', 'longitude']),
        ]


class PetPerdidoFoto(models.Model):
    """
    Galeria de fotos adicionais de pets perdidos.
    
    Permite anexar múltiplas fotos do pet para auxiliar na identificação,
    mostrando diferentes ângulos e características.
    
    Attributes:
        pet_perdido (PetPerdido): Pet relacionado (ForeignKey)
        imagem (ImageField): Foto adicional (upload_to='pets_perdidos/fotos/')
        descricao (str): Descrição da foto (opcional, max 200)
        data_criacao (datetime): Data de upload (auto)
    
    Methods:
        __str__: Retorna identificação da foto
    
    Meta:
        verbose_name: 'Foto do Pet Perdido'
        verbose_name_plural: 'Fotos do Pet Perdido'
        ordering: ['id']
    """
    pet_perdido = models.ForeignKey(PetPerdido, on_delete=models.CASCADE, related_name='fotos_adicionais')
    imagem = models.ImageField(
        upload_to='pets_perdidos/fotos/',
        validators=[validate_image_file]
    )
    descricao = models.CharField(max_length=200, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.pet_perdido.nome}"

    class Meta:
        verbose_name = "Foto do Pet Perdido"
        verbose_name_plural = "Fotos do Pet Perdido"
        ordering = ['id']


class ReportePetEncontrado(models.Model):
    """
    Reportes de pets encontrados por usuários.
    
    Registra pets encontrados na rua por usuários, com sistema de matching
    automático que compara características e proximidade geográfica com
    pets perdidos. Aguarda análise para conectar com possíveis donos.
    
    Attributes:
        usuario (Usuario): Usuário que encontrou (ForeignKey, opcional)
        nome_pessoa (str): Nome de quem encontrou (max 100)
        telefone_contato (str): Telefone (max 15)
        email_contato (str): E-mail
        especie (str): Cachorro, Gato ou Outro (choices)
        cor (str): Cor da pelagem (max 100)
        porte (str): Pequeno, Médio ou Grande (choices)
        sexo (str): M, F ou N (choices, default='N')
        descricao (str): Descrição detalhada
        caracteristicas_distintivas (str): Coleira, manchas, cicatrizes (opcional)
        data_encontro (date): Data que encontrou
        hora_encontro (time): Hora aproximada (opcional)
        latitude (Decimal): Coordenada latitude (max_digits=9, decimal_places=6)
        longitude (Decimal): Coordenada longitude (max_digits=9, decimal_places=6)
        endereco (str): Endereço onde encontrou (max 255)
        bairro (str): Bairro (max 100)
        cidade (str): Cidade (max 100)
        estado (str): Estado (sigla UF)
        pet_com_usuario (bool): Se pet está com quem encontrou (default=True)
        local_temporario (str): Onde o pet está agora (opcional, max 255)
        imagem_principal (ImageField): Foto principal (upload_to='pets_encontrados/')
        possiveis_matches (ManyToMany): Pets perdidos similares (PetPerdido)
        pet_perdido_confirmado (ForeignKey): Match confirmado (PetPerdido, opcional)
        status (str): Pendente, Aprovado, Rejeitado ou Em Análise (choices, default='pendente')
        analisado_por (User): Administrador que analisou (opcional)
        observacoes_admin (str): Notas do admin (opcional)
        data_criacao (datetime): Data do reporte (auto)
        data_analise (datetime): Data da análise (opcional)
        data_atualizacao (datetime): Última atualização (auto)
        dono_notificado (bool): Se dono foi notificado (default=False)
    
    Methods:
        __str__: Retorna espécie, localização e status
    
    Meta:
        verbose_name: 'Reporte de Pet Encontrado'
        verbose_name_plural: 'Reportes de Pets Encontrados'
        ordering: ['-data_criacao']
        indexes: [status, cidade+estado, lat+long] - Para performance
    
    Example:
        >>> reporte = ReportePetEncontrado.objects.create(
        ...     nome_pessoa='Maria Silva',
        ...     telefone_contato='11988888888',
        ...     email_contato='maria@email.com',
        ...     especie='cachorro',
        ...     cor='Marrom',
        ...     porte='medio',
        ...     data_encontro='2024-01-16',
        ...     latitude=-23.5505,
        ...     longitude=-46.6333,
        ...     cidade='São Paulo',
        ...     estado='SP',
        ...     descricao='Cachorro marrom com coleira vermelha'
        ... )
        >>> print(reporte)
        Pet Cachorro encontrado em São Paulo/SP - Aguardando Análise
    """
    STATUS_CHOICES = [
        ('pendente', 'Aguardando Análise'),
        ('aprovado', 'Match Confirmado'),
        ('rejeitado', 'Rejeitado'),
        ('em_analise', 'Em Análise'),
    ]
    
    ESPECIE_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('outro', 'Outro'),
    ]
    
    PORTE_CHOICES = [
        ('pequeno', 'Pequeno'),
        ('medio', 'Médio'),
        ('grande', 'Grande'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
        ('N', 'Não sei informar'),
    ]
    
    # Dados de quem encontrou
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='pets_encontrados', verbose_name='Usuário que Encontrou')
    nome_pessoa = models.CharField(max_length=100, verbose_name='Nome de Quem Encontrou')
    telefone_contato = models.CharField(max_length=15, verbose_name='Telefone para Contato')
    email_contato = models.EmailField(verbose_name='E-mail para Contato')
    
    # Características do pet encontrado
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES, verbose_name='Espécie')
    cor = models.CharField(max_length=100, verbose_name='Cor/Pelagem')
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, verbose_name='Porte')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='N', verbose_name='Sexo')
    descricao = models.TextField(verbose_name='Descrição do Pet Encontrado', help_text='Descreva as características físicas e comportamento')
    caracteristicas_distintivas = models.TextField(blank=True, null=True, verbose_name='Características Distintivas', help_text='Coleira, manchas, cicatrizes, etc.')
    
    # Informações de onde foi encontrado
    data_encontro = models.DateField(verbose_name='Data que Encontrou')
    hora_encontro = models.TimeField(blank=True, null=True, verbose_name='Hora Aproximada')
    
    # Localização
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Latitude')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Longitude')
    endereco = models.CharField(max_length=255, verbose_name='Endereço onde Encontrou')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado')
    
    # Situação atual do pet
    pet_com_usuario = models.BooleanField(default=True, verbose_name='Pet está com você')
    local_temporario = models.CharField(max_length=255, blank=True, null=True, verbose_name='Local Temporário do Pet', help_text='Se o pet não está mais com você, onde ele está?')
    
    # Mídia
    imagem_principal = models.ImageField(
        upload_to='pets_encontrados/',
        verbose_name='Foto Principal',
        validators=[
            validate_image_file,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
        help_text='Foto principal do pet encontrado (máximo 5MB)'
    )
    
    # Possíveis matches automáticos
    possiveis_matches = models.ManyToManyField(PetPerdido, blank=True, related_name='reportes_relacionados', verbose_name='Possíveis Matches')
    pet_perdido_confirmado = models.ForeignKey(PetPerdido, on_delete=models.SET_NULL, null=True, blank=True, related_name='match_confirmado', verbose_name='Pet Perdido Confirmado')
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    analisado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes_analisados', verbose_name='Analisado por')
    observacoes_admin = models.TextField(blank=True, null=True, verbose_name='Observações do Administrador')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data do Reporte')
    data_analise = models.DateTimeField(blank=True, null=True, verbose_name='Data da Análise')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    # Notificações
    dono_notificado = models.BooleanField(default=False, verbose_name='Dono foi Notificado')
    
    def __str__(self):
        return f"Pet {self.get_especie_display()} encontrado em {self.cidade}/{self.estado} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Reporte de Pet Encontrado"
        verbose_name_plural = "Reportes de Pets Encontrados"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['cidade', 'estado']),
            models.Index(fields=['latitude', 'longitude']),
        ]


class ReportePetEncontradoFoto(models.Model):
    """
    Galeria de fotos adicionais de pets encontrados.
    
    Permite anexar múltiplas fotos do pet encontrado para auxiliar
    no matching com pets perdidos.
    
    Attributes:
        reporte (ReportePetEncontrado): Reporte relacionado (ForeignKey)
        imagem (ImageField): Foto adicional (upload_to='pets_encontrados/fotos/')
        descricao (str): Descrição da foto (opcional, max 200)
        data_criacao (datetime): Data de upload (auto)
    
    Methods:
        __str__: Retorna identificação da foto
    
    Meta:
        verbose_name: 'Foto do Pet Encontrado'
        verbose_name_plural: 'Fotos do Pet Encontrado'
        ordering: ['id']
    """
    reporte = models.ForeignKey(ReportePetEncontrado, on_delete=models.CASCADE, related_name='fotos_adicionais')
    imagem = models.ImageField(
        upload_to='pets_encontrados/fotos/',
        validators=[validate_image_file]
    )
    descricao = models.CharField(max_length=200, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto do reporte #{self.reporte.id}"

    class Meta:
        verbose_name = "Foto do Pet Encontrado"
        verbose_name_plural = "Fotos do Pet Encontrado"
        ordering = ['id']


# ===== DONATIVO =====
class Donativo(models.Model):
    """
    Registro de doações financeiras para a ONG.
    
    Armazena as doações feitas pelos usuários para apoiar o trabalho
    da ONG S.O.S Pets. Permite rastreamento de contribuições.
    
    Attributes:
        usuario (Usuario): Usuário doador (ForeignKey, opcional)
        valor (Decimal): Valor doado em R$ (min=0.01, max_digits=10, decimal_places=2)
        descricao (str): Descrição da doação (opcional, max 255)
        data_doacao (datetime): Data da doação (auto)
    
    Methods:
        __str__: Retorna valor e data formatados
    
    Meta:
        verbose_name: 'Donativo'
        verbose_name_plural: 'Donativos'
        ordering: ['-data_doacao']
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> donativo = Donativo.objects.create(
        ...     usuario=usuario,
        ...     valor=50.00,
        ...     descricao='Doação mensal'
        ... )
        >>> print(donativo)
        Doação de R$ 50.00 - 15/01/2024
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='donativos')
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    descricao = models.CharField(max_length=255, blank=True)
    data_doacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Doação de R$ {self.valor} - {self.data_doacao.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Donativo"
        verbose_name_plural = "Donativos"
        ordering = ['-data_doacao']


# ===== HISTÓRIA =====
class Historia(models.Model):
    """
    Histórias de sucesso de adoções.
    
    Permite que usuários compartilhem suas experiências positivas
    com adoções, inspirando outros a adotar animais.
    
    Attributes:
        usuario (Usuario): Usuário autor (ForeignKey)
        animal (Animal): Animal relacionado (ForeignKey, opcional)
        titulo (str): Título da história (max 200)
        conteudo (str): Texto completo da história
        imagem (ImageField): Imagem ilustrativa (upload_to='historias/')
        data_criacao (datetime): Data de publicação (auto)
        data_atualizacao (datetime): Última edição (auto)
    
    Methods:
        __str__: Retorna título
    
    Meta:
        verbose_name: 'História'
        verbose_name_plural: 'Histórias'
        ordering: ['-data_criacao']
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> animal = Animal.objects.get(nome='Rex')
        >>> historia = Historia.objects.create(
        ...     usuario=usuario,
        ...     animal=animal,
        ...     titulo='Minha vida mudou com o Rex',
        ...     conteudo='Adotei o Rex há 6 meses e ele transformou minha casa...',
        ...     imagem='historias/rex_joao.jpg'
        ... )
        >>> print(historia)
        Minha vida mudou com o Rex
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historias')
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name='historias')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    imagem = models.ImageField(
        upload_to='historias/',
        validators=[
            validate_image_file,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
        help_text='Imagem ilustrativa da história (máximo 5MB)'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = "História"
        verbose_name_plural = "Histórias"
        ordering = ['-data_criacao']


# ===== CONTATO =====
class Contato(models.Model):
    """
    Mensagens de contato enviadas pelos usuários.
    
    Gerencia as mensagens enviadas através do formulário de contato
    do site, com sistema de status e resposta integrado.
    
    Attributes:
        usuario (Usuario): Usuário remetente (ForeignKey, opcional)
        nome (str): Nome do remetente (max 100)
        email (str): E-mail para resposta
        assunto (str): Assunto da mensagem (max 200)
        mensagem (str): Conteúdo da mensagem
        status (str): Pendente, Em Atendimento, Respondido ou Resolvido (choices, default='pendente')
        data_criacao (datetime): Data de envio (auto)
        lido (bool): Se foi visualizada (default=False)
        data_leitura (datetime): Data de visualização (opcional)
        resposta (str): Resposta do administrador (opcional)
        data_resposta (datetime): Data da resposta (opcional)
        respondido_por (User): Admin que respondeu (ForeignKey, opcional)
        usuario_notificado (bool): Se usuário foi notificado da resposta (default=False)
    
    Methods:
        __str__: Retorna assunto e nome
    
    Meta:
        verbose_name: 'Contato'
        verbose_name_plural: 'Contatos'
        ordering: ['-data_criacao']
    
    Example:
        >>> usuario = Usuario.objects.get(user__username='joao')
        >>> contato = Contato.objects.create(
        ...     usuario=usuario,
        ...     nome='João Silva',
        ...     email='joao@email.com',
        ...     assunto='Dúvida sobre adoção',
        ...     mensagem='Gostaria de saber como funciona o processo de adoção'
        ... )
        >>> print(contato)
        Dúvida sobre adoção - João Silva
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_atendimento', 'Em Atendimento'),
        ('respondido', 'Respondido'),
        ('resolvido', 'Resolvido'),
    ]
    
    # Informações do usuário
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='contatos')
    nome = models.CharField(
        max_length=100,
        help_text='Nome completo (máximo 100 caracteres)'
    )
    email = models.EmailField(
        validators=[EmailValidator(message='Digite um e-mail válido')],
        help_text='E-mail válido para resposta'
    )
    
    # Conteúdo
    assunto = models.CharField(
        max_length=200,
        help_text='Assunto da mensagem (máximo 200 caracteres)'
    )
    mensagem = models.TextField(
        max_length=5000,
        help_text='Mensagem detalhada (máximo 5000 caracteres)'
    )
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    lido = models.BooleanField(default=False)
    data_leitura = models.DateTimeField(null=True, blank=True)
    
    # Resposta do admin
    resposta = models.TextField(blank=True, null=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    respondido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contatos_respondidos')
    
    # Notificações
    usuario_notificado = models.BooleanField(default=False)  # Se o usuário foi notificado da resposta
    
    def __str__(self):
        return f"{self.assunto} - {self.nome}"
    
    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ['-data_criacao']
