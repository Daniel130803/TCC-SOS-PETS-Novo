from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuração da aplicação Core do sistema S.O.S Pets.
    
    App principal que gerencia:
    - Catálogo de animais para adoção da ONG
    - Sistema de pets perdidos com geolocalização
    - Denúncias de maus-tratos
    - Solicitações de adoção
    - Notificações e contatos
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
