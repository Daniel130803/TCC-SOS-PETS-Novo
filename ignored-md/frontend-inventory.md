# Inventário do Frontend e Endpoints

## Páginas/funcionalidades com JS puro

- **index.html** – página inicial, pouco ou nenhum JS.
- **login.html** – formulário de login (usa `login.js`).
- **registro.html** – cadastro de usuário (`registro.js`).
- **perfil.html** – edição de perfil (`perfil.js`).
- **adocao.html** – galeria de adoção com filtros, modais e cadastro de pets; contém script inline complexos.
- **animais-perdidos.html** – mapa Leaflet de pets perdidos (`animais-perdidos.js`).
- **arrecadacao.html** – formulário de doação (`arrecadacao.js`).
- **denuncia.html** – formulário de denúncia (`denuncia.js`).
- **contato.html** – formulário de contato (`contato.js`).
- **formulario-adocao.html** – formulário de ONG para adoção (JS inline).
- **historias.html** – conteúdo estático, possivelmente sem JS.
- **minhas-solicitacoes.html** – painel do usuário com várias chamadas AJAX (JS inline).
- **admin-panel.html** – interface administrativa com JS para tabelas e filtros.
- **toast-demo.html** – demo do sistema de toast.

Arquivos de script auxiliares:

- `validations.js` – validações de formulários.
- `user_session.js` – controle de sessão, cabeçalho, notificações.
- `toast-notifications.js` – exibição de mensagens/toasts.

## Endpoints consumidos

### Autenticação
- POST `/api/auth/token/` (login JWT)
- POST `/api/auth/register/` (registro)
- GET `/api/auth/me/` (dados do usuário)
- POST `/api/auth/token/refresh/` (renovar token)

### Adoção
- GET `/api/animais/` (animais da ONG)
- GET `/api/animais-adocao/` (animais de usuários)
- GET `/api/animais-adocao/{id}/` (detalhes de pet)
- POST `/api/animais-adocao/` (cadastrar pet)
- POST `/api/solicitacoes-adocao/` (manifestar interesse)
- GET `/api/minhas-solicitacoes-enviadas/`
- GET `/api/solicitacoes-recebidas/`

### Pets perdidos
- GET `/api/pets-perdidos/` (filtros: estado, cidade, especie, ativo)
- POST `/api/pets-perdidos/` (cadastrar)
- GET `/api/pets-encontrados/` (para listagem)

### Contato
- POST `/api/contatos/`

### Denúncia
- POST `/api/denuncias/`
- Requisições externas para IBGE (municípios e estados).

### Notificações
- GET `/api/notificacoes/?lida=false`
- GET `/api/notificacoes/`
- POST `/api/notificacoes/{id}/marcar_lida/`
- GET `/api/notificacoes/{id}/`

### Perfil
- PATCH `/api/auth/me/`


- Chamadas diversas a dados públicos (e.g., IBGE) e endpoints adicionais usados no painel.

---

