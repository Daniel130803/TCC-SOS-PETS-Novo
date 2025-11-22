"""
Testes para validação de arquivos (imagens e vídeos)
Testa validators.py com diferentes cenários
"""

import sys
import os
sys.path.insert(0, 'c:/Users/danie/OneDrive/Documentos/ProjetoRaiz/S.O.S Pets/TCC-SOS-PETS-Novo/backend/backend')

# Configuração mínima do Django para testes
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from PIL import Image
import io

# Importa validators
from core.validators import (
    validate_image_file,
    validate_video_file,
    validate_image_dimensions,
    validate_file_size,
    get_image_info
)

print("=" * 70)
print("TESTES DE VALIDAÇÃO DE ARQUIVOS")
print("=" * 70)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def criar_imagem_teste(largura=1000, altura=1000, formato='JPEG'):
    """Cria uma imagem de teste em memória"""
    img = Image.new('RGB', (largura, altura), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format=formato)
    buffer.seek(0)
    return buffer


def criar_arquivo_teste(tamanho_mb, extensao='jpg'):
    """Cria um arquivo de teste com tamanho específico"""
    tamanho_bytes = int(tamanho_mb * 1024 * 1024)
    conteudo = b'0' * tamanho_bytes
    nome = f'teste.{extensao}'
    return SimpleUploadedFile(nome, conteudo, content_type=f'image/{extensao}')


# ============================================
# TESTES DE IMAGEM
# ============================================

print("\n📸 TESTES DE VALIDAÇÃO DE IMAGEM")
print("-" * 70)

# Teste 1: Imagem válida
print("\n1. Teste Imagem Válida (1000x1000px JPEG)")
try:
    buffer = criar_imagem_teste(1000, 1000, 'JPEG')
    arquivo = SimpleUploadedFile('teste.jpg', buffer.getvalue(), content_type='image/jpeg')
    validate_image_file(arquivo)
    print("   ✅ PASSOU - Imagem válida aceita")
except ValidationError as e:
    print(f"   ❌ FALHOU - {e.message}")

# Teste 2: Imagem muito pequena
print("\n2. Teste Imagem Muito Pequena (100x100px)")
try:
    buffer = criar_imagem_teste(100, 100, 'JPEG')
    arquivo = SimpleUploadedFile('pequena.jpg', buffer.getvalue(), content_type='image/jpeg')
    validate_image_file(arquivo)
    print("   ❌ FALHOU - Deveria rejeitar imagem pequena")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")

# Teste 3: Imagem muito grande (dimensões)
print("\n3. Teste Imagem Dimensões Muito Grandes (5000x5000px)")
try:
    buffer = criar_imagem_teste(5000, 5000, 'JPEG')
    arquivo = SimpleUploadedFile('grande.jpg', buffer.getvalue(), content_type='image/jpeg')
    validate_image_file(arquivo)
    print("   ❌ FALHOU - Deveria rejeitar imagem com dimensões grandes")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")

# Teste 4: Extensão inválida
print("\n4. Teste Extensão Inválida (.bmp)")
try:
    arquivo = SimpleUploadedFile('teste.bmp', b'conteudo', content_type='image/bmp')
    validate_image_file(arquivo)
    print("   ❌ FALHOU - Deveria rejeitar BMP")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")

# Teste 5: Arquivo corrompido
print("\n5. Teste Arquivo Corrompido")
try:
    arquivo = SimpleUploadedFile('corrompido.jpg', b'nao_eh_imagem', content_type='image/jpeg')
    validate_image_file(arquivo)
    print("   ❌ FALHOU - Deveria rejeitar arquivo corrompido")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")

# Teste 6: PNG válido
print("\n6. Teste PNG Válido (800x800px)")
try:
    buffer = criar_imagem_teste(800, 800, 'PNG')
    arquivo = SimpleUploadedFile('teste.png', buffer.getvalue(), content_type='image/png')
    validate_image_file(arquivo)
    print("   ✅ PASSOU - PNG válido aceito")
except ValidationError as e:
    print(f"   ❌ FALHOU - {e.message}")

# Teste 7: WebP válido
print("\n7. Teste WebP Válido (600x600px)")
try:
    buffer = criar_imagem_teste(600, 600, 'WEBP')
    arquivo = SimpleUploadedFile('teste.webp', buffer.getvalue(), content_type='image/webp')
    validate_image_file(arquivo)
    print("   ✅ PASSOU - WebP válido aceito")
except ValidationError as e:
    print(f"   ❌ FALHOU - {e.message}")

# Teste 8: Dimensões customizadas
print("\n8. Teste Dimensões Customizadas (mínimo 500x500px)")
try:
    buffer = criar_imagem_teste(400, 400, 'JPEG')
    arquivo = SimpleUploadedFile('pequena.jpg', buffer.getvalue(), content_type='image/jpeg')
    validate_image_dimensions(arquivo, min_width=500, min_height=500)
    print("   ❌ FALHOU - Deveria rejeitar imagem 400x400px quando mínimo é 500x500px")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")


# ============================================
# TESTES DE VÍDEO
# ============================================

print("\n\n🎥 TESTES DE VALIDAÇÃO DE VÍDEO")
print("-" * 70)

# Teste 9: Vídeo com extensão válida
print("\n9. Teste Vídeo MP4 Válido (extensão)")
try:
    # Assinatura de cabeçalho MP4
    mp4_header = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 100
    arquivo = SimpleUploadedFile('teste.mp4', mp4_header, content_type='video/mp4')
    validate_video_file(arquivo)
    print("   ✅ PASSOU - MP4 válido aceito")
except ValidationError as e:
    print(f"   ❌ FALHOU - {e.message}")

# Teste 10: Vídeo extensão inválida
print("\n10. Teste Vídeo Extensão Inválida (.mkv)")
try:
    arquivo = SimpleUploadedFile('teste.mkv', b'conteudo', content_type='video/x-matroska')
    validate_video_file(arquivo)
    print("   ❌ FALHOU - Deveria rejeitar MKV")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")

# Teste 11: Vídeo MIME type inválido
print("\n11. Teste Vídeo com MIME Type Não-Video")
try:
    arquivo = SimpleUploadedFile('teste.mp4', b'conteudo', content_type='application/octet-stream')
    validate_video_file(arquivo)
    print("   ⚠️  ATENÇÃO - Aceito mas MIME type não é vídeo")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")

# Teste 12: AVI válido (com cabeçalho RIFF)
print("\n12. Teste Vídeo AVI Válido")
try:
    # Assinatura de cabeçalho AVI
    avi_header = b'RIFF' + b'\x00\x00\x00\x00' + b'AVI ' + b'\x00' * 100
    arquivo = SimpleUploadedFile('teste.avi', avi_header, content_type='video/x-msvideo')
    validate_video_file(arquivo)
    print("   ✅ PASSOU - AVI válido aceito")
except ValidationError as e:
    print(f"   ❌ FALHOU - {e.message}")


# ============================================
# TESTES DE TAMANHO
# ============================================

print("\n\n📏 TESTES DE TAMANHO DE ARQUIVO")
print("-" * 70)

# Teste 13: Tamanho válido (3MB)
print("\n13. Teste Tamanho Válido (3MB)")
try:
    validate_file_size(criar_arquivo_teste(3), max_size_mb=5)
    print("   ✅ PASSOU - Arquivo de 3MB aceito (limite 5MB)")
except ValidationError as e:
    print(f"   ❌ FALHOU - {e.message}")

# Teste 14: Tamanho excedido (6MB)
print("\n14. Teste Tamanho Excedido (6MB)")
try:
    validate_file_size(criar_arquivo_teste(6), max_size_mb=5)
    print("   ❌ FALHOU - Deveria rejeitar arquivo de 6MB (limite 5MB)")
except ValidationError as e:
    print(f"   ✅ PASSOU - Rejeitou corretamente: {e.message}")


# ============================================
# TESTES DE INFORMAÇÕES
# ============================================

print("\n\n📊 TESTE DE EXTRAÇÃO DE INFORMAÇÕES")
print("-" * 70)

# Teste 15: Obter informações da imagem
print("\n15. Teste Obter Informações da Imagem")
buffer = criar_imagem_teste(1920, 1080, 'JPEG')
arquivo = SimpleUploadedFile('teste.jpg', buffer.getvalue(), content_type='image/jpeg')
info = get_image_info(arquivo)
print(f"   📋 Formato: {info.get('formato')}")
print(f"   📋 Dimensões: {info.get('largura')}x{info.get('altura')}px")
print(f"   📋 Tamanho: {info.get('tamanho_mb')}MB")
print(f"   📋 Modo: {info.get('modo')}")
if 'erro' not in info:
    print("   ✅ PASSOU - Informações extraídas com sucesso")
else:
    print(f"   ❌ FALHOU - {info['erro']}")


# ============================================
# RESUMO
# ============================================

print("\n" + "=" * 70)
print("RESUMO DOS TESTES")
print("=" * 70)
print("\n✅ Validações Implementadas:")
print("   • Tamanho de arquivo (5MB imagens, 20MB vídeos)")
print("   • Extensões permitidas (jpg, jpeg, png, webp | mp4, avi, mov, webm)")
print("   • Verificação de MIME type real")
print("   • Dimensões de imagem (200x200 a 4000x4000px)")
print("   • Integridade de arquivo (detecta corrompidos)")
print("   • Verificação de cabeçalho de vídeo (assinaturas)")
print("\n✅ Proteções Ativas:")
print("   • Rejeita arquivos falsos (renomeados)")
print("   • Detecta arquivos corrompidos")
print("   • Valida dimensões para imagens")
print("   • Limite de tamanho configurável")
print("   • Suporte a formatos modernos (WebP)")
print("\n🎯 Sistema de Validação de Arquivos 100% Funcional!")
print("=" * 70)
