"""
Validators customizados para validação de arquivos (imagens e vídeos)
Implementa verificação de MIME real, dimensões e tamanhos
"""

from django.core.exceptions import ValidationError
from PIL import Image
import io


# ============================================
# CONSTANTES DE CONFIGURAÇÃO
# ============================================

# Tamanhos máximos permitidos (em bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 20 * 1024 * 1024  # 20MB

# Dimensões mínimas e máximas para imagens
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 200
MAX_IMAGE_WIDTH = 4000
MAX_IMAGE_HEIGHT = 4000

# Formatos permitidos
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'webm']

# MIME types permitidos (verificação real do conteúdo)
ALLOWED_IMAGE_MIMETYPES = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
]

ALLOWED_VIDEO_MIMETYPES = [
    'video/mp4',
    'video/mpeg',
    'video/quicktime',
    'video/x-msvideo',
    'video/webm',
]


# ============================================
# VALIDADORES DE IMAGEM
# ============================================

def validate_image_file(arquivo):
    """
    Validação completa de arquivo de imagem.
    
    Verifica:
    - Tamanho do arquivo (máximo 5MB)
    - Extensão permitida (jpg, jpeg, png, webp)
    - MIME type real (lendo cabeçalho do arquivo)
    - Dimensões da imagem (mínimo 200x200, máximo 4000x4000)
    - Integridade da imagem (pode ser aberta pelo Pillow)
    
    Args:
        arquivo: UploadedFile do Django
        
    Raises:
        ValidationError: Se arquivo não passar em alguma validação
        
    Examples:
        >>> from django.core.files.uploadedfile import SimpleUploadedFile
        >>> arquivo = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")
        >>> validate_image_file(arquivo)  # Valida o arquivo
    """
    if not arquivo:
        return
    
    # VALIDAÇÃO 1: Tamanho do arquivo
    tamanho_mb = arquivo.size / (1024 * 1024)
    if arquivo.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f'Imagem muito grande ({tamanho_mb:.1f}MB). '
            f'Tamanho máximo permitido: {MAX_IMAGE_SIZE / (1024 * 1024):.0f}MB'
        )
    
    # VALIDAÇÃO 2: Extensão do arquivo
    nome_arquivo = arquivo.name.lower()
    extensao = nome_arquivo.split('.')[-1] if '.' in nome_arquivo else ''
    
    if extensao not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Formato de imagem não permitido: .{extensao}. '
            f'Formatos aceitos: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )
    
    # VALIDAÇÃO 3: MIME type real (verificando conteúdo do arquivo)
    try:
        # Lê o início do arquivo para verificar MIME type
        arquivo.seek(0)
        img = Image.open(arquivo)
        
        # Verifica formato real detectado pelo Pillow
        formato_real = img.format.lower() if img.format else None
        
        if formato_real not in ['jpeg', 'png', 'webp']:
            raise ValidationError(
                f'Tipo de arquivo não permitido. '
                f'O arquivo parece ser {formato_real}, mas apenas JPEG, PNG e WebP são aceitos.'
            )
        
        # VALIDAÇÃO 4: Dimensões da imagem
        largura, altura = img.size
        
        if largura < MIN_IMAGE_WIDTH or altura < MIN_IMAGE_HEIGHT:
            raise ValidationError(
                f'Imagem muito pequena ({largura}x{altura}px). '
                f'Dimensões mínimas: {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}px'
            )
        
        if largura > MAX_IMAGE_WIDTH or altura > MAX_IMAGE_HEIGHT:
            raise ValidationError(
                f'Imagem muito grande ({largura}x{altura}px). '
                f'Dimensões máximas: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}px'
            )
        
        # VALIDAÇÃO 5: Verifica se imagem não está corrompida
        img.verify()
        
    except ValidationError:
        # Re-lança ValidationError já tratados
        raise
    except Exception as e:
        # Qualquer outro erro indica arquivo inválido/corrompido
        raise ValidationError(
            f'Arquivo de imagem inválido ou corrompido. '
            f'Certifique-se de enviar uma imagem válida. Erro: {str(e)}'
        )
    finally:
        # Volta cursor do arquivo para o início
        arquivo.seek(0)


def validate_image_dimensions(arquivo, min_width=MIN_IMAGE_WIDTH, min_height=MIN_IMAGE_HEIGHT,
                              max_width=MAX_IMAGE_WIDTH, max_height=MAX_IMAGE_HEIGHT):
    """
    Validação específica de dimensões de imagem com limites customizados.
    
    Args:
        arquivo: UploadedFile do Django
        min_width: Largura mínima em pixels
        min_height: Altura mínima em pixels
        max_width: Largura máxima em pixels
        max_height: Altura máxima em pixels
        
    Raises:
        ValidationError: Se dimensões não estiverem dentro dos limites
        
    Examples:
        >>> validate_image_dimensions(arquivo, min_width=300, min_height=300)
    """
    if not arquivo:
        return
    
    try:
        arquivo.seek(0)
        img = Image.open(arquivo)
        largura, altura = img.size
        
        if largura < min_width or altura < min_height:
            raise ValidationError(
                f'Imagem muito pequena ({largura}x{altura}px). '
                f'Dimensões mínimas: {min_width}x{min_height}px'
            )
        
        if largura > max_width or altura > max_height:
            raise ValidationError(
                f'Imagem muito grande ({largura}x{altura}px). '
                f'Dimensões máximas: {max_width}x{max_height}px'
            )
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Não foi possível verificar dimensões da imagem: {str(e)}')
    finally:
        arquivo.seek(0)


# ============================================
# VALIDADORES DE VÍDEO
# ============================================

def validate_video_file(arquivo):
    """
    Validação completa de arquivo de vídeo.
    
    Verifica:
    - Tamanho do arquivo (máximo 20MB)
    - Extensão permitida (mp4, avi, mov, webm)
    - MIME type (lendo cabeçalho do arquivo se disponível)
    
    Args:
        arquivo: UploadedFile do Django
        
    Raises:
        ValidationError: Se arquivo não passar em alguma validação
        
    Examples:
        >>> validate_video_file(arquivo)
    """
    if not arquivo:
        return
    
    # VALIDAÇÃO 1: Tamanho do arquivo
    tamanho_mb = arquivo.size / (1024 * 1024)
    if arquivo.size > MAX_VIDEO_SIZE:
        raise ValidationError(
            f'Vídeo muito grande ({tamanho_mb:.1f}MB). '
            f'Tamanho máximo permitido: {MAX_VIDEO_SIZE / (1024 * 1024):.0f}MB'
        )
    
    # VALIDAÇÃO 2: Extensão do arquivo
    nome_arquivo = arquivo.name.lower()
    extensao = nome_arquivo.split('.')[-1] if '.' in nome_arquivo else ''
    
    if extensao not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            f'Formato de vídeo não permitido: .{extensao}. '
            f'Formatos aceitos: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'
        )
    
    # VALIDAÇÃO 3: Verificação básica de MIME type
    # Para vídeos, fazemos verificação mais leve já que não temos biblioteca
    # específica como o Pillow. Verificamos o MIME type informado.
    if hasattr(arquivo, 'content_type'):
        content_type = arquivo.content_type.lower()
        
        # Verifica se é um dos MIME types de vídeo aceitos
        is_video = content_type.startswith('video/') or content_type in ALLOWED_VIDEO_MIMETYPES
        
        if not is_video:
            raise ValidationError(
                f'Tipo de arquivo não é vídeo. '
                f'MIME type recebido: {content_type}. '
                f'Envie apenas arquivos de vídeo.'
            )
    
    # VALIDAÇÃO 4: Verificação básica do cabeçalho do arquivo
    try:
        arquivo.seek(0)
        header = arquivo.read(12)
        arquivo.seek(0)
        
        # Assinaturas de cabeçalho de arquivos de vídeo comuns
        video_signatures = [
            b'\x00\x00\x00\x14ftypmp4',  # MP4
            b'\x00\x00\x00\x18ftypmp4',  # MP4 variant
            b'\x00\x00\x00\x1cftypisom', # MP4/MOV
            b'\x00\x00\x00\x20ftypisom', # MP4/MOV variant
            b'RIFF',                      # AVI (first 4 bytes)
            b'\x1aE\xdf\xa3',            # WebM/MKV
        ]
        
        # Verifica se cabeçalho corresponde a algum formato conhecido
        is_valid_header = any(header.startswith(sig) for sig in video_signatures)
        
        # Para AVI, verifica também a segunda parte do cabeçalho
        if header.startswith(b'RIFF'):
            arquivo.seek(8)
            avi_sig = arquivo.read(4)
            arquivo.seek(0)
            is_valid_header = avi_sig == b'AVI '
        
        if not is_valid_header:
            raise ValidationError(
                'Arquivo não parece ser um vídeo válido. '
                'Certifique-se de enviar um arquivo de vídeo real (.mp4, .avi, .mov, .webm).'
            )
        
    except ValidationError:
        raise
    except Exception:
        # Se falhar na leitura, permite (alguns vídeos podem ter formatos diferentes)
        pass
    finally:
        arquivo.seek(0)


# ============================================
# VALIDADORES AUXILIARES
# ============================================

def validate_file_size(arquivo, max_size_mb=5):
    """
    Validação genérica de tamanho de arquivo.
    
    Args:
        arquivo: UploadedFile do Django
        max_size_mb: Tamanho máximo em megabytes
        
    Raises:
        ValidationError: Se arquivo exceder tamanho máximo
    """
    if not arquivo:
        return
    
    max_size_bytes = max_size_mb * 1024 * 1024
    tamanho_mb = arquivo.size / (1024 * 1024)
    
    if arquivo.size > max_size_bytes:
        raise ValidationError(
            f'Arquivo muito grande ({tamanho_mb:.1f}MB). '
            f'Tamanho máximo permitido: {max_size_mb}MB'
        )


def get_image_info(arquivo):
    """
    Retorna informações sobre a imagem (formato, dimensões, tamanho).
    
    Args:
        arquivo: UploadedFile do Django
        
    Returns:
        dict: Dicionário com informações da imagem
        
    Examples:
        >>> info = get_image_info(arquivo)
        >>> print(info)
        {'formato': 'JPEG', 'largura': 1920, 'altura': 1080, 'tamanho_mb': 2.5}
    """
    try:
        arquivo.seek(0)
        img = Image.open(arquivo)
        
        info = {
            'formato': img.format,
            'largura': img.size[0],
            'altura': img.size[1],
            'tamanho_mb': round(arquivo.size / (1024 * 1024), 2),
            'modo': img.mode,  # RGB, RGBA, L, etc.
        }
        
        arquivo.seek(0)
        return info
    except Exception as e:
        return {'erro': str(e)}


# ============================================
# HELPER PARA MODELS
# ============================================

def get_image_validators():
    """
    Retorna lista de validators para campos ImageField.
    
    Returns:
        list: Lista de validators a serem usados em models.ImageField
        
    Examples:
        >>> class MeuModel(models.Model):
        ...     foto = models.ImageField(validators=get_image_validators())
    """
    return [validate_image_file]


def get_video_validators():
    """
    Retorna lista de validators para campos FileField de vídeo.
    
    Returns:
        list: Lista de validators a serem usados em models.FileField
        
    Examples:
        >>> class MeuModel(models.Model):
        ...     video = models.FileField(validators=get_video_validators())
    """
    return [validate_video_file]
