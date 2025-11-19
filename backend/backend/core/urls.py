from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, AnimalViewSet, AdocaoViewSet, DenunciaViewSet
from .views_fotos import AnimalFotoUploadView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'animais', AnimalViewSet, basename='animal')
router.register(r'adocoes', AdocaoViewSet, basename='adocao')
router.register(r'denuncias', DenunciaViewSet, basename='denuncia')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='auth_me'),
    path('animais/<int:pk>/fotos/', AnimalFotoUploadView.as_view(), name='animal-fotos'),
    path('', include(router.urls)),
]