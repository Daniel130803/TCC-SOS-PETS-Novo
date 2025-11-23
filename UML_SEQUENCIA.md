# Diagramas UML - Sequência
## S.O.S Pets

---

## 1. Visão Geral

Este documento apresenta os diagramas de sequência completos do sistema S.O.S Pets. Os diagramas mostram a interação temporal entre atores, frontend, backend e banco de dados em todos os fluxos principais da aplicação.

### Fluxos Documentados
1. **Autenticação**: Registro de Usuário e Login com JWT
2. **Adoção**: Cadastro de Animal, Solicitação e Aprovação
3. **Pets Perdidos**: Reportar pet perdido com geolocalização
4. **Pets Encontrados**: Reportar pet encontrado com matching automático
5. **Denúncias**: Criar denúncia com protocolo único

---

## 2. Registro de Usuário

### Descrição
Fluxo completo de registro de novo usuário no sistema, incluindo validações frontend, criação de User e Usuario, e geração de token JWT.

### Atores
- **Visitante**: Usuário não autenticado
- **Frontend**: Interface web (registro.html/js)
- **Backend**: API Django REST Framework
- **Database**: MySQL

### Diagrama

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Visitante │      │ Frontend │      │ Backend  │      │ Database │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                  │                  │
     │ 1. Acessa       │                  │                  │
     │ /registro       │                  │                  │
     │────────────────>│                  │                  │
     │                 │                  │                  │
     │                 │ 2. Renderiza     │                  │
     │                 │    formulário    │                  │
     │<────────────────│                  │                  │
     │                 │                  │                  │
     │ 3. Preenche dados│                 │                  │
     │    (nome, email, │                 │                  │
     │     senha, etc)  │                 │                  │
     │────────────────>│                  │                  │
     │                 │                  │                  │
     │                 │ 4. Validação     │                  │
     │                 │    Frontend      │                  │
     │                 │    (validations.js)│                │
     │                 │    - Email válido│                  │
     │                 │    - Senha >= 6  │                  │
     │                 │    - Confirmar   │                  │
     │                 │      senha       │                  │
     │                 │    - Telefone BR │                  │
     │                 │                  │                  │
     │                 │ [Se inválido]    │                  │
     │ 5. Toast Erro   │                  │                  │
     │<────────────────│                  │                  │
     │                 │                  │                  │
     │                 │ [Se válido]      │                  │
     │                 │ 6. POST /api/auth/register/        │
     │                 │    {              │                  │
     │                 │      username,    │                  │
     │                 │      email,       │                  │
     │                 │      password,    │                  │
     │                 │      first_name,  │                  │
     │                 │      last_name,   │                  │
     │                 │      telefone     │                  │
     │                 │    }              │                  │
     │                 │──────────────────>│                  │
     │                 │                  │                  │
     │                 │                  │ 7. Sanitização   │
     │                 │                  │    (utils.py)    │
     │                 │                  │    - HTML tags   │
     │                 │                  │    - Scripts XSS │
     │                 │                  │                  │
     │                 │                  │ 8. Validação     │
     │                 │                  │    Serializer    │
     │                 │                  │    - Email único │
     │                 │                  │    - Username    │
     │                 │                  │      único       │
     │                 │                  │                  │
     │                 │                  │ 9. BEGIN         │
     │                 │                  │    TRANSACTION   │
     │                 │                  │─────────────────>│
     │                 │                  │                  │
     │                 │                  │ 10. CREATE User  │
     │                 │                  │     - username   │
     │                 │                  │     - email      │
     │                 │                  │     - password   │
     │                 │                  │       (hashed)   │
     │                 │                  │─────────────────>│
     │                 │                  │                  │
     │                 │                  │ 11. User ID      │
     │                 │                  │<─────────────────│
     │                 │                  │                  │
     │                 │                  │ 12. CREATE       │
     │                 │                  │     Usuario      │
     │                 │                  │     - user_id    │
     │                 │                  │     - telefone   │
     │                 │                  │─────────────────>│
     │                 │                  │                  │
     │                 │                  │ 13. Usuario ID   │
     │                 │                  │<─────────────────│
     │                 │                  │                  │
     │                 │                  │ 14. COMMIT       │
     │                 │                  │─────────────────>│
     │                 │                  │                  │
     │                 │                  │ 15. Gera JWT     │
     │                 │                  │     Token        │
     │                 │                  │     - access     │
     │                 │                  │     - refresh    │
     │                 │                  │                  │
     │                 │ 16. 201 Created  │                  │
     │                 │     {            │                  │
     │                 │       access,    │                  │
     │                 │       refresh,   │                  │
     │                 │       user: {...}│                  │
     │                 │     }            │                  │
     │                 │<──────────────────│                  │
     │                 │                  │                  │
     │                 │ 17. Salva tokens │                  │
     │                 │     localStorage │                  │
     │                 │                  │                  │
     │ 18. Toast       │                  │                  │
     │     "Cadastro   │                  │                  │
     │     realizado!" │                  │                  │
     │<────────────────│                  │                  │
     │                 │                  │                  │
     │                 │ 19. Redirect     │                  │
     │                 │     para /       │                  │
     │<────────────────│                  │                  │
     │                 │                  │                  │

[FLUXO ALTERNATIVO - Erro]

     │                 │                  │ [Erro: Email já  │
     │                 │                  │  existe]         │
     │                 │                  │ ROLLBACK         │
     │                 │                  │─────────────────>│
     │                 │ 400 Bad Request  │                  │
     │                 │ { email: ["Já existe"] }            │
     │                 │<──────────────────│                  │
     │ Toast Erro      │                  │                  │
     │ "Email já cadastrado"               │                  │
     │<────────────────│                  │                  │
```

### Pontos-Chave
- **Validação Dupla**: Frontend (UX) + Backend (segurança)
- **Sanitização**: Remove HTML/scripts maliciosos
- **Transação Atômica**: User + Usuario criados juntos ou nenhum
- **JWT**: Access token (15min) + Refresh token (7 dias)
- **Hash de Senha**: PBKDF2+SHA256 com 260.000 iterações

---

## 3. Login com JWT

### Descrição
Processo de autenticação de usuário existente usando JWT (JSON Web Tokens).

### Diagrama

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Visitante │      │ Frontend │      │ Backend  │      │ Database │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                  │                  │
     │ 1. Acessa /login│                  │                  │
     │────────────────>│                  │                  │
     │                 │ 2. Renderiza formulário             │
     │<────────────────│                  │                  │
     │ 3. Preenche username + password    │                  │
     │────────────────>│                  │                  │
     │                 │ 4. POST /api/auth/token/           │
     │                 │──────────────────>│                  │
     │                 │                  │ 5. SELECT User   │
     │                 │                  │    WHERE username=?
     │                 │                  │─────────────────>│
     │                 │                  │ 6. User data     │
     │                 │                  │<─────────────────│
     │                 │                  │ 7. Verifica senha│
     │                 │                  │    (PBKDF2)      │
     │                 │                  │ 8. Gera JWT      │
     │                 │                  │    - access      │
     │                 │                  │    - refresh     │
     │                 │ 9. 200 OK {access, refresh}        │
     │                 │<──────────────────│                  │
     │                 │ 10. Salva tokens localStorage       │
     │                 │ 11. GET /api/auth/me/              │
     │                 │     Header: Bearer {token}         │
     │                 │──────────────────>│                  │
     │                 │                  │ 12. Valida JWT   │
     │                 │                  │ 13. SELECT Usuario│
     │                 │                  │─────────────────>│
     │                 │                  │ 14. User data    │
     │                 │                  │<─────────────────│
     │                 │ 15. 200 OK {id, username, email...}│
     │                 │<──────────────────│                  │
     │                 │ 16. Atualiza header UI              │
     │ 17. Redirect para /                 │                  │
     │<────────────────│                  │                  │

[FLUXO ALTERNATIVO - Credenciais Inválidas]

     │                 │                  │ [Senha incorreta]│
     │                 │ 401 Unauthorized │                  │
     │                 │ {detail: "Credenciais inválidas"}   │
     │                 │<──────────────────│                  │
     │ Toast Erro "Usuário ou senha incorretos"              │
     │<────────────────│                  │                  │
```

### Pontos-Chave
- **SimpleJWT**: Biblioteca padrão Django para JWT
- **Verificação de Senha**: Compara hash PBKDF2
- **Dois Tokens**: Access (requisições) + Refresh (renovar access)
- **Busca Perfil**: GET /auth/me/ retorna dados completos do usuário

---

## 4. Cadastro de Animal para Adoção

### Descrição
Fluxo completo de cadastro de animal para adoção, incluindo upload de múltiplas fotos, geolocalização e validações em múltiplas camadas.

### Diagrama

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ Doador   │      │ Frontend │      │ Backend  │      │ Database │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                  │                  │
     │ 1. Click "Cadastrar Pet"           │                  │
     │────────────────>│                  │                  │
     │                 │ 2. Verifica autenticação (JWT)      │
     │                 │ [Não autenticado] → Redirect /login │
     │                 │ [Autenticado] → Abre modal          │
     │<────────────────│                  │                  │
     │ 5. Preenche formulário:            │                  │
     │    - Nome, Espécie, Raça, Idade    │                  │
     │    - Sexo, Porte, Descrição        │                  │
     │    - Vacinado, Castrado, Adestrado │                  │
     │    - Temperamento                  │                  │
     │────────────────>│                  │                  │
     │ 6. Seleciona múltiplas fotos (até 10)                 │
     │────────────────>│                  │                  │
     │                 │ 7. Validação Frontend               │
     │                 │    - JPG, PNG                       │
     │                 │    - Max 5MB cada                   │
     │ 8. Click "Usar minha localização"  │                  │
     │────────────────>│                  │                  │
     │                 │ 9. navigator.geolocation.getCurrentPosition
     │ 10. Permissão concedida            │                  │
     │<────────────────│                  │                  │
     │                 │ 11. Recebe coords (lat, lng)        │
     │                 │ 12. Geocoding Reverso (Nominatim)  │
     │                 │     lat/lng → cidade/estado         │
     │                 │ 13. Preenche campos automaticamente │
     │<────────────────│                  │                  │
     │ 14. Click "Cadastrar"              │                  │
     │────────────────>│                  │                  │
     │                 │ 15. Cria FormData (multipart)       │
     │                 │ 16. POST /api/animais-adocao/      │
     │                 │     Header: JWT                     │
     │                 │──────────────────>│                  │
     │                 │                  │ 17. Valida JWT → user_id
     │                 │                  │ 18. Sanitiza inputs
     │                 │                  │ 19. Validação Serializer
     │                 │                  │ 20. Valida fotos (MIME)
     │                 │                  │ 21. BEGIN TRANSACTION
     │                 │                  │─────────────────>│
     │                 │                  │ 22. CREATE Animal│
     │                 │                  │─────────────────>│
     │                 │                  │ 23. Animal ID    │
     │                 │                  │<─────────────────│
     │                 │                  │ 24. CREATE AnimalParaAdocao
     │                 │                  │─────────────────>│
     │                 │                  │ 25. AnimalParaAdocao ID
     │                 │                  │<─────────────────│
     │                 │                  │ 26. Loop fotos   │
     │                 │                  │     CREATE AnimalFoto (N)
     │                 │                  │─────────────────>│
     │                 │                  │ 27. Foto IDs     │
     │                 │                  │<─────────────────│
     │                 │                  │ 28. COMMIT       │
     │                 │                  │─────────────────>│
     │                 │ 29. 201 Created {id, nome, fotos...}
     │                 │<──────────────────│                  │
     │                 │ 30. Fecha modal, recarrega galeria  │
     │ 32. Toast "Animal cadastrado com sucesso!"            │
     │<────────────────│                  │                  │
```

### Pontos-Chave
- **Multipart/form-data**: Upload de arquivos com FormData
- **Geolocalização**: API Geolocation + Nominatim (geocoding reverso)
- **Validação MIME**: Verifica tipo real do arquivo, não apenas extensão
- **Transação**: 3+ registros (Animal, AnimalParaAdocao, N AnimalFoto)
- **Até 10 fotos**: Máximo 5MB cada, JPG/PNG

---

## 5. Solicitação de Adoção

### Descrição
Fluxo de solicitação de adoção por um adotante interessado, com regras de negócio específicas.

### Diagrama

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ Adotante │      │ Frontend │      │ Backend  │      │ Database │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                  │                  │
     │ 1. Navega galeria adoção           │                  │
     │────────────────>│                  │                  │
     │                 │ 2. GET /api/animais-adocao/        │
     │                 │──────────────────>│                  │
     │                 │                  │ 3. SELECT AnimalParaAdocao
     │                 │                  │    WHERE adotado=false
     │                 │                  │─────────────────>│
     │                 │ 5. 200 OK {results: []}            │
     │                 │<──────────────────│                  │
     │                 │ 6. Renderiza cards │                  │
     │<────────────────│                  │                  │
     │ 7. Click "Ver Detalhes"            │                  │
     │────────────────>│                  │                  │
     │                 │ 8. Abre modal com info completa     │
     │<────────────────│                  │                  │
     │ 9. Click "Quero Adotar"            │                  │
     │────────────────>│                  │                  │
     │                 │ 10. Verifica autenticação           │
     │                 │ [Não autenticado] → Redirect /login │
     │                 │ [Autenticado] → Abre modal solicitação
     │<────────────────│                  │                  │
     │ 13. Escreve mensagem ao doador     │                  │
     │────────────────>│                  │                  │
     │ 14. Click "Enviar Solicitação"     │                  │
     │────────────────>│                  │                  │
     │                 │ 15. POST /api/solicitacoes-adocao/ │
     │                 │     {animal_id, mensagem}          │
     │                 │     Header: JWT                     │
     │                 │──────────────────>│                  │
     │                 │                  │ 16. Valida JWT   │
     │                 │                  │ 17. Verifica se é dono
     │                 │                  │─────────────────>│
     │                 │                  │ [É dono] → 400 "Não pode adotar próprio pet"
     │                 │                  │ [Não é dono]     │
     │                 │                  │ 19. Verifica solicitação existente
     │                 │                  │─────────────────>│
     │                 │                  │ [Já solicitou] → 400 "Solicitação pendente"
     │                 │                  │ [Primeira vez]   │
     │                 │                  │ 21. Sanitiza mensagem
     │                 │                  │ 22. BEGIN TRANSACTION
     │                 │                  │─────────────────>│
     │                 │                  │ 23. CREATE SolicitacaoAdocao
     │                 │                  │     - status: pendente
     │                 │                  │─────────────────>│
     │                 │                  │ 25. CREATE Notificacao
     │                 │                  │     - usuario: dono
     │                 │                  │     - tipo: solicitacao_adocao
     │                 │                  │─────────────────>│
     │                 │                  │ 27. COMMIT       │
     │                 │                  │─────────────────>│
     │                 │ 28. 201 Created  │                  │
     │                 │<──────────────────│                  │
     │ 30. Toast "Solicitação enviada!"   │                  │
     │<────────────────│                  │                  │
```

### Regras de Negócio
1. ❌ **Não pode solicitar próprio animal**
2. ❌ **Apenas uma solicitação ativa por usuário por animal**
3. ✅ **Notificação automática para o doador**
4. ✅ **Status inicial: "pendente"**

---

## 6. Reportar Pet Perdido

### Descrição
Fluxo de cadastro de pet perdido com geolocalização, pin vermelho no mapa Leaflet.js e upload de múltiplas fotos.

### Diagrama

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   Dono   │   │ Frontend │   │Leaflet.js│   │ Backend  │   │ Database │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │              │
     │ 1. Acessa /pets-perdidos    │              │              │
     │─────────────>│              │              │              │
     │              │ 2. Inicializa mapa          │              │
     │              │─────────────>│              │              │
     │              │              │ 3. Carrega tiles OSM        │
     │              │<─────────────│              │              │
     │              │ 4. GET /api/pets-perdidos/  │              │
     │              │─────────────────────────────>│              │
     │              │              │              │ 5. SELECT WHERE ativo=true
     │              │              │              │─────────────>│
     │              │ 7. 200 OK {results:[]}      │              │
     │              │<─────────────────────────────│              │
     │              │ 8. Adiciona pins vermelhos  │              │
     │              │─────────────>│              │              │
     │<─────────────│              │              │              │
     │ 9. Click "Reportar Pet Perdido"            │              │
     │─────────────>│              │              │              │
     │              │ 10. Abre modal              │              │
     │<─────────────│              │              │              │
     │ 11. Preenche dados: Nome, Espécie, Raça...│              │
     │─────────────>│              │              │              │
     │ 12. Click "Selecionar local no mapa"       │              │
     │─────────────>│              │              │              │
     │              │ 13. Ativa modo seleção      │              │
     │              │─────────────>│              │              │
     │ 14. Click no mapa           │              │              │
     │─────────────────────────────>│              │              │
     │              │              │ 15. Retorna lat/lng         │
     │              │<─────────────│              │              │
     │              │ 16. Geocoding Reverso (Nominatim)          │
     │              │     lat/lng → endereço      │              │
     │              │ 17. Preenche cidade/estado  │              │
     │<─────────────│              │              │              │
     │ 18. Upload fotos (até 10)   │              │              │
     │─────────────>│              │              │              │
     │              │ 19. Preview thumbnails      │              │
     │<─────────────│              │              │              │
     │ 20. Informa recompensa (opcional)          │              │
     │─────────────>│              │              │              │
     │ 21. Click "Reportar"        │              │              │
     │─────────────>│              │              │              │
     │              │ 22. FormData multipart      │              │
     │              │ 23. POST /api/pets-perdidos/│              │
     │              │     Header: JWT             │              │
     │              │─────────────────────────────>│              │
     │              │              │              │ 24. Valida JWT
     │              │              │              │ 25. Sanitiza inputs
     │              │              │              │ 26. Valida fotos
     │              │              │              │ 27. BEGIN    │
     │              │              │              │─────────────>│
     │              │              │              │ 28. CREATE PetPerdido
     │              │              │              │─────────────>│
     │              │              │              │ 30. Loop fotos
     │              │              │              │     CREATE PetPerdidoFoto
     │              │              │              │─────────────>│
     │              │              │              │ 31. COMMIT   │
     │              │              │              │─────────────>│
     │              │ 32. 201 Created {id, nome...}              │
     │              │<─────────────────────────────│              │
     │              │ 33. Adiciona pin VERMELHO no mapa          │
     │              │─────────────>│              │              │
     │ 35. Toast "Pet perdido reportado!"         │              │
     │<─────────────│              │              │              │
```

### Pontos-Chave
- **Leaflet.js**: Biblioteca de mapas interativos
- **OpenStreetMap**: Tiles gratuitos do mapa
- **Pin Vermelho**: Indica pet perdido no mapa
- **Recompensa Opcional**: Campo monetário para incentivar busca
- **Geolocalização**: Latitude/longitude armazenadas para matching

---

## 7. Reportar Pet Encontrado (com Matching Automático)

### Descrição
Fluxo de reporte de pet encontrado com algoritmo de matching automático que busca pets perdidos próximos geograficamente.

### Diagrama

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│Encontrou │   │ Frontend │   │ Backend  │   │ Database │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     │ 1. Click "Reportar Pet Encontrado"         │
     │─────────────>│              │              │
     │              │ 2. Abre modal│              │
     │<─────────────│              │              │
     │ 3. Preenche descrição (Espécie, Porte, Sexo, Cor...)
     │─────────────>│              │              │
     │ 4. Upload fotos              │              │
     │─────────────>│              │              │
     │ 5. Seleciona local no mapa  │              │
     │─────────────>│              │              │
     │              │ 6. Captura lat/lng           │
     │ 7. Click "Reportar"         │              │
     │─────────────>│              │              │
     │              │ 8. POST /api/pets-encontrados/
     │              │    Header: JWT│              │
     │              │─────────────>│              │
     │              │              │ 9. Valida JWT│
     │              │              │ 10. BEGIN    │
     │              │              │─────────────>│
     │              │              │ 11. CREATE ReportePetEncontrado
     │              │              │─────────────>│
     │              │              │ 13. Loop fotos
     │              │              │     CREATE ReportePetEncontradoFoto
     │              │              │─────────────>│
     │              │              │              │
     │              │              │ 14. MATCHING AUTOMÁTICO
     │              │              │ ┌──────────────────┐
     │              │              │ │ 1. SELECT        │
     │              │              │ │    PetPerdido    │
     │              │              │ │    WHERE         │
     │              │              │ │    ativo=true    │
     │              │              │ │    AND estado=?  │
     │              │              │ │                  │
     │              │              │ │ 2. Para cada pet:│
     │              │              │ │    - Calc distância│
     │              │              │ │      Haversine   │
     │              │              │ │    - Se <= 10km: │
     │              │              │ │      Score:      │
     │              │              │ │      Espécie=40% │
     │              │              │ │      Porte=30%   │
     │              │              │ │      Sexo=30%    │
     │              │              │ │                  │
     │              │              │ │ 3. Se score>=50%:│
     │              │              │ │    CREATE        │
     │              │              │ │    Notificacao   │
     │              │              │ │    para dono     │
     │              │              │ └──────────────────┘
     │              │              │─────────────>│
     │              │              │ 21. COMMIT   │
     │              │              │─────────────>│
     │              │ 22. 201 Created              │
     │              │     {                        │
     │              │       id,                    │
     │              │       matches: [             │
     │              │         {pet, score, distancia_km}
     │              │       ]                      │
     │              │     }                        │
     │              │<─────────────│              │
     │              │ 23. Adiciona pin VERDE no mapa
     │              │ 24. Exibe matches encontrados│
     │<─────────────│              │              │
     │ 25. Toast "X possíveis matches encontrados!"
     │<─────────────│              │              │
```

### Algoritmo de Matching

**Fórmula Haversine (Distância):**
```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
c = 2 × atan2(√a, √(1−a))
d = R × c  (R = 6371 km)
```

**Score de Similaridade:**
- Espécie igual: +40 pontos
- Porte igual: +30 pontos
- Sexo igual: +30 pontos
- **Threshold**: Notifica se score >= 50%

**Critérios:**
1. ✅ Pet perdido ativo (ativo=true)
2. ✅ Mesmo estado
3. ✅ Distância <= 10km
4. ✅ Score >= 50%

### Pontos-Chave
- **Pin Verde**: Indica pet encontrado no mapa
- **Matching Automático**: Executado ao criar reporte
- **Notificações**: Donos de pets com match recebem alerta
- **Score Visual**: Frontend exibe % de similaridade
- **Raio de Busca**: 10km (Haversine)

---

## 8. Criar Denúncia

### Descrição
Fluxo de criação de denúncia anônima ou nominada com protocolo único para rastreamento.

### Diagrama

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│Denunciante│     │ Frontend │      │ Backend  │      │ Database │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                  │                  │
     │ 1. Acessa /denuncia                │                  │
     │────────────────>│                  │                  │
     │                 │ 2. Renderiza formulário             │
     │<────────────────│                  │                  │
     │ 3. Preenche:    │                  │                  │
     │    - Tipo (maus-tratos, abandono, agressao...)        │
     │    - Descrição, Endereço, Cidade, Estado              │
     │────────────────>│                  │                  │
     │ 4. Seleciona local no mapa         │                  │
     │────────────────>│                  │                  │
     │                 │ 5. Captura lat/lng                  │
     │ 6. Upload evidências (fotos + vídeos)                 │
     │────────────────>│                  │                  │
     │                 │ 7. Validação Frontend               │
     │                 │    - Imagens: 5MB                   │
     │                 │    - Vídeos: 20MB                   │
     │ 8. Marca checkbox "Denúncia Anônima"                  │
     │────────────────>│                  │                  │
     │ 9. Click "Enviar Denúncia"         │                  │
     │────────────────>│                  │                  │
     │                 │ 10. FormData multipart              │
     │                 │ 11. POST /api/denuncias/           │
     │                 │     Header: JWT (opcional)         │
     │                 │─────────────────>│                  │
     │                 │                  │ 12. Valida JWT (se enviado)
     │                 │                  │ 13. Sanitiza inputs
     │                 │                  │ 14. Valida arquivos (MIME)
     │                 │                  │ 15. BEGIN        │
     │                 │                  │─────────────────>│
     │                 │                  │ 16. Gera protocolo
     │                 │                  │     "DEN-20251123-001"
     │                 │                  │ 17. CREATE Denuncia
     │                 │                  │     - denunciante: NULL (se anônima)
     │                 │                  │     - protocolo  │
     │                 │                  │     - status: pendente
     │                 │                  │─────────────────>│
     │                 │                  │ 19. Loop imagens │
     │                 │                  │     CREATE DenunciaImagem
     │                 │                  │─────────────────>│
     │                 │                  │ 20. Loop vídeos  │
     │                 │                  │     CREATE DenunciaVideo
     │                 │                  │─────────────────>│
     │                 │                  │ 21. COMMIT       │
     │                 │                  │─────────────────>│
     │                 │ 22. 201 Created  │                  │
     │                 │     {id, protocolo, status}         │
     │                 │<─────────────────│                  │
     │                 │ 23. Exibe modal com protocolo       │
     │<────────────────│                  │                  │
     │ 24. Toast "Denúncia registrada! Protocolo: DEN-XXX"   │
     │<────────────────│                  │                  │
```

### Geração de Protocolo Único

**Formato**: `DEN-AAAAMMDD-NNN`

**Exemplo**: `DEN-20251123-001`

**Algoritmo**:
```python
def gerar_protocolo():
    hoje = date.today()
    prefixo_data = f"DEN-{hoje.strftime('%Y%m%d')}"
    
    ultimo = Denuncia.objects.filter(
        protocolo__startswith=prefixo_data
    ).order_by('-protocolo').first()
    
    if ultimo:
        numero = int(ultimo.protocolo.split('-')[-1]) + 1
    else:
        numero = 1
    
    return f"{prefixo_data}-{numero:03d}"
```

### Pontos-Chave
- **Denúncia Anônima**: denunciante_id = NULL
- **Protocolo Único**: Para acompanhamento
- **Evidências**: Fotos (5MB) + Vídeos (20MB)
- **Status Inicial**: "pendente"
- **Tipos**: maus-tratos, abandono, agressao, criacao_ilegal, outro

---

## 9. Aprovação de Adoção

### Descrição
Doador avalia e aprova solicitação de adoção, com efeitos em cascata no sistema.

### Diagrama

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Doador  │      │ Frontend │      │ Backend  │      │ Database │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                  │                  │
     │ 1. Recebe notificação "Nova Solicitação"              │
     │<────────────────│                  │                  │
     │ 2. Click na notificação            │                  │
     │────────────────>│                  │                  │
     │                 │ 3. GET /api/solicitacoes-recebidas/│
     │                 │    Header: JWT   │                  │
     │                 │─────────────────>│                  │
     │                 │                  │ 4. SELECT SolicitacaoAdocao
     │                 │                  │    WHERE animal.dono=user_id
     │                 │                  │─────────────────>│
     │                 │ 6. 200 OK {results: []}            │
     │                 │<─────────────────│                  │
     │                 │ 7. Renderiza lista                  │
     │<────────────────│                  │                  │
     │ 8. Click "Ver Detalhes"            │                  │
     │────────────────>│                  │                  │
     │                 │ 9. Abre modal com:                  │
     │                 │    - Dados solicitante              │
     │                 │    - Mensagem, Data                 │
     │<────────────────│                  │                  │
     │ 10. Avalia perfil                  │                  │
     │ 11. Click "Aprovar"                │                  │
     │────────────────>│                  │                  │
     │                 │ 12. Confirma decisão                │
     │<────────────────│                  │                  │
     │ 13. Confirma    │                  │                  │
     │────────────────>│                  │                  │
     │                 │ 14. POST /api/solicitacoes-adocao/{id}/aprovar/
     │                 │─────────────────>│                  │
     │                 │                  │ 15. Valida JWT (é dono?)
     │                 │                  │ 16. BEGIN        │
     │                 │                  │─────────────────>│
     │                 │                  │ 17. UPDATE SolicitacaoAdocao
     │                 │                  │     SET status='aprovada'
     │                 │                  │─────────────────>│
     │                 │                  │ 18. UPDATE AnimalParaAdocao
     │                 │                  │     SET adotado=true
     │                 │                  │         adotado_por=solicitante
     │                 │                  │─────────────────>│
     │                 │                  │ 19. UPDATE Animal
     │                 │                  │     SET is_active=false
     │                 │                  │─────────────────>│
     │                 │                  │ 20. UPDATE outras solicitações
     │                 │                  │     SET status='rejeitada'
     │                 │                  │─────────────────>│
     │                 │                  │ 21. CREATE Notificacao
     │                 │                  │     tipo='aprovacao_adocao'
     │                 │                  │     para solicitante aprovado
     │                 │                  │─────────────────>│
     │                 │                  │ 22. Loop outras solicitações
     │                 │                  │     CREATE Notificacao
     │                 │                  │     tipo='rejeicao_adocao'
     │                 │                  │─────────────────>│
     │                 │                  │ 23. COMMIT       │
     │                 │                  │─────────────────>│
     │                 │ 24. 200 OK {status: 'aprovada'}    │
     │                 │<─────────────────│                  │
     │ 27. Toast "Adoção aprovada!"       │                  │
     │<────────────────│                  │                  │
```

### Efeitos em Cascata

Uma aprovação dispara **6 operações atômicas**:

1. ✅ **SolicitacaoAdocao** → status = "aprovada"
2. ✅ **AnimalParaAdocao** → adotado = true, adotado_por = solicitante, data_adocao = NOW
3. ✅ **Animal** → is_active = false (sai da galeria)
4. ✅ **Outras SolicitacaoAdocao** → status = "rejeitada" (auto-rejeição)
5. ✅ **Notificacao** → Solicitante aprovado (tipo: aprovacao_adocao)
6. ✅ **Notificacoes** → Demais solicitantes (tipo: rejeicao_adocao)

### Regras de Negócio
- ❌ Apenas dono pode aprovar/rejeitar
- ❌ Apenas uma solicitação pode ser aprovada
- ❌ Aprovação é irreversível
- ✅ Animal sai da galeria imediatamente
- ✅ Todas outras solicitações são rejeitadas automaticamente

---

## 10. Glossário

### Autenticação
- **JWT**: JSON Web Token, token compacto para autenticação stateless
- **Access Token**: Token de curta duração (15min) para requisições API
- **Refresh Token**: Token de longa duração (7 dias) para renovar access token
- **PBKDF2**: Algoritmo de hash de senha (260.000 iterações)

### Upload e Validação
- **FormData**: API JavaScript para construir dados multipart/form-data
- **Multipart/form-data**: Codificação HTTP para envio de arquivos binários
- **MIME Type**: Tipo real do arquivo verificado por conteúdo (image/jpeg, video/mp4)
- **Sanitização**: Remoção de HTML/scripts maliciosos dos inputs

### Geolocalização
- **Geolocation API**: API do navegador para obter coordenadas GPS
- **Geocoding Reverso**: Conversão de lat/lng em endereço legível
- **Nominatim**: Serviço gratuito de geocoding do OpenStreetMap
- **Haversine**: Fórmula para calcular distância entre coordenadas GPS

### Mapas
- **Leaflet.js**: Biblioteca JavaScript para mapas interativos
- **OpenStreetMap (OSM)**: Mapeamento colaborativo mundial
- **Tiles**: Imagens 256x256px que compõem o mapa
- **Pin Vermelho**: Marcador de pet perdido
- **Pin Verde**: Marcador de pet encontrado
- **Clusters**: Agrupamento de pins próximos

### Matching
- **Score de Similaridade**: Pontuação 0-100% (espécie + porte + sexo)
- **Threshold**: Score mínimo 50% para notificar match
- **Raio de Busca**: 10km de distância máxima

### Banco de Dados
- **Transação Atômica**: Conjunto de operações que ou todas ocorrem ou nenhuma
- **BEGIN/COMMIT**: Início e confirmação de transação
- **ROLLBACK**: Desfaz transação em caso de erro
- **CASCADE**: Ao deletar pai, deleta filhos relacionados
- **SET_NULL**: Ao deletar pai, seta campo relacionado como NULL

### Sistema
- **Toast**: Notificação temporária na tela
- **Modal**: Janela sobreposta ao conteúdo principal
- **Protocolo**: Código único para rastreamento (DEN-AAAAMMDD-NNN)
- **Auto-rejeição**: Rejeição automática de solicitações ao aprovar uma
- **OneToOne**: Relacionamento 1:1 entre models
- **ForeignKey**: Relacionamento N:1 entre models

---

## 11. Índice de Endpoints API

### Autenticação
- `POST /api/auth/register/` - Registro de usuário
- `POST /api/auth/token/` - Login (obter tokens JWT)
- `POST /api/auth/token/refresh/` - Renovar access token
- `GET /api/auth/me/` - Buscar dados do usuário logado

### Animais para Adoção
- `GET /api/animais-adocao/` - Listar animais disponíveis
- `POST /api/animais-adocao/` - Cadastrar animal
- `GET /api/animais-adocao/{id}/` - Detalhes do animal
- `PATCH /api/animais-adocao/{id}/` - Atualizar animal
- `DELETE /api/animais-adocao/{id}/` - Deletar animal

### Solicitações de Adoção
- `POST /api/solicitacoes-adocao/` - Criar solicitação
- `GET /api/solicitacoes-adocao/minhas-solicitacoes/` - Solicitações enviadas
- `GET /api/solicitacoes-adocao/solicitacoes-recebidas/` - Solicitações recebidas
- `POST /api/solicitacoes-adocao/{id}/aprovar/` - Aprovar solicitação
- `POST /api/solicitacoes-adocao/{id}/rejeitar/` - Rejeitar solicitação

### Pets Perdidos
- `GET /api/pets-perdidos/` - Listar pets perdidos ativos
- `POST /api/pets-perdidos/` - Reportar pet perdido
- `PATCH /api/pets-perdidos/{id}/marcar_encontrado/` - Marcar como encontrado

### Pets Encontrados
- `POST /api/pets-encontrados/` - Reportar pet encontrado (com matching)
- `GET /api/pets-encontrados/` - Listar reportes

### Denúncias
- `POST /api/denuncias/` - Criar denúncia
- `GET /api/denuncias/minhas_denuncias/` - Minhas denúncias
- `GET /api/denuncias/{protocolo}/` - Buscar por protocolo

### Notificações
- `GET /api/notificacoes/` - Listar notificações
- `POST /api/notificacoes/{id}/marcar_lida/` - Marcar como lida
- `POST /api/notificacoes/marcar_todas_lidas/` - Marcar todas como lidas

---

## 12. Resumo de Validações

### Frontend (validations.js)
- ✅ Email: Formato RFC 5322
- ✅ Senha: Mínimo 6 caracteres, não só números
- ✅ Telefone: Formato brasileiro (11) 98765-4321
- ✅ Nome: Mínimo 3 caracteres
- ✅ Arquivos: Formato e tamanho

### Backend (Serializers + Validators)
- ✅ Sanitização: Remove HTML/scripts (utils.py)
- ✅ Unicidade: Email e username únicos
- ✅ MIME Type: Validação real de arquivos
- ✅ Dimensões: Imagens mínimo 200x200px
- ✅ Tamanho: Imagens 5MB, vídeos 20MB
- ✅ Coordenadas: Latitude -90 a 90, longitude -180 a 180

### Regras de Negócio
- ✅ Não pode solicitar próprio animal
- ✅ Uma solicitação ativa por usuário por animal
- ✅ Aprovação de adoção é irreversível
- ✅ Matching apenas para pets ativos
- ✅ Protocolo único por denúncia

---

**Versão**: 1.0  
**Última Atualização**: 23/11/2025  
**Autor**: Daniel
**Projeto**: TCC - S.O.S Pets

---

**Documentos Relacionados**:
- `UML_CASOS_DE_USO.md` - Casos de uso detalhados (21 UCs)
- `UML_CLASSES.md` - Diagrama de classes (19 classes)
- `ARCHITECTURE.md` - Arquitetura do sistema (6 camadas)
- `API_DOCS.md` - Documentação REST completa (10 módulos)
