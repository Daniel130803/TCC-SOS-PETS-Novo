from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Animal, AnimalFoto

class AnimalFotoUploadView(APIView):
    """
    View para upload de fotos adicionais de animais.
    
    Endpoint:
        POST /api/animais/{id}/fotos/
    
    Permissions:
        IsAuthenticated (requer login)
    
    Request Body:
        imagem (file): Arquivo de imagem para upload (opcional se url fornecida)
        url (str): URL externa da imagem (opcional se imagem fornecida)
    
    Response:
        201: {'id': int, 'url': str} - Foto criada com sucesso
        400: Erro de validação (nenhum arquivo ou URL fornecido)
        404: Animal não encontrado
    
    Note:
        Aceita tanto upload direto de arquivo quanto URL externa
        Retorna URL absoluta da imagem criada
    
    Example:
        POST /api/animais/123/fotos/
        Content-Type: multipart/form-data
        imagem: [arquivo]
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        animal = get_object_or_404(Animal, pk=pk)
        file = request.FILES.get('imagem')
        url = request.data.get('url')
        if not file and not url:
            return Response({'detail': 'Envie um arquivo em "imagem" ou uma "url".'}, status=status.HTTP_400_BAD_REQUEST)
        if file:
            foto = AnimalFoto.objects.create(animal=animal, imagem=file)
            final_url = request.build_absolute_uri(foto.imagem.url)
        else:
            foto = AnimalFoto.objects.create(animal=animal, url=url)
            final_url = url
        return Response({'id': foto.id, 'url': final_url}, status=status.HTTP_201_CREATED)
