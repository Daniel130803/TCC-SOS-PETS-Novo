from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# ===== USUÁRIO (Estendido) =====
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


# ===== ANIMAL =====
class Animal(models.Model):
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
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, blank=True, null=True)
    raca = models.CharField(max_length=100, blank=True)
    idade_anos = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    descricao = models.TextField(blank=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    imagem = models.ImageField(upload_to='animais/', blank=True, null=True)
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
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='fotos')
    url = models.URLField(blank=True, null=True)
    imagem = models.ImageField(upload_to='animais/fotos/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.animal.nome}"

    class Meta:
        verbose_name = "Foto do Animal"
        verbose_name_plural = "Fotos do Animal"
        ordering = ['id']


class AnimalVideo(models.Model):
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
    telefone = models.CharField(max_length=15, verbose_name='Telefone para Contato')
    email = models.EmailField(verbose_name='E-mail para Contato')
    
    # Mídia
    imagem_principal = models.ImageField(upload_to='adocao/pendentes/', blank=True, null=True, verbose_name='Foto Principal')
    
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
    titulo = models.CharField(max_length=200, verbose_name='Título')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='outros', verbose_name='Categoria')
    descricao = models.TextField(verbose_name='Descrição')
    localizacao = models.CharField(max_length=255, verbose_name='Localização')
    imagem = models.ImageField(upload_to='denuncias/', blank=True, null=True, verbose_name='Imagem Principal')
    video = models.FileField(upload_to='denuncias/videos/', blank=True, null=True, verbose_name='Vídeo Principal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes_moderador = models.TextField(blank=True, null=True, verbose_name='Observações do Moderador')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    
    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"
        ordering = ['-data_criacao']


class DenunciaImagem(models.Model):
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='imagens_adicionais')
    imagem = models.ImageField(upload_to='denuncias/imagens/')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagem de denúncia #{self.denuncia.id}"

    class Meta:
        verbose_name = "Imagem da Denúncia"
        verbose_name_plural = "Imagens da Denúncia"
        ordering = ['id']


class DenunciaVideo(models.Model):
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='videos_adicionais')
    video = models.FileField(upload_to='denuncias/videos/')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vídeo de denúncia #{self.denuncia.id}"

    class Meta:
        verbose_name = "Vídeo da Denúncia"
        verbose_name_plural = "Vídeos da Denúncia"
        ordering = ['id']


class DenunciaHistorico(models.Model):
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
    """Pet que foi perdido pelo dono e está sendo procurado"""
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
    imagem_principal = models.ImageField(upload_to='pets_perdidos/', verbose_name='Foto Principal')
    
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
    """Fotos adicionais do pet perdido"""
    pet_perdido = models.ForeignKey(PetPerdido, on_delete=models.CASCADE, related_name='fotos_adicionais')
    imagem = models.ImageField(upload_to='pets_perdidos/fotos/')
    descricao = models.CharField(max_length=200, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.pet_perdido.nome}"

    class Meta:
        verbose_name = "Foto do Pet Perdido"
        verbose_name_plural = "Fotos do Pet Perdido"
        ordering = ['id']


class ReportePetEncontrado(models.Model):
    """Reporte de alguém que encontrou um pet - aguarda aprovação para conectar com dono"""
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
    imagem_principal = models.ImageField(upload_to='pets_encontrados/', verbose_name='Foto Principal')
    
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
    """Fotos adicionais do pet encontrado"""
    reporte = models.ForeignKey(ReportePetEncontrado, on_delete=models.CASCADE, related_name='fotos_adicionais')
    imagem = models.ImageField(upload_to='pets_encontrados/fotos/')
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
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historias')
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name='historias')
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    imagem = models.ImageField(upload_to='historias/')
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
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_atendimento', 'Em Atendimento'),
        ('respondido', 'Respondido'),
        ('resolvido', 'Resolvido'),
    ]
    
    # Informações do usuário
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, related_name='contatos')
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    
    # Conteúdo
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    
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
