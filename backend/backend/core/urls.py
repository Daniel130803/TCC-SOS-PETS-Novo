from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, MeView, AnimalViewSet, AdocaoViewSet, DenunciaViewSet,
    AnimalParaAdocaoViewSet, SolicitacaoAdocaoViewSet, NotificacaoViewSet
)
from .views_fotos import AnimalFotoUploadView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'animais', AnimalViewSet, basename='animal')
router.register(r'adocoes', AdocaoViewSet, basename='adocao')
router.register(r'denuncias', DenunciaViewSet, basename='denuncia')
router.register(r'animais-adocao', AnimalParaAdocaoViewSet, basename='animal-adocao')
router.register(r'solicitacoes-adocao', SolicitacaoAdocaoViewSet, basename='solicitacao-adocao')
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='auth_me'),
    path('animais/<int:pk>/fotos/', AnimalFotoUploadView.as_view(), name='animal-fotos'),
    path('', include(router.urls)),
]