from django.contrib.auth.models import User

user = User.objects.get(username='admin')
user.set_password('!@#$Admin123')
user.save()
print('✅ Senha definida com sucesso!')
print(f'Usuário: {user.username}')
print(f'Email: {user.email}')
print(f'Admin: {user.is_staff}')
print(f'Superuser: {user.is_superuser}')
