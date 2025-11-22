"""
Testes unitários completos para o sistema S.O.S Pets.

Cobre todas as funcionalidades principais:
- Models (validações, métodos, relacionamentos)
- Serializers (validações, criação, atualização)
- Views/APIs (endpoints, permissões, filtros)
- Sistema de Pets Perdidos (matching automático, geolocalização)
- Sistema de Adoção (solicitações, aprovações)
- Sistema de Denúncias (moderação, histórico)
"""
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from .models import (
    Usuario, Animal, AnimalFoto, AnimalVideo,
    AnimalParaAdocao, SolicitacaoAdocao,
    PetPerdido, PetPerdidoFoto, ReportePetEncontrado, ReportePetEncontradoFoto,
    Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico,
    Notificacao, Contato
)
from .serializers import (
    AnimalSerializer, RegisterSerializer, UserMeSerializer,
    AnimalParaAdocaoSerializer, SolicitacaoAdocaoSerializer,
    PetPerdidoSerializer, ReportePetEncontradoSerializer,
    DenunciaSerializer
)


# ===== TESTES DE MODELS =====

class UsuarioModelTest(TestCase):
    """Testes para o modelo Usuario (perfil estendido)."""
    
    def setUp(self) -> None:
        """Configura dados de teste."""
        self.user = User.objects.create_user(
            username='joao',
            email='joao@email.com',
            password='senha123',
            first_name='João Silva'
        )
    
    def test_criar_usuario_completo(self) -> None:
        """Testa criação de usuário com todos os campos."""
        usuario = Usuario.objects.create(
            user=self.user,
            telefone='11999999999',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP'
        )
        
        self.assertEqual(usuario.user, self.user)
        self.assertEqual(usuario.telefone, '11999999999')
        self.assertEqual(usuario.cidade, 'São Paulo')
        self.assertEqual(usuario.estado, 'SP')
        self.assertIsNotNone(usuario.data_criacao)
    
    def test_usuario_str_retorna_nome_completo(self) -> None:
        """Testa método __str__ com nome completo."""
        usuario = Usuario.objects.create(user=self.user)
        self.assertEqual(str(usuario), 'João Silva')
    
    def test_usuario_str_retorna_username_sem_nome(self) -> None:
        """Testa método __str__ quando não tem nome completo."""
        user = User.objects.create_user(username='maria', password='senha123')
        usuario = Usuario.objects.create(user=user)
        self.assertEqual(str(usuario), 'maria')


class AnimalModelTest(TestCase):
    """Testes para o modelo Animal (catálogo da ONG)."""
    
    def test_criar_animal_campos_obrigatorios(self) -> None:
        """Testa criação de animal com campos obrigatórios."""
        animal = Animal.objects.create(
            nome='Rex',
            tipo='cachorro',
            porte='medio',
            sexo='macho',
            idade_anos=3,
            descricao='Cachorro dócil',
            cidade='São Paulo',
            estado='SP'
        )
        
        self.assertEqual(animal.nome, 'Rex')
        self.assertEqual(animal.tipo, 'cachorro')
        self.assertEqual(animal.status, 'disponivel')  # default
        self.assertIsNotNone(animal.data_criacao)  # Campo correto é data_criacao
    
    def test_animal_str(self) -> None:
        """Testa representação em string do animal."""
        animal = Animal.objects.create(
            nome='Mia',
            tipo='gato',
            porte='pequeno',
            sexo='femea',
            cidade='Rio de Janeiro',
            estado='RJ'
        )
        self.assertIn('Mia', str(animal))
        self.assertIn('Gato', str(animal))
    
    def test_animal_choices_validos(self) -> None:
        """Testa que choices de tipo são válidos."""
        animal_cachorro = Animal.objects.create(
            nome='Dog', tipo='cachorro', porte='pequeno',
            sexo='macho', cidade='SP', estado='SP'
        )
        animal_gato = Animal.objects.create(
            nome='Cat', tipo='gato', porte='pequeno',
            sexo='femea', cidade='SP', estado='SP'
        )
        
        self.assertEqual(animal_cachorro.tipo, 'cachorro')
        self.assertEqual(animal_gato.tipo, 'gato')


class PetPerdidoModelTest(TestCase):
    """Testes para o modelo PetPerdido."""
    
    def setUp(self) -> None:
        """Configura usuário para testes."""
        user = User.objects.create_user(username='teste', password='senha123')
        self.usuario = Usuario.objects.create(user=user, telefone='11999999999')
    
    def test_criar_pet_perdido(self) -> None:
        """Testa criação de pet perdido com geolocalização."""
        pet = PetPerdido.objects.create(
            usuario=self.usuario,
            nome='Totó',
            especie='cachorro',
            porte='pequeno',
            cor='marrom',
            descricao='Cachorro pequeno e amigável',
            data_perda=timezone.now().date(),
            bairro='Centro',
            cidade='São Paulo',
            estado='SP',
            latitude=Decimal('-23.5505'),
            longitude=Decimal('-46.6333')
        )
        
        self.assertEqual(pet.nome, 'Totó')
        self.assertEqual(pet.status, 'perdido')  # default
        self.assertTrue(pet.ativo)  # default True
        self.assertEqual(pet.visualizacoes, 0)  # default
        self.assertIsNotNone(pet.data_criacao)
    
    def test_pet_perdido_str(self) -> None:
        """Testa representação em string."""
        pet = PetPerdido.objects.create(
            usuario=self.usuario,
            nome='Rex',
            especie='cachorro',
            data_perda=timezone.now().date(),
            cidade='SP',
            estado='SP',
            latitude=Decimal('-23.5505'),
            longitude=Decimal('-46.6333')
        )
        self.assertIn('Rex', str(pet))


class DenunciaModelTest(TestCase):
    """Testes para o modelo Denuncia."""
    
    def setUp(self) -> None:
        """Configura usuário para testes."""
        user = User.objects.create_user(username='denunciante', password='senha123')
        self.usuario = Usuario.objects.create(user=user)
    
    def test_criar_denuncia(self) -> None:
        """Testa criação de denúncia."""
        denuncia = Denuncia.objects.create(
            usuario=self.usuario,
            titulo='Maus-tratos',
            descricao='Animal em situação precária',
            categoria='maus_tratos',
            localizacao='Rua X, 123 - São Paulo/SP'  # Denuncia não tem campos cidade/estado separados
        )
        
        self.assertEqual(denuncia.status, 'pendente')  # default
        self.assertEqual(denuncia.categoria, 'maus_tratos')
        self.assertIsNotNone(denuncia.data_criacao)
    
    def test_denuncia_str(self) -> None:
        """Testa representação em string."""
        denuncia = Denuncia.objects.create(
            usuario=self.usuario,
            titulo='Abandono de animal',
            categoria='abandono',
            descricao='Descrição',
            localizacao='Rua Y - SP/SP'  # Denuncia não tem campos cidade/estado separados
        )
        self.assertIn('Abandono de animal', str(denuncia))


# ===== TESTES DE SERIALIZERS =====

class RegisterSerializerTest(TestCase):
    """Testes para o RegisterSerializer."""
    
    def test_criar_usuario_valido(self) -> None:
        """Testa criação de usuário com dados válidos."""
        data = {
            'username': 'novousuario',
            'email': 'novo@email.com',
            'password': 'senha123',
            'first_name': 'Novo Usuário',
            'telefone': '11988888888'
        }
        serializer = RegisterSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        self.assertEqual(user.username, 'novousuario')
        self.assertEqual(user.email, 'novo@email.com')
        self.assertTrue(user.check_password('senha123'))
        
        # Verifica que perfil Usuario foi criado
        self.assertTrue(hasattr(user, 'usuario'))
        self.assertEqual(user.usuario.telefone, '11988888888')
    
    def test_email_duplicado_invalido(self) -> None:
        """Testa que email duplicado não é aceito."""
        User.objects.create_user(
            username='existente',
            email='existente@email.com',
            password='senha123'
        )
        
        data = {
            'username': 'novo',
            'email': 'existente@email.com',
            'password': 'senha123'
        }
        serializer = RegisterSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class AnimalSerializerTest(TestCase):
    """Testes para o AnimalSerializer."""
    
    def test_serializar_animal_com_fotos(self) -> None:
        """Testa serialização de animal com fotos adicionais."""
        animal = Animal.objects.create(
            nome='Thor',
            tipo='cachorro',
            porte='grande',
            sexo='macho',
            cidade='SP',
            estado='SP'
        )
        
        # Adiciona foto
        AnimalFoto.objects.create(
            animal=animal,
            url='http://example.com/foto1.jpg'
        )
        
        serializer = AnimalSerializer(animal)
        data = serializer.data
        
        self.assertEqual(data['nome'], 'Thor')
        self.assertIn('fotos_urls', data)
        self.assertEqual(len(data['fotos_urls']), 1)


# ===== TESTES DE VIEWS/APIs =====

class AnimaisApiTests(APITestCase):
    """Testes para a API de animais do catálogo da ONG."""
    
    def setUp(self) -> None:
        """Configura dados de teste."""
        # Cria 3 animais com status variados
        Animal.objects.create(
            nome='Rex',
            tipo='cachorro',
            porte='medio',
            sexo='macho',
            estado='SP',
            cidade='São Paulo',
            status='disponivel'
        )
        Animal.objects.create(
            nome='Mia',
            tipo='gato',
            porte='pequeno',
            sexo='femea',
            estado='RJ',
            cidade='Rio de Janeiro',
            status='disponivel'
        )
        Animal.objects.create(
            nome='Bob',
            tipo='cachorro',
            porte='grande',
            sexo='macho',
            estado='MG',
            cidade='Belo Horizonte',
            status='adotado'
        )
    
    def test_list_default_shows_only_disponiveis(self) -> None:
        """Testa que listagem padrão mostra apenas disponíveis."""
        response = self.client.get('/api/animais/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            data = data['results']
        
        nomes = {a['nome'] for a in data}
        self.assertIn('Rex', nomes)
        self.assertIn('Mia', nomes)
        self.assertNotIn('Bob', nomes)  # adotado não aparece por padrão
    
    def test_filter_por_tipo(self) -> None:
        """Testa filtro por tipo de animal."""
        response = self.client.get('/api/animais/', {'tipo': 'gato'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            data = data['results']
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nome'], 'Mia')
    
    def test_filter_por_nome(self) -> None:
        """Testa busca por nome (case-insensitive, partial match)."""
        response = self.client.get('/api/animais/', {'nome': 'mi'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            data = data['results']
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nome'], 'Mia')
    
    def test_filter_por_cidade(self) -> None:
        """Testa filtro por cidade."""
        response = self.client.get('/api/animais/', {'cidade': 'São Paulo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            data = data['results']
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nome'], 'Rex')


class RegisterApiTest(APITestCase):
    """Testes para a API de registro de usuários."""
    
    def test_registrar_usuario_sucesso(self) -> None:
        """Testa registro de novo usuário."""
        data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'senha123',
            'first_name': 'Test User',
            'telefone': '11999999999'
        }
        
        response = self.client.post('/api/auth/register/', data, format='json')  # URL correta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica que usuário foi criado
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@email.com')
        self.assertTrue(hasattr(user, 'usuario'))
        self.assertEqual(user.usuario.telefone, '11999999999')
    
    def test_registrar_usuario_email_duplicado(self) -> None:
        """Testa que email duplicado retorna erro."""
        # Cria usuário existente
        User.objects.create_user(
            username='existing',
            email='existing@email.com',
            password='senha123'
        )
        
        data = {
            'username': 'newuser',
            'email': 'existing@email.com',
            'password': 'senha123'
        }
        
        response = self.client.post('/api/auth/register/', data, format='json')  # URL correta
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json())


class MeApiTest(APITestCase):
    """Testes para a API /api/me/ (dados do usuário autenticado)."""
    
    def setUp(self) -> None:
        """Configura usuário autenticado."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@email.com',
            password='senha123',
            first_name='Test User'
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            telefone='11999999999'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_dados_usuario(self) -> None:
        """Testa obtenção de dados do usuário logado."""
        response = self.client.get('/api/auth/me/')  # URL correta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@email.com')
        self.assertEqual(data['telefone'], '11999999999')
    
    def test_patch_atualizar_dados(self) -> None:
        """Testa atualização de dados do usuário."""
        data = {
            'first_name': 'Novo Nome',
            'telefone': '11988888888'
        }
        
        response = self.client.patch('/api/auth/me/', data, format='json')  # URL correta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que dados foram atualizados
        self.user.refresh_from_db()
        self.usuario.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'Novo Nome')
        self.assertEqual(self.usuario.telefone, '11988888888')


class PetPerdidoApiTest(APITestCase):
    """Testes para a API de pets perdidos."""
    
    def setUp(self) -> None:
        """Configura usuário e pet perdido."""
        self.user = User.objects.create_user(
            username='dono',
            password='senha123'
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            telefone='11999999999'
        )
        self.client.force_authenticate(user=self.user)
        
        self.pet = PetPerdido.objects.create(
            usuario=self.usuario,
            nome='Rex',
            especie='cachorro',
            porte='medio',
            cor='marrom',
            data_perda=timezone.now().date(),
            cidade='São Paulo',
            estado='SP',
            latitude=Decimal('-23.5505'),
            longitude=Decimal('-46.6333'),
            telefone_contato='11999999999',
            email_contato='dono@email.com'
        )
    
    def test_listar_pets_perdidos_ativos(self) -> None:
        """Testa listagem de pets perdidos ativos."""
        response = self.client.get('/api/pets-perdidos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            data = data['results']
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nome'], 'Rex')
    
    def test_marcar_pet_como_encontrado(self) -> None:
        """Testa ação de marcar pet como encontrado."""
        url = f'/api/pets-perdidos/{self.pet.id}/marcar_encontrado/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que status mudou
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.status, 'encontrado')
        self.assertFalse(self.pet.ativo)
        self.assertIsNotNone(self.pet.data_encontrado)


class MatchingAutomaticoTest(TransactionTestCase):
    """Testes para o sistema de matching automático de pets perdidos/encontrados."""
    
    def setUp(self) -> None:
        """Configura usuários e pets perdidos."""
        # Usuário dono do pet perdido
        user1 = User.objects.create_user(username='dono', password='senha123')
        self.usuario1 = Usuario.objects.create(user=user1)
        
        # Usuário que encontrou o pet
        user2 = User.objects.create_user(username='encontrador', password='senha123')
        self.usuario2 = Usuario.objects.create(user=user2)
        
        # Cria pet perdido
        self.pet_perdido = PetPerdido.objects.create(
            usuario=self.usuario1,
            nome='Totó',
            especie='cachorro',
            porte='pequeno',
            cor='marrom',
            data_perda=timezone.now().date(),
            cidade='São Paulo',
            estado='SP',
            latitude=Decimal('-23.5505'),
            longitude=Decimal('-46.6333'),
            telefone_contato='11999999999'
        )
    
    def test_reporte_pet_encontrado_cria_match(self) -> None:
        """Testa que reporte de pet encontrado similar cria match automático."""
        # Cria reporte de pet encontrado similar
        reporte = ReportePetEncontrado.objects.create(
            usuario=self.usuario2,
            especie='cachorro',
            porte='pequeno',
            cor='marrom claro',  # Cor similar
            data_encontro=timezone.now().date(),
            bairro='Centro',
            cidade='São Paulo',
            estado='SP',
            latitude=Decimal('-23.5510'),  # Próximo (500m)
            longitude=Decimal('-46.6340'),
            telefone_contato='11988888888',
            pet_com_usuario=True
        )
        
        # Simula matching automático (normalmente feito no create da view)
        from .views import ReportePetEncontradoViewSet
        viewset = ReportePetEncontradoViewSet()
        viewset._buscar_matches_automaticos(reporte)
        
        # Verifica que match foi criado
        reporte.refresh_from_db()
        self.assertTrue(reporte.possiveis_matches.exists())
        self.assertIn(self.pet_perdido, reporte.possiveis_matches.all())
    
    def test_calcular_distancia_haversine(self) -> None:
        """Testa cálculo de distância geodésica."""
        from .views import ReportePetEncontradoViewSet
        
        viewset = ReportePetEncontradoViewSet()
        
        # São Paulo (Sé) vs São Paulo (Av Paulista) ≈ 2.5km
        distancia = viewset._calcular_distancia(
            -23.5505, -46.6333,  # Sé
            -23.5613, -46.6561   # Paulista
        )
        
        # Verifica que distância está no range esperado (2-3 km)
        self.assertGreater(distancia, 2.0)
        self.assertLess(distancia, 3.0)


class DenunciaApiTest(APITestCase):
    """Testes para a API de denúncias."""
    
    def setUp(self) -> None:
        """Configura usuários (normal e admin)."""
        # Usuário normal
        self.user = User.objects.create_user(
            username='user',
            password='senha123'
        )
        self.usuario = Usuario.objects.create(user=self.user)
        
        # Admin
        self.admin = User.objects.create_user(
            username='admin',
            password='senha123',
            is_staff=True
        )
        Usuario.objects.create(user=self.admin)
    
    def test_criar_denuncia_autenticado(self) -> None:
        """Testa criação de denúncia por usuário autenticado."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'titulo': 'Maus-tratos',
            'descricao': 'Animal em situação precária',
            'categoria': 'maus_tratos',
            'localizacao': 'Rua X, 123',
            'cidade': 'São Paulo',
            'estado': 'SP'
        }
        
        response = self.client.post('/api/denuncias/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica que denúncia foi criada
        denuncia = Denuncia.objects.get(titulo='Maus-tratos')
        self.assertEqual(denuncia.usuario, self.usuario)
        self.assertEqual(denuncia.status, 'pendente')
    
    def test_admin_aprovar_denuncia(self) -> None:
        """Testa que admin pode aprovar denúncia."""
        # Cria denúncia
        denuncia = Denuncia.objects.create(
            usuario=self.usuario,
            titulo='Teste',
            categoria='maus_tratos',
            descricao='Descrição',
            localizacao='Rua Y - SP/SP'  # Denuncia não tem campos cidade/estado separados
        )
        
        # Admin aprova
        self.client.force_authenticate(user=self.admin)
        url = f'/api/denuncias/{denuncia.id}/aprovar/'
        response = self.client.post(url, {'observacoes': 'Aprovada'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que status mudou
        denuncia.refresh_from_db()
        self.assertEqual(denuncia.status, 'aprovada')
        self.assertEqual(denuncia.moderador, self.admin)
    
    def test_usuario_normal_nao_pode_aprovar(self) -> None:
        """Testa que usuário normal não pode aprovar denúncia."""
        denuncia = Denuncia.objects.create(
            usuario=self.usuario,
            titulo='Teste',
            categoria='abandono',
            descricao='Descrição',
            localizacao='Rua Z - SP/SP'  # Denuncia não tem campos cidade/estado separados
        )
        
        # Tenta aprovar como usuário normal
        self.client.force_authenticate(user=self.user)
        url = f'/api/denuncias/{denuncia.id}/aprovar/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SolicitacaoAdocaoApiTest(APITestCase):
    """Testes para sistema de solicitações de adoção."""
    
    def setUp(self) -> None:
        """Configura usuários e animal para adoção."""
        # Doador
        self.doador = User.objects.create_user(username='doador', password='senha123')
        self.usuario_doador = Usuario.objects.create(user=self.doador)
        
        # Interessado
        self.interessado = User.objects.create_user(username='interessado', password='senha123')
        self.usuario_interessado = Usuario.objects.create(user=self.interessado)
        
        # Admin
        self.admin = User.objects.create_user(
            username='admin',
            password='senha123',
            is_staff=True
        )
        Usuario.objects.create(user=self.admin)
        
        # Animal para adoção (aprovado)
        self.animal = AnimalParaAdocao.objects.create(
            usuario_doador=self.usuario_doador,
            nome='Thor',
            especie='cachorro',
            porte='grande',
            sexo='M',
            idade='2 anos',
            descricao='Cachorro grande e dócil',
            cidade='São Paulo',
            estado='SP',
            status='aprovado'
        )
    
    def test_criar_solicitacao_adocao(self) -> None:
        """Testa criação de solicitação de adoção."""
        self.client.force_authenticate(user=self.interessado)
        
        data = {
            'animal': self.animal.id,
            'mensagem': 'Gostaria de adotar este pet'
        }
        
        response = self.client.post('/api/solicitacoes-adocao/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica que solicitação foi criada
        solicitacao = SolicitacaoAdocao.objects.get(animal=self.animal)
        self.assertEqual(solicitacao.usuario_interessado, self.usuario_interessado)
        self.assertEqual(solicitacao.status, 'pendente')
    
    def test_admin_aprovar_solicitacao(self) -> None:
        """Testa aprovação de solicitação por admin."""
        # Cria solicitação
        solicitacao = SolicitacaoAdocao.objects.create(
            animal=self.animal,
            usuario_interessado=self.usuario_interessado,
            mensagem='Quero adotar'
        )
        
        # Admin aprova
        self.client.force_authenticate(user=self.admin)
        url = f'/api/solicitacoes-adocao/{solicitacao.id}/aprovar/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que solicitação foi aprovada
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'aprovada')
        
        # Verifica que animal foi marcado como adotado
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.status, 'adotado')


# ===== TESTES DE INTEGRAÇÃO =====

class IntegracaoCompletaTest(TransactionTestCase):
    """Testes de integração para fluxos completos do sistema."""
    
    def test_fluxo_completo_pet_perdido_encontrado(self) -> None:
        """Testa fluxo completo: pet perdido → reporte encontrado → match → reunião."""
        # 1. Usuário cadastra pet perdido
        user_dono = User.objects.create_user(username='dono', password='senha123')
        usuario_dono = Usuario.objects.create(user=user_dono)
        
        pet_perdido = PetPerdido.objects.create(
            usuario=usuario_dono,
            nome='Bolt',
            especie='cachorro',
            porte='medio',
            cor='branco',
            data_perda=timezone.now().date(),
            cidade='São Paulo',
            estado='SP',
            latitude=Decimal('-23.5505'),
            longitude=Decimal('-46.6333'),
            telefone_contato='11999999999'
        )
        
        self.assertEqual(pet_perdido.status, 'perdido')
        self.assertTrue(pet_perdido.ativo)
        
        # 2. Outra pessoa encontra pet similar e reporta
        user_encontrador = User.objects.create_user(username='encontrador', password='senha123')
        usuario_encontrador = Usuario.objects.create(user=user_encontrador)
        
        reporte = ReportePetEncontrado.objects.create(
            usuario=usuario_encontrador,
            especie='cachorro',
            porte='medio',
            cor='branco',
            data_encontro=timezone.now().date(),
            cidade='São Paulo',
            estado='SP',
            latitude=Decimal('-23.5510'),
            longitude=Decimal('-46.6335'),
            telefone_contato='11988888888',
            pet_com_usuario=True
        )
        
        # 3. Sistema faz matching automático
        from .views import ReportePetEncontradoViewSet
        viewset = ReportePetEncontradoViewSet()
        viewset._buscar_matches_automaticos(reporte)
        
        reporte.refresh_from_db()
        self.assertTrue(reporte.possiveis_matches.exists())
        
        # 4. Admin confirma match
        reporte.pet_perdido_confirmado = pet_perdido
        reporte.status = 'aprovado'
        reporte.save()
        
        # 5. Pet perdido é marcado como encontrado
        pet_perdido.status = 'encontrado'
        pet_perdido.ativo = False
        pet_perdido.data_encontrado = timezone.now()
        pet_perdido.save()
        
        # Verificações finais
        pet_perdido.refresh_from_db()
        self.assertEqual(pet_perdido.status, 'encontrado')
        self.assertFalse(pet_perdido.ativo)
        self.assertIsNotNone(pet_perdido.data_encontrado)

