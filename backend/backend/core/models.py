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
class AnimalPerdido(models.Model):
    STATUS_CHOICES = [
        ('perdido', 'Perdido'),
        ('encontrado', 'Encontrado'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='animais_perdidos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    localizacao = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to='perdidos/')
    data_perdido = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='perdido')
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Animal Perdido"
        verbose_name_plural = "Animais Perdidos"
        ordering = ['-data_criacao']


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
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    lido = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.assunto} - {self.email}"
    
    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ['-data_criacao']
