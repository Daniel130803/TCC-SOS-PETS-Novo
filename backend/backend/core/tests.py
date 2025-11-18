from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Animal


class AnimaisApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		# cria 3 animais com status variados
		Animal.objects.create(nome='Rex', tipo='cachorro', porte='medio', sexo='macho', estado='SP', cidade='São Paulo', status='disponivel')
		Animal.objects.create(nome='Mia', tipo='gato', porte='pequeno', sexo='femea', estado='RJ', cidade='Rio de Janeiro', status='disponivel')
		Animal.objects.create(nome='Bob', tipo='cachorro', porte='grande', sexo='macho', estado='MG', cidade='Belo Horizonte', status='adotado')

	def test_list_default_shows_only_disponiveis(self):
		resp = self.client.get('/api/animais/')
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		nomes = {a['nome'] for a in data}
		self.assertIn('Rex', nomes)
		self.assertIn('Mia', nomes)
		self.assertNotIn('Bob', nomes)  # adotado não deve aparecer por padrão

	def test_filter_tipo_and_nome(self):
		resp = self.client.get('/api/animais/', {'tipo': 'gato', 'nome': 'mi'})
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertEqual(len(data), 1)
		self.assertEqual(data[0]['nome'], 'Mia')
