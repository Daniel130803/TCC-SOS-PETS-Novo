#!/usr/bin/env sh
set -e

echo "🚀 Starting S.O.S Pets Backend..."

# Aguarda o banco de dados estar pronto
echo "⏳ Waiting for database..."
until python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
  echo "Database unavailable - sleeping"
  sleep 2
done
echo "✅ Database is ready!"

# Executa migrações
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Coleta arquivos estáticos (se não for dev)
if [ "$DJANGO_ENV" != "dev" ]; then
  echo "📦 Collecting static files..."
  python manage.py collectstatic --noinput --clear
fi

# Cria superusuário se variáveis estiverem definidas
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "👤 Creating superuser..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created!')
else:
    print('Superuser already exists.')
END
fi

echo "✨ Setup complete! Starting application..."

# Executa o comando passado (CMD do Dockerfile)
exec "$@"
