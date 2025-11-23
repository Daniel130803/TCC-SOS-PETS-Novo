# Documentação da API - S.O.S Pets

## Visão Geral

A API do S.O.S Pets é uma RESTful API construída com Django REST Framework que fornece endpoints para gerenciamento de adoções, pets perdidos, denúncias e muito mais.

**Base URL**: `http://localhost:8000/api/`  
**Versão**: 1.0  
**Formato**: JSON  
**Autenticação**: JWT (JSON Web Tokens)

---

## Índice

1. [Autenticação](#autenticação)
2. [Usuários](#usuários)
3. [Animais para Adoção](#animais-para-adoção)
4. [Solicitações de Adoção](#solicitações-de-adoção)
5. [Pets Perdidos](#pets-perdidos)
6. [Reportes de Pets Encontrados](#reportes-de-pets-encontrados)
7. [Denúncias](#denúncias)
8. [Notificações](#notificações)
9. [Contatos](#contatos)
10. [Códigos de Status](#códigos-de-status)
11. [Erros Comuns](#erros-comuns)

---

## Autenticação

### Obter Token JWT

**POST** `/api/auth/token/`

Autentica um usuário e retorna tokens de acesso e renovação.

#### Request Body
```json
{
  "username": "usuario@email.com",
  "password": "senha123"
}
```

#### Response (200 OK)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Uso do Token
Todas as requisições autenticadas devem incluir o header:
```
Authorization: Bearer <access_token>
```

### Renovar Token

**POST** `/api/auth/token/refresh/`

Renova o token de acesso usando o refresh token.

#### Request Body
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Response (200 OK)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Registro de Usuário

**POST** `/api/auth/register/`

Cria uma nova conta de usuário.

#### Request Body
```json
{
  "username": "usuario@email.com",
  "email": "usuario@email.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva"
}
```

#### Response (201 Created)
```json
{
  "id": 1,
  "username": "usuario@email.com",
  "email": "usuario@email.com",
  "first_name": "João",
  "last_name": "Silva"
}
```

---

## Usuários

### Obter Perfil do Usuário Logado

**GET** `/api/auth/me/`

Retorna informações do usuário autenticado.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200 OK)
```json
{
  "id": 1,
  "username": "usuario@email.com",
  "email": "usuario@email.com",
  "first_name": "João",
  "last_name": "Silva",
  "telefone": "(11) 98765-4321",
  "cpf": "123.456.789-00",
  "endereco": "Rua das Flores, 123",
  "data_nascimento": "1990-01-15"
}
```

### Atualizar Perfil

**PUT** `/api/auth/me/`

Atualiza informações do usuário autenticado.

#### Request Body
```json
{
  "first_name": "João Carlos",
  "telefone": "(11) 98765-4321",
  "endereco": "Rua Nova, 456"
}
```

#### Response (200 OK)
```json
{
  "id": 1,
  "username": "usuario@email.com",
  "first_name": "João Carlos",
  "telefone": "(11) 98765-4321",
  "endereco": "Rua Nova, 456"
}
```

---

## Animais para Adoção

### Listar Animais Disponíveis

**GET** `/api/animais-adocao/`

Lista todos os animais disponíveis para adoção.

#### Query Parameters
- `especie` (string): Filtrar por espécie (cachorro, gato, outro)
- `porte` (string): Filtrar por porte (pequeno, medio, grande)
- `sexo` (string): Filtrar por sexo (macho, femea)
- `estado` (string): Filtrar por estado (UF)
- `cidade` (string): Filtrar por cidade
- `page` (int): Número da página (padrão: 1)

#### Response (200 OK)
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/animais-adocao/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "nome": "Rex",
      "especie": "cachorro",
      "especie_display": "Cachorro",
      "raca": "Labrador",
      "idade_aproximada": "2 anos",
      "sexo": "macho",
      "sexo_display": "Macho",
      "porte": "grande",
      "porte_display": "Grande",
      "cor": "Amarelo",
      "peso_aproximado": "30.5",
      "vacinado": true,
      "castrado": true,
      "descricao": "Cão muito dócil e brincalhão",
      "caracteristicas_especiais": "Ama crianças, precisa de espaço",
      "imagem_principal_url": "http://localhost:8000/media/animais/rex.jpg",
      "fotos_adicionais": [
        {
          "id": 1,
          "imagem_url": "http://localhost:8000/media/animais/rex_2.jpg"
        }
      ],
      "estado": "SP",
      "cidade": "São Paulo",
      "bairro": "Jardins",
      "disponivel": true,
      "usuario": {
        "id": 2,
        "nome": "Maria Silva",
        "telefone": "(11) 98765-4321"
      },
      "data_cadastro": "2025-11-20T10:30:00Z"
    }
  ]
}
```

### Obter Animal Específico

**GET** `/api/animais-adocao/{id}/`

Retorna detalhes de um animal específico.

#### Response (200 OK)
```json
{
  "id": 1,
  "nome": "Rex",
  "especie": "cachorro",
  "raca": "Labrador",
  "idade_aproximada": "2 anos",
  "descricao": "Cão muito dócil e brincalhão",
  "imagem_principal_url": "http://localhost:8000/media/animais/rex.jpg",
  "fotos_adicionais": [],
  "vacinado": true,
  "castrado": true,
  "usuario": {
    "id": 2,
    "nome": "Maria Silva"
  }
}
```

### Cadastrar Animal para Adoção

**POST** `/api/animais-adocao/`

Cadastra um novo animal para adoção.

#### Headers
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### Request Body (multipart/form-data)
```
nome: Rex
especie: cachorro
raca: Labrador
idade_aproximada: 2 anos
sexo: macho
porte: grande
cor: Amarelo
peso_aproximado: 30.5
vacinado: true
castrado: true
descricao: Cão muito dócil e brincalhão
caracteristicas_especiais: Ama crianças
estado: SP
cidade: São Paulo
bairro: Jardins
imagem_principal: [arquivo]
fotos_adicionais: [arquivo1, arquivo2]
```

#### Response (201 Created)
```json
{
  "id": 1,
  "nome": "Rex",
  "especie": "cachorro",
  "imagem_principal_url": "http://localhost:8000/media/animais/rex.jpg",
  "data_cadastro": "2025-11-23T14:30:00Z"
}
```

### Atualizar Animal

**PUT** `/api/animais-adocao/{id}/`  
**PATCH** `/api/animais-adocao/{id}/`

Atualiza informações de um animal (somente o dono pode atualizar).

#### Response (200 OK)
```json
{
  "id": 1,
  "nome": "Rex Atualizado",
  "descricao": "Nova descrição"
}
```

### Deletar Animal

**DELETE** `/api/animais-adocao/{id}/`

Remove um animal (somente o dono pode deletar).

#### Response (204 No Content)

---

## Solicitações de Adoção

### Listar Solicitações Enviadas

**GET** `/api/solicitacoes-adocao/minhas-solicitacoes/`

Lista todas as solicitações de adoção enviadas pelo usuário logado.

#### Response (200 OK)
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "animal": {
        "id": 5,
        "nome": "Mel",
        "imagem_principal_url": "http://localhost:8000/media/animais/mel.jpg"
      },
      "status": "pendente",
      "status_display": "Pendente",
      "mensagem": "Gostaria de adotar a Mel",
      "data_solicitacao": "2025-11-20T10:00:00Z",
      "data_resposta": null,
      "resposta_dono": null
    }
  ]
}
```

### Listar Solicitações Recebidas

**GET** `/api/solicitacoes-adocao/solicitacoes-recebidas/`

Lista todas as solicitações recebidas para os animais do usuário.

#### Response (200 OK)
```json
{
  "count": 5,
  "results": [
    {
      "id": 2,
      "animal": {
        "id": 1,
        "nome": "Rex"
      },
      "solicitante": {
        "id": 3,
        "nome": "João Silva",
        "email": "joao@email.com",
        "telefone": "(11) 98765-4321"
      },
      "status": "pendente",
      "mensagem": "Tenho experiência com cães grandes",
      "data_solicitacao": "2025-11-21T15:30:00Z"
    }
  ]
}
```

### Criar Solicitação de Adoção

**POST** `/api/solicitacoes-adocao/`

Envia uma solicitação de adoção para um animal.

#### Request Body
```json
{
  "animal": 1,
  "mensagem": "Gostaria muito de adotar o Rex. Tenho quintal grande e experiência com cães."
}
```

#### Response (201 Created)
```json
{
  "id": 1,
  "animal": 1,
  "status": "pendente",
  "mensagem": "Gostaria muito de adotar o Rex",
  "data_solicitacao": "2025-11-23T14:30:00Z"
}
```

### Aprovar Solicitação

**POST** `/api/solicitacoes-adocao/{id}/aprovar/`

Aprova uma solicitação de adoção (somente o dono do animal).

#### Request Body
```json
{
  "resposta": "Aprovado! Entre em contato pelo telefone para agendar visita."
}
```

#### Response (200 OK)
```json
{
  "id": 1,
  "status": "aprovada",
  "resposta_dono": "Aprovado! Entre em contato pelo telefone",
  "data_resposta": "2025-11-23T15:00:00Z"
}
```

### Rejeitar Solicitação

**POST** `/api/solicitacoes-adocao/{id}/rejeitar/`

Rejeita uma solicitação de adoção.

#### Request Body
```json
{
  "resposta": "Infelizmente outro candidato foi selecionado."
}
```

#### Response (200 OK)
```json
{
  "id": 1,
  "status": "rejeitada",
  "resposta_dono": "Infelizmente outro candidato foi selecionado"
}
```

---

## Pets Perdidos

### Listar Pets Perdidos

**GET** `/api/pets-perdidos/`

Lista todos os pets perdidos ativos.

#### Query Parameters
- `ativo` (boolean): Filtrar por status ativo (padrão: true)
- `status` (string): perdido ou encontrado
- `especie` (string): cachorro, gato, outro
- `estado` (string): Sigla do estado (UF)
- `cidade` (string): Nome da cidade
- `raio_km` (float): Raio de busca em km (requer lat/lng)
- `latitude` (float): Latitude de referência
- `longitude` (float): Longitude de referência

#### Response (200 OK)
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "nome": "Atena",
      "especie": "cachorro",
      "especie_display": "Cachorro",
      "raca": "Vira-lata",
      "cor": "Preto",
      "porte": "pequeno",
      "porte_display": "Pequeno",
      "sexo": "femea",
      "sexo_display": "Fêmea",
      "idade_aproximada": "3 anos",
      "caracteristicas_distintivas": "Possui mancha branca na pata",
      "descricao": "Perdida no parque",
      "data_perda": "2025-11-20",
      "hora_perda": "21:19:00",
      "endereco": "rua tal, asd",
      "bairro": "goiania",
      "cidade": "goiania",
      "estado": "GO",
      "latitude": "-16.6799",
      "longitude": "-49.2550",
      "status": "perdido",
      "status_display": "Perdido",
      "oferece_recompensa": true,
      "valor_recompensa": "200.00",
      "telefone_contato": "(62) 98765-4321",
      "whatsapp": "(62) 98765-4321",
      "email_contato": "dono@email.com",
      "imagem_principal_url": "http://localhost:8000/media/pets/atena.jpg",
      "fotos_adicionais": [
        {
          "id": 1,
          "imagem_url": "http://localhost:8000/media/pets/atena_2.jpg"
        }
      ],
      "ativo": true,
      "usuario": {
        "id": 1,
        "nome": "Maria Santos"
      },
      "data_cadastro": "2025-11-20T21:30:00Z"
    }
  ]
}
```

### Obter Pet Perdido Específico

**GET** `/api/pets-perdidos/{id}/`

Retorna detalhes completos de um pet perdido.

#### Response (200 OK)
```json
{
  "id": 1,
  "nome": "Atena",
  "especie": "cachorro",
  "raca": "Vira-lata",
  "cor": "Preto",
  "caracteristicas_distintivas": "Possui mancha branca na pata",
  "data_perda": "2025-11-20",
  "hora_perda": "21:19:00",
  "endereco": "rua tal, asd",
  "cidade": "goiania",
  "estado": "GO",
  "latitude": "-16.6799",
  "longitude": "-49.2550",
  "telefone_contato": "(62) 98765-4321",
  "oferece_recompensa": true,
  "valor_recompensa": "200.00",
  "imagem_principal_url": "http://localhost:8000/media/pets/atena.jpg"
}
```

### Registrar Pet Perdido

**POST** `/api/pets-perdidos/`

Registra um pet como perdido.

#### Headers
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### Request Body (multipart/form-data)
```
nome: Atena
especie: cachorro
raca: Vira-lata
cor: Preto
porte: pequeno
sexo: femea
idade_aproximada: 3 anos
caracteristicas_distintivas: Mancha branca na pata
descricao: Perdida no parque próximo à casa
data_perda: 2025-11-20
hora_perda: 21:19:00
endereco: Rua das Flores, 123
bairro: Centro
cidade: Goiânia
estado: GO
latitude: -16.6799
longitude: -49.2550
oferece_recompensa: true
valor_recompensa: 200.00
telefone_contato: (62) 98765-4321
whatsapp: (62) 98765-4321
email_contato: dono@email.com
imagem_principal: [arquivo]
fotos_adicionais: [arquivo1, arquivo2]
ativo: true
status: perdido
```

#### Response (201 Created)
```json
{
  "id": 1,
  "nome": "Atena",
  "status": "perdido",
  "data_cadastro": "2025-11-23T14:30:00Z",
  "imagem_principal_url": "http://localhost:8000/media/pets/atena.jpg"
}
```

### Atualizar Pet Perdido

**PUT/PATCH** `/api/pets-perdidos/{id}/`

Atualiza informações do pet perdido (somente o dono).

#### Response (200 OK)

### Marcar como Encontrado

**POST** `/api/pets-perdidos/{id}/marcar_encontrado/`

Marca um pet como encontrado.

#### Response (200 OK)
```json
{
  "id": 1,
  "status": "encontrado",
  "ativo": false
}
```

### Buscar Matches (Pets Similares)

**GET** `/api/pets-perdidos/{id}/buscar_matches/`

Busca pets reportados como encontrados que possam ser matches.

#### Response (200 OK)
```json
{
  "matches": [
    {
      "id": 5,
      "nome": "Pet Encontrado",
      "similaridade": 85.5,
      "distancia_km": 2.3,
      "imagem_url": "http://localhost:8000/media/pets/encontrado.jpg",
      "contato": {
        "telefone": "(62) 99999-8888",
        "email": "encontrou@email.com"
      }
    }
  ]
}
```

---

## Reportes de Pets Encontrados

### Listar Pets Encontrados

**GET** `/api/pets-encontrados/`

Lista reportes de pets encontrados.

#### Query Parameters
- `especie` (string)
- `estado` (string)
- `cidade` (string)

#### Response (200 OK)
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "descricao": "Encontrei um cachorro preto no parque",
      "especie": "cachorro",
      "cor": "Preto",
      "porte": "pequeno",
      "data_encontrado": "2025-11-21",
      "hora_encontrado": "10:30:00",
      "endereco": "Parque Central",
      "cidade": "Goiânia",
      "estado": "GO",
      "latitude": "-16.6850",
      "longitude": "-49.2600",
      "imagem_principal_url": "http://localhost:8000/media/pets/encontrado.jpg",
      "telefone_contato": "(62) 99999-8888"
    }
  ]
}
```

### Reportar Pet Encontrado

**POST** `/api/pets-encontrados/`

Reporta que encontrou um pet.

#### Request Body (multipart/form-data)
```
descricao: Encontrei um cachorro preto no parque
especie: cachorro
cor: Preto
porte: pequeno
data_encontrado: 2025-11-21
hora_encontrado: 10:30
endereco: Parque Central
cidade: Goiânia
estado: GO
latitude: -16.6850
longitude: -49.2600
telefone_contato: (62) 99999-8888
imagem_principal: [arquivo]
status: encontrado
```

#### Response (201 Created)
```json
{
  "id": 1,
  "descricao": "Encontrei um cachorro preto",
  "data_cadastro": "2025-11-23T14:30:00Z"
}
```

---

## Denúncias

### Listar Denúncias do Usuário

**GET** `/api/denuncias/minhas_denuncias/`

Lista denúncias criadas pelo usuário logado.

#### Response (200 OK)
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "tipo_denuncia": "maus_tratos",
      "tipo_denuncia_display": "Maus-tratos",
      "descricao": "Animal sendo maltratado",
      "status": "em_analise",
      "status_display": "Em análise",
      "data_ocorrencia": "2025-11-20T15:00:00Z",
      "anonima": false,
      "protocolo": "DEN-20251120-001"
    }
  ]
}
```

### Criar Denúncia

**POST** `/api/denuncias/`

Cria uma nova denúncia.

#### Request Body (multipart/form-data)
```
tipo_denuncia: maus_tratos
categoria: abandono
descricao: Observei animal sendo maltratado
endereco: Rua X, 123
cidade: São Paulo
estado: SP
data_ocorrencia: 2025-11-20T15:00:00Z
anonima: false
nome_denunciante: João Silva
email_denunciante: joao@email.com
telefone_denunciante: (11) 98765-4321
imagens: [arquivo1, arquivo2]
videos: [arquivo1]
```

#### Response (201 Created)
```json
{
  "id": 1,
  "protocolo": "DEN-20251120-001",
  "tipo_denuncia": "maus_tratos",
  "status": "pendente",
  "data_criacao": "2025-11-23T14:30:00Z"
}
```

### Obter Status da Denúncia

**GET** `/api/denuncias/{id}/`

Retorna detalhes e histórico da denúncia.

#### Response (200 OK)
```json
{
  "id": 1,
  "protocolo": "DEN-20251120-001",
  "tipo_denuncia": "maus_tratos",
  "status": "em_analise",
  "descricao": "Animal sendo maltratado",
  "historico": [
    {
      "id": 1,
      "status_anterior": "pendente",
      "status_novo": "em_analise",
      "observacoes": "Denúncia em análise pela equipe",
      "data_mudanca": "2025-11-21T10:00:00Z"
    }
  ]
}
```

---

## Notificações

### Listar Notificações

**GET** `/api/notificacoes/`

Lista notificações do usuário logado.

#### Query Parameters
- `lida` (boolean): Filtrar por lidas/não lidas
- `tipo` (string): Tipo de notificação

#### Response (200 OK)
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "tipo": "solicitacao_adocao",
      "titulo": "Nova Solicitação de Adoção",
      "mensagem": "João Silva enviou uma solicitação para adotar Rex",
      "lida": false,
      "link": "/api/solicitacoes-adocao/1/",
      "data_criacao": "2025-11-23T14:00:00Z"
    }
  ]
}
```

### Marcar Notificação como Lida

**POST** `/api/notificacoes/{id}/marcar_lida/`

Marca uma notificação como lida.

#### Response (200 OK)
```json
{
  "id": 1,
  "lida": true
}
```

### Marcar Todas como Lidas

**POST** `/api/notificacoes/marcar_todas_lidas/`

Marca todas as notificações como lidas.

#### Response (200 OK)
```json
{
  "message": "Todas as notificações foram marcadas como lidas",
  "count": 5
}
```

---

## Contatos

### Enviar Mensagem de Contato

**POST** `/api/contatos/`

Envia uma mensagem de contato para a equipe.

#### Request Body
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "telefone": "(11) 98765-4321",
  "assunto": "Dúvida sobre adoção",
  "mensagem": "Gostaria de saber mais sobre o processo de adoção"
}
```

#### Response (201 Created)
```json
{
  "id": 1,
  "protocolo": "CONT-20251123-001",
  "nome": "João Silva",
  "assunto": "Dúvida sobre adoção",
  "status": "pendente",
  "data_envio": "2025-11-23T14:30:00Z"
}
```

---

## Códigos de Status

### Códigos de Sucesso
- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `204 No Content` - Requisição bem-sucedida sem conteúdo de retorno

### Códigos de Erro do Cliente
- `400 Bad Request` - Dados inválidos na requisição
- `401 Unauthorized` - Autenticação necessária
- `403 Forbidden` - Acesso negado
- `404 Not Found` - Recurso não encontrado
- `409 Conflict` - Conflito de dados

### Códigos de Erro do Servidor
- `500 Internal Server Error` - Erro interno do servidor
- `503 Service Unavailable` - Serviço temporariamente indisponível

---

## Erros Comuns

### Erro de Validação (400)
```json
{
  "nome": ["Este campo é obrigatório"],
  "email": ["Insira um endereço de email válido"],
  "telefone": ["Formato inválido. Use: (XX) XXXXX-XXXX"]
}
```

### Erro de Autenticação (401)
```json
{
  "detail": "As credenciais de autenticação não foram fornecidas."
}
```

```json
{
  "detail": "Token inválido ou expirado"
}
```

### Erro de Permissão (403)
```json
{
  "detail": "Você não tem permissão para executar esta ação."
}
```

### Erro Não Encontrado (404)
```json
{
  "detail": "Não encontrado."
}
```

### Erro de Servidor (500)
```json
{
  "detail": "Erro interno do servidor. Tente novamente mais tarde."
}
```

---

## Paginação

A API utiliza paginação padrão do Django REST Framework.

### Parâmetros de Paginação
- `page` (int): Número da página (padrão: 1)
- `page_size` (int): Itens por página (padrão: 12, máximo: 100)

### Resposta Paginada
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/animais-adocao/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Rate Limiting

A API implementa rate limiting para prevenir abuso:

- **Usuários Anônimos**: 100 requisições/hora
- **Usuários Autenticados**: 1000 requisições/hora

### Headers de Rate Limit
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1637683200
```

---

## CORS

A API permite requisições de origens específicas configuradas no backend.

### Headers CORS
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Versionamento

A API não possui versionamento explícito na URL atualmente. Mudanças breaking serão comunicadas com antecedência.

**Versão Atual**: 1.0  
**Breaking Changes**: Nenhum planejado

---

## Documentação Interativa

### Swagger UI
Acesse a documentação interativa em:
```
http://localhost:8000/api/schema/swagger-ui/
```

### ReDoc
Documentação alternativa em:
```
http://localhost:8000/api/schema/redoc/
```

### OpenAPI Schema
Schema JSON disponível em:
```
http://localhost:8000/api/schema/
```

---

## Exemplos de Uso

### cURL

#### Autenticação
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario@email.com","password":"senha123"}'
```

#### Listar Animais
```bash
curl http://localhost:8000/api/animais-adocao/ \
  -H "Authorization: Bearer <access_token>"
```

#### Criar Pet Perdido
```bash
curl -X POST http://localhost:8000/api/pets-perdidos/ \
  -H "Authorization: Bearer <access_token>" \
  -F "nome=Atena" \
  -F "especie=cachorro" \
  -F "cor=Preto" \
  -F "cidade=Goiania" \
  -F "estado=GO" \
  -F "latitude=-16.6799" \
  -F "longitude=-49.2550" \
  -F "imagem_principal=@atena.jpg"
```

### JavaScript (Fetch API)

```javascript
// Autenticação
const login = async () => {
  const response = await fetch('http://localhost:8000/api/auth/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'usuario@email.com',
      password: 'senha123'
    })
  });
  const data = await response.json();
  localStorage.setItem('access', data.access);
  localStorage.setItem('refresh', data.refresh);
};

// Listar Animais
const getAnimals = async () => {
  const token = localStorage.getItem('access');
  const response = await fetch('http://localhost:8000/api/animais-adocao/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.results;
};

// Criar Solicitação de Adoção
const createAdoptionRequest = async (animalId, message) => {
  const token = localStorage.getItem('access');
  const response = await fetch('http://localhost:8000/api/solicitacoes-adocao/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      animal: animalId,
      mensagem: message
    })
  });
  return await response.json();
};
```

### Python (requests)

```python
import requests

# Autenticação
def login(username, password):
    url = 'http://localhost:8000/api/auth/token/'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    tokens = response.json()
    return tokens['access'], tokens['refresh']

# Listar Animais
def get_animals(token):
    url = 'http://localhost:8000/api/animais-adocao/'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()['results']

# Criar Pet Perdido
def create_lost_pet(token, data, image_path):
    url = 'http://localhost:8000/api/pets-perdidos/'
    headers = {'Authorization': f'Bearer {token}'}
    files = {'imagem_principal': open(image_path, 'rb')}
    response = requests.post(url, headers=headers, data=data, files=files)
    return response.json()
```

---

## Suporte

Para dúvidas ou problemas com a API:

- **Email**: suporte@sospets.com
- **GitHub Issues**: https://github.com/Daniel130803/TCC-SOS-PETS-Novo/issues
- **Documentação**: https://github.com/Daniel130803/TCC-SOS-PETS-Novo/blob/main/API_DOCS.md

---

**Última Atualização**: 23/11/2025  
**Versão**: 1.0  
**Autor**: Daniel 
**Projeto**: TCC - S.O.S Pets
