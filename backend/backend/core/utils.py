"""
Utilidades para o core da aplicação
Inclui funções de sanitização, normalização e helpers
"""

import bleach
import re
from typing import Optional


# ============================================
# CONFIGURAÇÃO DE SANITIZAÇÃO
# ============================================

# Tags HTML permitidas (whitelist mínima)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'b', 'i',
    'ul', 'ol', 'li', 'a'
]

# Atributos permitidos por tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}

# Protocolos permitidos em links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


# ============================================
# FUNÇÕES DE SANITIZAÇÃO
# ============================================

def sanitize_html(text: str, strip: bool = False) -> str:
    """
    Remove HTML perigoso mantendo apenas tags seguras
    
    Args:
        text: Texto a ser sanitizado
        strip: Se True, remove todas as tags HTML
        
    Returns:
        Texto sanitizado
        
    Examples:
        >>> sanitize_html('<script>alert("xss")</script><p>Texto</p>')
        '<p>Texto</p>'
        
        >>> sanitize_html('<p>Texto</p>', strip=True)
        'Texto'
    """
    if not text:
        return ''
    
    if strip:
        # Remove todas as tags HTML
        return bleach.clean(text, tags=[], strip=True)
    
    # Sanitiza mantendo apenas tags seguras
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )


def sanitize_text_field(text: str) -> str:
    """
    Sanitiza campos de texto removendo TODOS os HTML/scripts
    Ideal para campos como nome, título, descrição curta
    
    Args:
        text: Texto a ser sanitizado
        
    Returns:
        Texto limpo sem HTML
        
    Examples:
        >>> sanitize_text_field('<b>Nome</b>')
        'Nome'
        
        >>> sanitize_text_field('João & Maria')
        'João &amp; Maria'
    """
    if not text:
        return ''
    
    # Remove todas as tags HTML
    cleaned = bleach.clean(text, tags=[], strip=True)
    
    # Remove espaços extras
    cleaned = ' '.join(cleaned.split())
    
    # Limita caracteres especiais repetidos
    cleaned = re.sub(r'([!?.]){3,}', r'\1\1', cleaned)
    
    return cleaned.strip()


def sanitize_multiline_text(text: str) -> str:
    """
    Sanitiza texto multilinha (descrições, mensagens)
    Remove HTML perigoso mas preserva quebras de linha
    
    Args:
        text: Texto multilinha
        
    Returns:
        Texto sanitizado com quebras de linha preservadas
        
    Examples:
        >>> sanitize_multiline_text('Linha 1\\n<script>alert()</script>\\nLinha 2')
        'Linha 1\\n\\nLinha 2'
    """
    if not text:
        return ''
    
    # Remove HTML perigoso
    cleaned = bleach.clean(text, tags=['br'], strip=True)
    
    # Converte <br> em quebras de linha
    cleaned = cleaned.replace('<br>', '\n').replace('<br/>', '\n')
    
    # Remove múltiplas quebras de linha seguidas (máximo 2)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Remove espaços no início/fim de cada linha
    lines = [line.strip() for line in cleaned.split('\n')]
    cleaned = '\n'.join(lines)
    
    return cleaned.strip()


def sanitize_email(email: str) -> str:
    """
    Normaliza e sanitiza email
    
    Args:
        email: Email a ser sanitizado
        
    Returns:
        Email normalizado
        
    Examples:
        >>> sanitize_email('  USER@EXAMPLE.COM  ')
        'user@example.com'
    """
    if not email:
        return ''
    
    # Remove espaços e converte para minúsculo
    email = email.strip().lower()
    
    # Remove caracteres perigosos
    email = bleach.clean(email, tags=[], strip=True)
    
    # Validação básica de formato (será validada no serializer)
    return email


def sanitize_url(url: str) -> str:
    """
    Sanitiza URL removendo protocolos perigosos
    
    Args:
        url: URL a ser sanitizada
        
    Returns:
        URL sanitizada ou string vazia se inválida
        
    Examples:
        >>> sanitize_url('http://example.com')
        'http://example.com'
        
        >>> sanitize_url('javascript:alert(1)')
        ''
    """
    if not url:
        return ''
    
    url = url.strip()
    
    # Remove espaços internos
    url = url.replace(' ', '')
    
    # Verifica protocolos perigosos
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    url_lower = url.lower()
    
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return ''
    
    # Sanitiza a URL
    url = bleach.linkify(url, parse_email=False)
    
    return url


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres perigosos
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Nome sanitizado
        
    Examples:
        >>> sanitize_filename('../../../etc/passwd')
        'etc_passwd'
        
        >>> sanitize_filename('meu arquivo (1).jpg')
        'meu_arquivo_1.jpg'
    """
    if not filename:
        return ''
    
    # Remove path traversal
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    
    # Remove caracteres especiais perigosos
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Substitui espaços e parênteses
    filename = filename.replace(' ', '_')
    filename = filename.replace('(', '_')
    filename = filename.replace(')', '_')
    
    # Remove underscores múltiplos
    filename = re.sub(r'_{2,}', '_', filename)
    
    # Limita comprimento
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}.{ext}" if ext else name


def normalize_whitespace(text: str) -> str:
    """
    Normaliza espaços em branco
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto com espaços normalizados
        
    Examples:
        >>> normalize_whitespace('  texto   com    espaços  ')
        'texto com espaços'
    """
    if not text:
        return ''
    
    # Remove espaços extras
    text = ' '.join(text.split())
    
    return text.strip()


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitiza número de telefone mantendo apenas dígitos
    
    Args:
        phone: Número de telefone
        
    Returns:
        Apenas dígitos do telefone
        
    Examples:
        >>> sanitize_phone_number('(11) 98765-4321')
        '11987654321'
        
        >>> sanitize_phone_number('+55 11 9 8765-4321')
        '5511987654321'
    """
    if not phone:
        return ''
    
    # Remove tudo exceto dígitos
    return re.sub(r'\D', '', phone)


def sanitize_cpf(cpf: str) -> str:
    """
    Sanitiza CPF mantendo apenas dígitos
    
    Args:
        cpf: CPF formatado ou não
        
    Returns:
        CPF apenas com dígitos
        
    Examples:
        >>> sanitize_cpf('123.456.789-10')
        '12345678910'
    """
    if not cpf:
        return ''
    
    # Remove tudo exceto dígitos
    return re.sub(r'\D', '', cpf)


# ============================================
# HELPERS DE VALIDAÇÃO
# ============================================

def is_safe_text(text: str, max_length: Optional[int] = None) -> bool:
    """
    Verifica se texto é seguro (sem HTML/scripts)
    
    Args:
        text: Texto a verificar
        max_length: Comprimento máximo opcional
        
    Returns:
        True se texto é seguro
        
    Examples:
        >>> is_safe_text('Texto normal')
        True
        
        >>> is_safe_text('<script>alert()</script>')
        False
    """
    if not text:
        return True
    
    # Verifica comprimento
    if max_length and len(text) > max_length:
        return False
    
    # Verifica se há tags HTML
    if re.search(r'<[^>]+>', text):
        return False
    
    # Verifica scripts inline
    dangerous_patterns = [
        r'javascript:',
        r'on\w+\s*=',  # onclick, onload, etc
        r'<script',
        r'</script',
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower):
            return False
    
    return True


def strip_html_tags(text: str) -> str:
    """
    Remove todas as tags HTML de um texto
    
    Args:
        text: Texto com HTML
        
    Returns:
        Texto sem HTML
        
    Examples:
        >>> strip_html_tags('<p>Olá <b>mundo</b></p>')
        'Olá mundo'
    """
    if not text:
        return ''
    
    return bleach.clean(text, tags=[], strip=True)
