"""
Rate Limiting customizado para proteção contra spam e abuso
Implementa diferentes limites para diferentes endpoints
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# ============================================
# THROTTLES PARA USUÁRIOS ANÔNIMOS
# ============================================

class AnonBurstRateThrottle(AnonRateThrottle):
    """
    Limite agressivo para burst (rajada de requisições)
    Previne ataques rápidos de força bruta
    """
    scope = 'anon_burst'


class AnonSustainedRateThrottle(AnonRateThrottle):
    """
    Limite sustentado para uso normal
    Permite navegação normal mas previne abuso prolongado
    """
    scope = 'anon_sustained'


# ============================================
# THROTTLES PARA USUÁRIOS AUTENTICADOS
# ============================================

class UserBurstRateThrottle(UserRateThrottle):
    """
    Limite de burst para usuários logados
    Mais permissivo que anônimos, mas ainda protege
    """
    scope = 'user_burst'


class UserSustainedRateThrottle(UserRateThrottle):
    """
    Limite sustentado para usuários logados
    Permite uso intenso mas razoável
    """
    scope = 'user_sustained'


# ============================================
# THROTTLES PARA AÇÕES ESPECÍFICAS
# ============================================

class RegistroRateThrottle(AnonRateThrottle):
    """
    Limite muito restritivo para registro de usuários
    Previne criação em massa de contas falsas
    5 registros por hora por IP
    """
    scope = 'registro'


class LoginRateThrottle(AnonRateThrottle):
    """
    Limite para tentativas de login
    Previne ataques de força bruta em senhas
    10 tentativas por hora por IP
    """
    scope = 'login'


class ContatoRateThrottle(AnonRateThrottle):
    """
    Limite para formulário de contato
    Previne spam via formulário de contato
    5 mensagens por hora por IP
    """
    scope = 'contato'


class DenunciaRateThrottle(AnonRateThrottle):
    """
    Limite para denúncias
    Previne spam de denúncias falsas
    10 denúncias por hora por IP
    """
    scope = 'denuncia'


class AdocaoRateThrottle(AnonRateThrottle):
    """
    Limite para solicitações de adoção
    Previne spam de solicitações falsas
    5 solicitações por hora por IP
    """
    scope = 'adocao'


class PetPerdidoRateThrottle(AnonRateThrottle):
    """
    Limite para cadastro de pets perdidos
    Previne spam de cadastros falsos
    10 cadastros por hora por IP
    """
    scope = 'pet_perdido'


class UploadRateThrottle(AnonRateThrottle):
    """
    Limite para upload de arquivos (fotos/vídeos)
    Previne abuso de armazenamento
    20 uploads por hora por IP
    """
    scope = 'upload'


# ============================================
# THROTTLES PARA LEITURA (GET)
# ============================================

class ListRateThrottle(AnonRateThrottle):
    """
    Limite para listagem de recursos (GET em coleções)
    Previne scraping massivo
    100 listagens por hora por IP
    """
    scope = 'list'


class DetailRateThrottle(AnonRateThrottle):
    """
    Limite para leitura de detalhes (GET em instância única)
    Mais permissivo que listagens
    200 requisições por hora por IP
    """
    scope = 'detail'
