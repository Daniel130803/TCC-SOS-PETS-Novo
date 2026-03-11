# Arquitetura do Sistema S.O.S Pets

## Visão Geral

O S.O.S Pets é uma plataforma web desenvolvida com arquitetura cliente-servidor, utilizando Django REST Framework no backend e JavaScript vanilla no frontend. O sistema foi projetado para ser escalável, seguro e de fácil manutenção.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CAMADA DE APRESENTAÇÃO                          │
│                                  (Frontend)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   HTML5/     │  │  JavaScript  │  │     CSS3     │  │   Leaflet.js │   │
│  │   Django     │  │   (Vanilla)  │  │  (Responsive)│  │    (Mapas)   │   │
│  │  Templates   │  │              │  │              │  │              │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │            │
│         └─────────────────┴─────────────────┴─────────────────┘            │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     │ HTTPS/REST API
                                     │ (JSON)
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                                    │                                        │
│                           CAMADA DE APLICAÇÃO                               │
│                              (Backend - Django)                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Django REST Framework                         │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │   ViewSets   │  │ Serializers  │  │ Permissions  │             │   │
│  │  │              │  │              │  │              │             │   │
│  │  │ - Animal     │  │ - Animal     │  │ - IsAuth     │             │   │
│  │  │ - Adocao     │  │ - Adocao     │  │ - IsOwner    │             │   │
│  │  │ - Denuncia   │  │ - Denuncia   │  │ - IsAdmin    │             │   │
│  │  │ - PetPerdido │  │ - PetPerdido │  │              │             │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │   │
│  │         │                 │                 │                      │   │
│  └─────────┼─────────────────┼─────────────────┼──────────────────────┘   │
│            │                 │                 │                           │
│            └─────────────────┴─────────────────┘                           │
│                              │                                              │
│  ┌───────────────────────────┼───────────────────────────────────────┐    │
│  │                    CAMADA DE NEGÓCIO                              │    │
│  │                                                                    │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │    │
│  │  │     Models      │  │    Business      │  │    Utilities     │ │    │
│  │  │                 │  │     Logic        │  │                  │ │    │
│  │  │ - Usuario       │  │                  │  │ - Geolocalização │ │    │
│  │  │ - Animal        │  │ - Matching Pets  │  │ - Upload Imgs    │ │    │
│  │  │ - Adocao        │  │ - Notificações   │  │ - Validações     │ │    │
│  │  │ - Denuncia      │  │ - Cálculo Raio   │  │ - Formatação     │ │    │
│  │  │ - PetPerdido    │  │ - Status Tracking│  │                  │ │    │
│  │  │ - Notificacao   │  │                  │  │                  │ │    │
│  │  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘ │    │
│  │           │                    │                     │           │    │
│  └───────────┼────────────────────┼─────────────────────┼───────────┘    │
│              │                    │                     │                 │
└──────────────┼────────────────────┼─────────────────────┼─────────────────┘
               │                    │                     │
               │                    │                     │
┌──────────────┼────────────────────┼─────────────────────┼─────────────────┐
│              │          CAMADA DE SEGURANÇA             │                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │     JWT      │  │     CORS     │  │   CSRF       │  │  Validators │  │
│  │ Authentication│  │   Headers    │  │ Protection   │  │             │  │
│  │              │  │              │  │              │  │  - Email    │  │
│  │ - Access     │  │ - Origins    │  │ - Tokens     │  │  - Phone    │  │
│  │ - Refresh    │  │ - Methods    │  │ - Cookie     │  │  - CPF      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
               │                    │                     │
               │                    │                     │
┌──────────────┼────────────────────┼─────────────────────┼─────────────────┐
│              │           CAMADA DE DADOS                │                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │                        Django ORM                                │     │
│  │                                                                  │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │     │
│  │  │  Migrations  │  │    Queries   │  │ Transactions │         │     │
│  │  │              │  │              │  │              │         │     │
│  │  │ - Schema     │  │ - Select     │  │ - ACID       │         │     │
│  │  │ - Versioning │  │ - Join       │  │ - Rollback   │         │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │     │
│  └──────────────────────────────┬───────────────────────────────────┘     │
│                                 │                                         │
│  ┌──────────────────────────────┼──────────────────────────────────┐     │
│  │                         MySQL 8.0                                │     │
│  │                                                                  │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │     │
│  │  │  Tabelas │  │  Índices │  │ Triggers │  │  Views   │       │     │
│  │  │          │  │          │  │          │  │          │       │     │
│  │  │ - core_* │  │ - PK/FK  │  │ - Auto   │  │ - Stats  │       │     │
│  │  │ - auth_* │  │ - Search │  │ - Audit  │  │          │       │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
               │                                          │
               │                                          │
┌──────────────┼──────────────────────────────────────────┼─────────────────┐
│              │        CAMADA DE ARMAZENAMENTO           │                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────┐              ┌──────────────────┐                  │
│  │   Sistema de     │              │      Logs        │                  │
│  │    Arquivos      │              │                  │                  │
│  │                  │              │  - Application   │                  │
│  │  /media/         │              │  - Access        │                  │
│  │  ├─ animais/     │              │  - Error         │                  │
│  │  ├─ denuncias/   │              │  - Security      │                  │
│  │  ├─ pets/        │              │                  │                  │
│  │  └─ usuarios/    │              │  /logs/          │                  │
│  │                  │              │  ├─ django.log   │                  │
│  │  /static/        │              │  └─ access.log   │                  │
│  │  ├─ css/         │              │                  │                  │
│  │  ├─ js/          │              │                  │                  │
│  │  └─ images/      │              │                  │                  │
│  └──────────────────┘              └──────────────────┘                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND COMPONENTS                              │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   index.html │    │ adocao.html  │    │animais-      │    │ denuncia.html│
│              │    │              │    │perdidos.html │    │              │
│ - Hero       │    │ - Galeria    │    │              │    │ - Formulário │
│ - Features   │    │ - Filtros    │    │ - Mapa       │    │ - Upload     │
│ - CTA        │    │ - Cards      │    │ - Modais     │    │ - Anônimo    │
└──────┬───────┘    └──────┬───────┘    │ - Pins       │    └──────┬───────┘
       │                   │            └──────┬───────┘           │
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                ┌─────────▼────────┐ ┌────────▼─────────┐
                │  user_session.js │ │  Script Principal│
                │                  │ │                  │
                │ - checkAuth()    │ │ - API calls      │
                │ - updateUI()     │ │ - Event handlers │
                │ - logout()       │ │ - Validations    │
                └──────────────────┘ └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND COMPONENTS                               │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────────┐
                        │    urls.py (Root)    │
                        │                      │
                        │ /api/ → core.urls    │
                        │ /admin/ → admin      │
                        │ /auth/ → JWT         │
                        └──────────┬───────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
    ┌───────────▼──────────┐             ┌───────────▼──────────┐
    │   ViewSets (DRF)     │             │    Serializers       │
    │                      │             │                      │
    │ - list()             │◄────────────┤ - validate()         │
    │ - create()           │             │ - to_representation()│
    │ - retrieve()         │             │ - create()           │
    │ - update()           │             │ - update()           │
    │ - destroy()          │             │                      │
    │ - custom_actions()   │             │                      │
    └───────────┬──────────┘             └──────────────────────┘
                │
    ┌───────────▼──────────┐
    │      Models          │
    │                      │
    │ - Usuario            │
    │ - Animal             │
    │ - AnimalParaAdocao   │
    │ - SolicitacaoAdocao  │
    │ - Denuncia           │
    │ - PetPerdido         │
    │ - ReportePetEnc.     │
    │ - Notificacao        │
    │ - Contato            │
    └──────────────────────┘
```

## Fluxo de Dados

### 1. Fluxo de Autenticação

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│ Cliente │         │Frontend │         │ Backend │         │Database │
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │ 1. Login          │                   │                   │
     ├──────────────────►│                   │                   │
     │                   │ 2. POST /auth/    │                   │
     │                   ├──────────────────►│                   │
     │                   │                   │ 3. Validate       │
     │                   │                   ├──────────────────►│
     │                   │                   │                   │
     │                   │                   │ 4. User Data      │
     │                   │                   ◄──────────────────┤
     │                   │                   │                   │
     │                   │ 5. JWT Tokens     │                   │
     │                   ◄──────────────────┤                   │
     │                   │                   │                   │
     │ 6. Store Tokens   │                   │                   │
     ◄──────────────────┤                   │                   │
     │                   │                   │                   │
     │ 7. API Request    │                   │                   │
     │ (Bearer Token)    │                   │                   │
     ├──────────────────►├──────────────────►│                   │
     │                   │                   │ 8. Verify Token   │
     │                   │                   │                   │
     │                   │                   │ 9. Query          │
     │                   │                   ├──────────────────►│
     │                   │                   │                   │
     │                   │                   │ 10. Data          │
     │                   │                   ◄──────────────────┤
     │                   │ 11. JSON Response │                   │
     │                   ◄──────────────────┤                   │
     │ 12. Update UI     │                   │                   │
     ◄──────────────────┤                   │                   │
     │                   │                   │                   │
```

### 2. Fluxo de Adoção

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│Adotante │         │ Sistema │         │  Dono   │         │  Admin  │
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │ 1. Solicita       │                   │                   │
     ├──────────────────►│                   │                   │
     │                   │ 2. Cria Solic.    │                   │
     │                   ├───────────────────┤                   │
     │                   │                   │                   │
     │                   │ 3. Notifica       │                   │
     │                   ├──────────────────►│                   │
     │                   │                   │                   │
     │                   │ 4. Avalia Perfil  │                   │
     │                   ◄──────────────────┤                   │
     │                   │                   │                   │
     │                   │ 5. Aprova/Rejeita │                   │
     │                   ◄──────────────────┤                   │
     │                   │                   │                   │
     │ 6. Notificação    │                   │                   │
     ◄──────────────────┤                   │                   │
     │                   │                   │                   │
     │ 7. Se Aprovado    │                   │                   │
     │ Agendar Visita    │                   │                   │
     ├──────────────────►├──────────────────►│                   │
     │                   │                   │                   │
     │                   │ 8. Marca como     │                   │
     │                   │    Adotado        │                   │
     │                   ├──────────────────►│                   │
     │                   │                   │                   │
     │                   │ 9. Admin Valida   │                   │
     │                   ├───────────────────┼──────────────────►│
     │                   │                   │                   │
     │                   │ 10. Confirmação   │                   │
     │                   ◄───────────────────┼──────────────────┤
     │                   │                   │                   │
```

### 3. Fluxo de Pets Perdidos

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│  Dono   │         │ Sistema │         │Encontrou│         │ Matching│
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │ 1. Registra       │                   │                   │
     │    Pet Perdido    │                   │                   │
     ├──────────────────►│                   │                   │
     │                   │ 2. Salva + Geoloc │                   │
     │                   ├───────────────────┤                   │
     │                   │                   │                   │
     │                   │ 3. Exibe no Mapa  │                   │
     │                   │    (Pin Vermelho) │                   │
     │                   ├───────────────────┤                   │
     │                   │                   │                   │
     │                   │                   │ 4. Encontra Pet   │
     │                   │                   │    Reporta        │
     │                   ◄───────────────────┤                   │
     │                   │                   │                   │
     │                   │ 5. Matching Auto  │                   │
     │                   ├───────────────────┼──────────────────►│
     │                   │                   │                   │
     │                   │ 6. Cálculo Raio   │                   │
     │                   │    + Similaridade │                   │
     │                   ◄───────────────────┼──────────────────┤
     │                   │                   │                   │
     │ 7. Notificação    │                   │                   │
     │    de Match       │                   │                   │
     ◄──────────────────┤                   │                   │
     │                   │                   │                   │
     │ 8. Visualiza      │                   │ 9. Recebe         │
     │    Contato        │                   │    Contato        │
     ├──────────────────►├──────────────────►│                   │
     │                   │                   │                   │
     │ 10. Confirma      │                   │                   │
     │     Reencontro    │                   │                   │
     ├──────────────────►│                   │                   │
     │                   │ 11. Status:       │                   │
     │                   │     Encontrado    │                   │
     │                   ├───────────────────┤                   │
     │                   │                   │                   │
```

## Tecnologias e Ferramentas

### Backend
- **Framework**: Django 5.2.8
- **API**: Django REST Framework 3.16.1
- **Autenticação**: SimpleJWT 5.5.1
- **Banco de Dados**: MySQL 8.0
- **ORM**: Django ORM
- **Validação**: Django Validators + Custom
- **Upload**: Pillow 12.0.0
- **Documentação**: drf-spectacular 0.27.2

### Frontend
- **Marcação**: HTML5 + Django Templates
- **Estilização**: CSS3 (Grid, Flexbox, Animations)
- **Interatividade**: JavaScript ES6+ (Vanilla)
- **Mapas**: Leaflet.js 1.9.4
- **Ícones**: Font Awesome 6.5.2
- **Fontes**: Google Fonts (Poppins, Roboto, Nunito)

### Infraestrutura
- **Containerização**: Docker + Docker Compose
- **Web Server**: Gunicorn (produção)
- **Proxy Reverso**: Nginx (planejado)
- **Cache**: Redis (planejado para Celery)
- **CI/CD**: GitHub Actions

### Segurança
- **Autenticação**: JWT (Access + Refresh Tokens)
- **Autorização**: DRF Permissions (IsAuthenticated, IsOwner)
- **CORS**: django-cors-headers
- **CSRF**: Django CSRF Protection
- **Senha**: PBKDF2 (Django default)
- **HTTPS**: SSL/TLS (produção)

## Padrões de Projeto

### 1. Model-View-Template (MVT)
Django segue o padrão MVT, onde:
- **Model**: Define estrutura dos dados (models.py)
- **View**: Lógica de negócio (views.py, viewsets)
- **Template**: Apresentação (HTML com Django template language)

### 2. Repository Pattern
Usamos Django ORM como camada de abstração sobre o banco de dados.

### 3. Serializer Pattern
DRF Serializers convertem objetos Python ↔ JSON.

### 4. ViewSet Pattern
DRF ViewSets agrupam operações CRUD em uma classe.

### 5. Dependency Injection
Django utiliza injeção de dependência via middleware, signals e decorators.

### 6. Observer Pattern
Django Signals para eventos (pré/pós save, delete, etc).

## Escalabilidade

### Horizontal
- **Load Balancer**: Nginx ou AWS ALB
- **Multiple Instances**: Gunicorn workers
- **Database Replication**: MySQL Master-Slave

### Vertical
- **Cache Layer**: Redis para sessões e queries
- **CDN**: CloudFlare para assets estáticos
- **Background Tasks**: Celery + Redis

### Performance
- **Database Indexing**: Índices em campos de busca
- **Query Optimization**: Select/Prefetch related
- **Pagination**: DRF PageNumberPagination
- **Compression**: Gzip middleware

## Segurança

### Camadas de Proteção
1. **Firewall**: AWS Security Groups / iptables
2. **HTTPS**: Certificado SSL/TLS (Let's Encrypt)
3. **WAF**: AWS WAF ou CloudFlare (opcional)
4. **Rate Limiting**: DRF throttling
5. **Input Validation**: Serializers + Validators
6. **SQL Injection**: Django ORM (parameterized queries)
7. **XSS**: Django template auto-escaping
8. **CSRF**: Django CSRF tokens

### Autenticação e Autorização
```
┌─────────────────┐
│   JWT Token     │
├─────────────────┤
│ Header          │
│ - alg: HS256    │
│ - typ: JWT      │
├─────────────────┤
│ Payload         │
│ - user_id       │
│ - exp           │
│ - iat           │
├─────────────────┤
│ Signature       │
│ (SECRET_KEY)    │
└─────────────────┘
```

## Monitoramento e Logs

### Logs Estruturados
- **Application**: django.log (INFO, WARNING, ERROR)
- **Access**: access.log (requisições HTTP)
- **Error**: error.log (exceções e crashes)
- **Security**: security.log (tentativas de acesso)

### Métricas (Futuro)
- **APM**: New Relic ou Datadog
- **Uptime**: UptimeRobot ou Pingdom
- **Alertas**: Email/SMS em caso de erros críticos

## Backup e Recuperação

### Estratégia de Backup
- **Banco de Dados**: Dump diário (mysqldump)
- **Mídia**: Rsync para S3 ou storage externo
- **Código**: Git (GitHub)
- **Retenção**: 30 dias (diário), 12 meses (mensal)

### Disaster Recovery
- **RTO**: Recovery Time Objective < 4 horas
- **RPO**: Recovery Point Objective < 24 horas
- **Testes**: Simulação de restauração mensal

## Ambientes

### Desenvolvimento
- **Local**: SQLite + Django Dev Server
- **Debug**: DEBUG=True, logs verbosos
- **Data**: Fixtures e seed commands

### Staging (Futuro)
- **Docker**: Container similar à produção
- **MySQL**: Banco de dados isolado
- **Dados**: Cópia anonimizada da produção

### Produção
- **Docker**: Container otimizado
- **Gunicorn**: WSGI server
- **MySQL**: Banco principal
- **Monitoring**: Logs + métricas

---

**Versão**: 1.0  
**Última Atualização**: 23/11/2025  
**Autor**: Daniel 
**Projeto**: TCC - S.O.S Pets
