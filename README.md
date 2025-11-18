# TCC-SOS-PETS

Plataforma web para adoção e reencontro de pets, conectando animais resgatados com novos lares e ajudando a reunir pets perdidos com suas famílias.

## 🐾 Sobre o Projeto

O S.O.S Pets é uma plataforma digital que oferece:
- **Adoção**: Galeria de animais disponíveis para adoção com filtros avançados
- **Pets Perdidos**: Sistema de mural com geolocalização para reportar e encontrar animais perdidos
- **Arrecadação**: Canal para doações financeiras e materiais
- **Denúncia**: Formulário seguro e anônimo para reportar maus-tratos
- **Histórias de Sucesso**: Depoimentos e casos de adoções e reencontros bem-sucedidos

## 🚀 Tecnologias

### Backend
- **Django 5.2.8** - Framework web
- **Django REST Framework 3.16.1** - APIs RESTful
- **MySQL** - Banco de dados principal
- **SimpleJWT 5.5.1** - Autenticação JWT
- **Pillow 12.0.0** - Processamento de imagens
- **Python 3.13**

### Frontend
- **HTML5/CSS3** - Estrutura e estilização
- **JavaScript (Vanilla)** - Interatividade
- **Font Awesome 6.5.2** - Ícones
- **Google Fonts (Poppins, Roboto, Nunito)** - Tipografia
- **Leaflet 1.9.4** - Mapas interativos

## 📋 Pré-requisitos

**Opção 1: Com Docker (Recomendado)**
- Docker Desktop 20.10+
- Docker Compose 2.0+
- Navegador web moderno

**Opção 2: Instalação Manual**
- Python 3.13+
- MySQL Server 8.0+
- Navegador web moderno

## ⚙️ Instalação

### 🐳 Opção 1: Docker (Recomendado - Mais Rápido)

Ideal para desenvolvimento. Tudo configurado automaticamente.

#### 1. Clone o repositório
```bash
git clone https://github.com/Daniel130803/TCC-SOS-PETS-Novo.git
cd TCC-SOS-PETS-Novo
```

#### 2. Configure variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite se necessário (valores padrão já funcionam)
```

#### 3. Suba os containers
```bash
docker-compose up -d
```

Isso irá:
- Criar container MySQL com banco configurado
- Criar container Redis para cache
- Criar container do backend Django
- Rodar migrações automaticamente
- Subir o servidor em http://localhost:8000

#### 4. Acesse a aplicação
- Frontend: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

#### 5. (Opcional) Criar superusuário
```bash
docker-compose exec web python manage.py createsuperuser
```

#### Comandos úteis Docker
```bash
# Ver logs
docker-compose logs -f web

# Parar containers
docker-compose down

# Reconstruir após mudanças no código
docker-compose up -d --build

# Rodar comandos Django
docker-compose exec web python manage.py <comando>

# Acessar shell do container
docker-compose exec web bash
```

---

### 💻 Opção 2: Instalação Manual (Sem Docker)

### 1. Clone o repositório
```bash
git clone https://github.com/Daniel130803/TCC-SOS-PETS-Novo.git
cd TCC-SOS-PETS-Novo
```

### 2. Configure o ambiente virtual (Backend)
```bash
cd backend/backend
python -m venv venv-backend
# Windows
venv-backend\Scripts\activate
# Linux/Mac
source venv-backend/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na pasta `backend/backend/` (ou copie de `.env.example`) com:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_ENGINE=mysql
DB_NAME=sos_pets
DB_USER=root
DB_PASSWORD=sua-senha-mysql
DB_HOST=localhost
DB_PORT=3306
```

### 5. Configure o banco de dados MySQL
```sql
CREATE DATABASE sos_pets CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crie um superusuário (opcional)
```bash
python manage.py createsuperuser
```

### 8. Inicie o servidor
```bash
python manage.py runserver
```

Acesse: `http://localhost:8000`

## 🔐 Sistema de Autenticação
### Documentação da API (OpenAPI)

- Esquema: `/api/schema/`
- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`


### Fluxo de Autenticação JWT

O sistema utiliza **JWT (JSON Web Tokens)** para autenticação stateless:

1. **Registro**: Usuário cria conta via `/registro/`
2. **Login**: Sistema retorna `access` e `refresh` tokens
3. **Armazenamento**: Tokens salvos no `localStorage` do navegador
4. **Autenticação**: Token `access` enviado no header `Authorization: Bearer <token>`
5. **Renovação**: Token `refresh` usado para obter novo `access` quando expira

### Endpoints da API

#### Autenticação

**POST `/api/auth/register/`** - Registrar novo usuário
```json
{
  "username": "usuario",
  "email": "usuario@email.com",
  "password": "senha123",
  "first_name": "Nome",
  "telefone": "(11) 90000-0000"
}
```

**POST `/api/auth/token/`** - Obter tokens (login)
```json
{
  "username": "usuario",
  "password": "senha123"
}
```
Resposta:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhb..."
}
```

**POST `/api/auth/token/refresh/`** - Renovar token de acesso
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhb..."
}
```

**GET `/api/auth/me/`** - Obter dados do usuário logado
- Header: `Authorization: Bearer <access_token>`
- Resposta:
```json
{
  "id": 1,
  "username": "usuario",
  "email": "usuario@email.com",
  "first_name": "Nome",
  "telefone": "(11) 90000-0000"
}
```

**PATCH `/api/auth/me/`** - Atualizar perfil do usuário
- Header: `Authorization: Bearer <access_token>`
```json
{
  "first_name": "Novo Nome",
  "email": "novoemail@email.com",
  "telefone": "(11) 99999-9999"
}
```

#### Recursos

**GET/POST `/api/animais/`** - Listar/criar animais para adoção
**GET/PUT/PATCH/DELETE `/api/animais/{id}/`** - Operações CRUD em animal específico

**GET/POST `/api/adocoes/`** - Listar/criar solicitações de adoção
**GET/PUT/PATCH/DELETE `/api/adocoes/{id}/`** - Operações CRUD em adoção específica

#### Filtros em `/api/animais/`

Parâmetros de query aceitos (todos opcionais):

- `status`: filtra por status (padrão da listagem é `disponivel`)
- `tipo`: `cachorro` | `gato` (aceita `cao` como sinônimo de `cachorro`)
- `porte`: `pequeno` | `medio` | `grande`
- `sexo`: `macho` | `femea`
- `estado`: UF, ex.: `SP`, `RJ`
- `cidade`: nome exato da cidade, ex.: `São Paulo`
- `nome` (ou `q`): busca parcial por nome (case-insensitive)

Exemplos:

- `/api/animais/?tipo=cachorro&porte=pequeno&estado=SP`
- `/api/animais/?nome=apo` (retorna registros com nome contendo "apo")

Campos retornados incluem `imagem_url` (se imagem remota), `imagem_absolute` (se upload local), além de `fotos_urls` e `videos_urls` com mídias adicionais.

#### Seed de animais (exemplos)

Para popular a base com alguns animais de exemplo:

```bash
python manage.py seed_animais
```

### Permissões

- **Endpoints públicos**: `/api/auth/register/`, `/api/auth/token/`, `/api/animais/` (GET)
- **Autenticação obrigatória**: 
  - `/api/auth/me/` (GET, PATCH)
  - `/api/adocoes/` (todos os métodos)
  - `/api/animais/` (POST, PUT, PATCH, DELETE)

### Script de Sessão (`user_session.js`)

O arquivo `user_session.js` gerencia a interface de usuário logado:

**Funcionalidades:**
- Verifica tokens no `localStorage` ao carregar página
- Exibe dropdown com "Olá, <usuário>" quando autenticado
- Mostra botão "Login" quando não autenticado
- Renova token automaticamente quando necessário
- Implementa menu dropdown com opções "Perfil" e "Sair"
- Sanitiza dados para prevenir XSS

**Uso:**
```html
<div class="nav-user-area"></div>
<script src="{% static 'user_session.js' %}" defer></script>
```

## 📁 Estrutura do Projeto

```
TCC-SOS-PETS/
├── backend/
│   └── backend/
│       ├── manage.py
│       ├── requirements.txt
│       ├── .env (criar)
│       ├── backend/
│       │   ├── settings/
│       │   │   ├── __init__.py  # seleciona dev/prod via DJANGO_ENV
│       │   │   ├── base.py
│       │   │   ├── dev.py
│       │   │   └── prod.py
│       │   ├── urls.py
│       │   └── wsgi.py
│       └── core/
│           ├── models.py       # Usuario, Animal, Adocao, etc.
│           ├── serializers.py  # DRF serializers
│           ├── views.py        # API views
│           └── urls.py         # Rotas da API
└── TCC_SOS_Pets/
    ├── index.html
    ├── login.html
    ├── registro.html
    ├── perfil.html
    ├── adocao.html
    ├── animais-perdidos.html
    ├── arrecadacao.html
    ├── denuncia.html
    ├── contato.html
    ├── historias.html
    ├── formulario-adocao.html
    ├── style.css
    ├── user_session.js         # Gerenciamento de sessão
    ├── login.js                # Lógica de login
    ├── registro.js             # Lógica de registro
    └── Estetica_site/          # Imagens e assets
```

## 🗄️ Modelos do Banco de Dados

### Usuario (perfil estendido de User)
- `user` (OneToOne com User do Django)
- `telefone`
- `foto_perfil`

### Animal
- `nome`, `especie`, `porte`, `sexo`, `idade`
- `descricao`, `foto`
- `estado`, `cidade`
- `status` (disponível, adotado, reservado)
- `data_cadastro`

### Adocao
- `animal` (ForeignKey)
- `adotante` (ForeignKey para User)
- `data_solicitacao`, `status`
- `unique_together` para prevenir duplicatas

## 🎨 Funcionalidades Frontend

### Sistema de Navegação
- Header responsivo com dropdown de usuário
- Links dinâmicos baseados em estado de autenticação
- Redirecionamento de URLs legadas (.html → rotas limpas)

### Páginas Principais
- **Index**: Hero section, carrossel, depoimentos, CTAs
- **Adoção**: Galeria com filtros (espécie, porte, localização)
- **Pets Perdidos**: Mapa interativo com Leaflet, modais para reportar
- **Perfil**: Formulário de edição com validação e feedback
- **Login/Registro**: Autenticação com tratamento de erros

### Recursos CSS
- Design responsivo
- Animações suaves (hover, transitions)
- Paleta de cores consistente
- Acessibilidade (ARIA labels, contraste)

## 🔒 Segurança

### Implementado
- ✅ Autenticação JWT stateless
- ✅ Passwords hasheados (Django PBKDF2)
- ✅ Validação de email único
- ✅ Sanitização de inputs no frontend
- ✅ CORS configurado
- ✅ Tokens com expiração

### A Implementar (Produção)
- ⚠️ HTTPS obrigatório
- ⚠️ Secure flags em cookies (se usar sessões)
- ⚠️ Rate limiting em endpoints sensíveis
- ⚠️ Validação CSRF para forms não-API
- ⚠️ Environment variables protegidas
- ⚠️ Logging de segurança

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Testes específicos
python manage.py test core.tests
```

## 🤖 CI/CD (Integração Contínua)

O projeto usa **GitHub Actions** para automação de qualidade e deploy.

### Pipeline CI
A cada push ou pull request, automaticamente:
1. ✅ **Lint & Format**: Verifica formatação com black, isort e ruff
2. 🧪 **Testes**: Roda suite de testes com MySQL
3. 🐳 **Docker Build**: Valida que a imagem Docker compila

### Ver status do CI
- Badge no topo do README (quando configurado)
- Aba "Actions" no GitHub
- Status de checks em Pull Requests

### Rodar localmente o que o CI roda
```bash
# Lint e formatação
cd backend/backend
pip install black isort ruff
black --check .
isort --check-only .
ruff check .

# Testes
python manage.py test

# Build Docker
docker-compose build
```

## 📊 Monitoramento e Logs

### Logging Estruturado (JSON)
Logs em formato JSON para análise e alertas:
```json
{
  "timestamp": "2025-11-18T19:00:00Z",
  "level": "ERROR",
  "message": "Failed to create adoption",
  "pathname": "/app/core/views.py",
  "lineno": 42
}
```

### Sentry (Monitoramento de Erros)
Configure Sentry para capturar erros em produção:
1. Crie conta em https://sentry.io (grátis até 5k eventos/mês)
2. Crie novo projeto Django
3. Adicione DSN no `.env`:
```env
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
SENTRY_TRACES_SAMPLE_RATE=0.1
```

Erros em produção serão automaticamente reportados com:
- Stack trace completo
- Contexto da requisição
- Dados do usuário (se configurado)
- Alertas por email/Slack

## 🚀 Deploy

### Deploy com Docker (Recomendado)

#### 1. Configure variáveis de produção
Crie `.env` com valores de produção:
```env
DJANGO_ENV=prod
SECRET_KEY=<chave-super-secreta-aqui>
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

DB_ENGINE=mysql
DB_NAME=sos_pets_prod
DB_USER=prod_user
DB_PASSWORD=<senha-forte>
DB_HOST=db  # ou IP do banco gerenciado

CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://seudominio.com

SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

#### 2. Build e deploy
```bash
# Build da imagem de produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Suba os containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verifique logs
docker-compose logs -f web
```

#### 3. Nginx reverso (opcional mas recomendado)
Configure Nginx como proxy reverso:
```nginx
server {
    listen 80;
    server_name seudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/staticfiles/;
    }

    location /media/ {
        alias /var/www/media/;
    }
}
```

### Deploy Manual (Sem Docker)

#### Preparação para Produção
1. Altere `DJANGO_ENV=prod` no `.env`
2. Configure `SECRET_KEY` forte e única
3. `DEBUG=False`
4. Configure `ALLOWED_HOSTS` correto
5. Use servidor WSGI: Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 --workers 3 backend.wsgi:application
```
6. Configure servidor web (Nginx/Apache) como proxy
7. Use banco gerenciado (AWS RDS, Azure Database)
8. Configure backup automático
9. Implemente monitoring (Sentry configurado)

### Collectstatic
```bash
python manage.py collectstatic --noinput
```

### Healthcheck
Endpoint para verificar saúde da aplicação:
- `/api/schema/` - Se retornar 200, aplicação está saudável

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- **Daniel** - Desenvolvedor Principal - [Daniel130803](https://github.com/Daniel130803)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou suporte, abra uma issue no GitHub ou entre em contato através do formulário de contato no site.

---

**S.O.S Pets** - Conectando corações e transformando vidas 🐶🐱💙
