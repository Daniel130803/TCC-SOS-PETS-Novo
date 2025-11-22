# 🧪 Testes do Frontend - S.O.S Pets

## 📋 Visão Geral

Suíte completa de testes unitários para o frontend JavaScript do sistema S.O.S Pets usando **Jest** e **jsdom**.

## 🎯 Estatísticas

- **Total de Testes:** 21
- **Suites de Teste:** 3
- **Status:** ✅ 100% passando
- **Tempo de Execução:** ~3 segundos

## 📂 Estrutura

```
TCC_SOS_Pets/
├── tests/
│   ├── setup.js              # Configuração global (mocks, helpers)
│   ├── login.test.js         # Testes do módulo de login
│   ├── registro.test.js      # Testes do módulo de registro
│   └── user_session.test.js  # Testes da sessão do usuário
├── package.json              # Configuração do Jest
└── .gitignore                # Ignora node_modules e coverage
```

## 🧩 Módulos Testados

### 1. **Login Module** (6 testes)
- ✅ Validação de campos vazios
- ✅ Login com credenciais válidas
- ✅ Tratamento de credenciais inválidas
- ✅ Armazenamento de tokens JWT
- ✅ Prevenção de submit padrão
- ✅ Atalho Enter para submit

### 2. **Registro Module** (6 testes)
- ✅ Validação de campos obrigatórios
- ✅ Validação de confirmação de senha
- ✅ Registro bem-sucedido
- ✅ Tratamento de email duplicado
- ✅ Exibição de mensagens de erro/sucesso
- ✅ Prevenção de submit padrão

### 3. **User Session Module** (9 testes)
- ✅ Fetch de dados do usuário
- ✅ Tratamento de token expirado (401)
- ✅ Refresh automático de token
- ✅ Renderização de usuário logado
- ✅ Renderização de link admin (para staff)
- ✅ Renderização de usuário não logado
- ✅ Logout com limpeza de tokens
- ✅ Sanitização de XSS
- ✅ Sistema de notificações (contagem, formatação, ícones)

## 🚀 Executando os Testes

### Instalação
```bash
cd TCC_SOS_Pets
npm install
```

### Executar todos os testes
```bash
npm test
```

### Executar em modo watch (desenvolvimento)
```bash
npm run test:watch
```

### Gerar relatório de coverage
```bash
npm run test:coverage
```

## 🔧 Tecnologias

- **Jest 29.7.0** - Framework de testes
- **jsdom** - Simulação de DOM para testes
- **@testing-library/jest-dom** - Matchers customizados

## 📝 Convenções

### Mocks Globais
```javascript
// localStorage mock
localStorage.setItem('key', 'value');
localStorage.getItem('key');

// fetch mock
mockFetchSuccess({ data: 'value' });
mockFetchError(400, 'Error message');

// alert mock
alert('message');
expect(alert).toHaveBeenCalledWith('message');
```

### Estrutura de Testes
```javascript
describe('Nome do Módulo', () => {
  beforeEach(() => {
    // Setup do DOM e variáveis
  });

  test('deve fazer algo específico', async () => {
    // Arrange
    // Act
    // Assert
  });
});
```

## ✨ Destaques para o TCC

1. **Cobertura Completa:** Testa autenticação, validações, navegação e notificações
2. **Segurança:** Valida sanitização contra XSS
3. **UX:** Testa mensagens de erro/sucesso e feedback visual
4. **JWT:** Valida refresh automático de tokens
5. **Mocks Realistas:** Simula API backend e navegador

## 🎓 Valor Acadêmico

Estes testes demonstram:
- Conhecimento de **testes unitários** em JavaScript
- Uso de **mocks e stubs** para isolamento
- **Test-Driven Development (TDD)** principles
- Validação de **experiência do usuário**
- Testes de **segurança** (XSS, injeção)

## 📊 Exemplos de Saída

```bash
PASS  tests/login.test.js
PASS  tests/registro.test.js
PASS  tests/user_session.test.js

Test Suites: 3 passed, 3 total
Tests:       21 passed, 21 total
Snapshots:   0 total
Time:        2.819 s
```

## 🔍 Debugging

Para debugar um teste específico:
```bash
npm test -- --testNamePattern="deve fazer login"
```

Para ver logs detalhados:
```bash
npm test -- --verbose
```

## 📌 Próximos Passos

- [ ] Adicionar testes para `animais-perdidos.js`
- [ ] Adicionar testes para `contato.js`
- [ ] Adicionar testes para `denuncia.js`
- [ ] Implementar testes E2E com Cypress/Playwright
- [ ] Adicionar testes de acessibilidade

---

**Desenvolvido por:** Daniel (TCC S.O.S Pets)  
**Framework:** Jest + jsdom  
**Última Atualização:** 21/11/2025
