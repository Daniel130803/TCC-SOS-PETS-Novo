"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponseRedirect, Http404
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    # Documentação da API (OpenAPI/Swagger/Redoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', csrf_exempt(TemplateView.as_view(template_name='login.html')), name='login'),
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),
    path('login.html', csrf_exempt(TemplateView.as_view(template_name='login.html'))),  # compatibilidade
    # Rotas de páginas estáticas convertidas para Django TemplateView
    path('adocao/', TemplateView.as_view(template_name='adocao.html'), name='adocao'),
    path('arrecadacao/', TemplateView.as_view(template_name='arrecadacao.html'), name='arrecadacao'),
    path('denuncia/', TemplateView.as_view(template_name='denuncia.html'), name='denuncia'),
    path('animais-perdidos/', TemplateView.as_view(template_name='animais-perdidos.html'), name='animais_perdidos'),
    path('contato/', TemplateView.as_view(template_name='contato.html'), name='contato'),
    path('historias/', TemplateView.as_view(template_name='historias.html'), name='historias'),
    path('formulario-adocao/', TemplateView.as_view(template_name='formulario-adocao.html'), name='formulario_adocao'),
    path('perfil/', TemplateView.as_view(template_name='perfil.html'), name='perfil'),  # placeholder futura página de perfil
    path('admin-panel/', TemplateView.as_view(template_name='admin-panel.html'), name='admin_panel'),  # painel administrativo
    # Rota legacy: redireciona /<slug>.html -> /<slug>/ para compatibilidade com links antigos
    re_path(r'^(?P<slug>[\w-]+)\.html$', lambda request, slug: HttpResponseRedirect(f'/{slug}/') if slug in {
        'adocao','arrecadacao','denuncia','animais-perdidos','contato','historias','formulario-adocao','perfil'
    } else Http404()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
