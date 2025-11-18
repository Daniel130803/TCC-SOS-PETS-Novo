from django.core.management.base import BaseCommand
from core.models import Animal, AnimalFoto

SAMPLES = [
    {
        'nome': 'Abelly', 'tipo': 'cachorro', 'porte': 'pequeno', 'sexo': 'femea',
        'raca': 'SRD', 'idade_anos': 2, 'descricao': 'Dócil e brincalhona',
        'estado': 'SP', 'cidade': 'São Paulo',
        'imagem_url': 'https://images.pexels.com/photos/1805164/pexels-photo-1805164.jpeg?auto=compress&cs=tinysrgb&w=400',
        'fotos': [
            'https://images.pexels.com/photos/1805164/pexels-photo-1805164.jpeg?auto=compress&cs=tinysrgb&w=400'
        ]
    },
    {
        'nome': 'Aglaia', 'tipo': 'gato', 'porte': 'pequeno', 'sexo': 'femea',
        'raca': 'SRD', 'idade_anos': 1, 'descricao': 'Curiosa e carinhosa',
        'estado': 'RJ', 'cidade': 'Rio de Janeiro',
        'imagem_url': 'https://images.pexels.com/photos/208773/pexels-photo-208773.jpeg?auto=compress&cs=tinysrgb&w=400',
        'fotos': [
            'https://images.pexels.com/photos/208773/pexels-photo-208773.jpeg?auto=compress&cs=tinysrgb&w=400'
        ]
    },
    {
        'nome': 'Alordy', 'tipo': 'cachorro', 'porte': 'medio', 'sexo': 'macho',
        'raca': 'SRD', 'idade_anos': 3, 'descricao': 'Leal e amigável',
        'estado': 'MG', 'cidade': 'Belo Horizonte',
        'imagem_url': 'https://images.pexels.com/photos/57497/pexels-photo-57497.jpeg?auto=compress&cs=tinysrgb&w=400',
        'fotos': [
            'https://images.pexels.com/photos/57497/pexels-photo-57497.jpeg?auto=compress&cs=tinysrgb&w=400'
        ]
    },
    {
        'nome': 'Apolo', 'tipo': 'cachorro', 'porte': 'grande', 'sexo': 'macho',
        'raca': 'SRD', 'idade_anos': 4, 'descricao': 'Ativo e protetor',
        'estado': 'SP', 'cidade': 'São Joaquim da Barra',
        'imagem_url': 'https://images.pexels.com/photos/3726315/pexels-photo-3726315.jpeg?auto=compress&cs=tinysrgb&w=400',
        'fotos': [
            'https://images.pexels.com/photos/3726315/pexels-photo-3726315.jpeg?auto=compress&cs=tinysrgb&w=400'
        ]
    }
]

class Command(BaseCommand):
    help = 'Popula o banco com animais de exemplo (não duplica por nome + cidade).'

    def handle(self, *args, **options):
        created = 0
        for item in SAMPLES:
            animal, was_created = Animal.objects.get_or_create(
                nome=item['nome'], cidade=item['cidade'], defaults={
                    'tipo': item['tipo'],
                    'porte': item.get('porte'),
                    'sexo': item.get('sexo'),
                    'raca': item.get('raca', ''),
                    'idade_anos': item.get('idade_anos'),
                    'descricao': item.get('descricao', ''),
                    'estado': item.get('estado'),
                    'imagem_url': item.get('imagem_url'),
                    'status': 'disponivel',
                }
            )
            if was_created:
                created += 1
                for url in item.get('fotos', []):
                    AnimalFoto.objects.create(animal=animal, url=url)
        self.stdout.write(self.style.SUCCESS(f"Seed finalizado. Novos animais criados: {created}"))
