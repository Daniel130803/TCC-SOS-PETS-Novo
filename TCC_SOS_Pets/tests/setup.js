/**
 * Configuração global para testes Jest do S.O.S Pets.
 * 
 * Este arquivo configura:
 * - Mocks globais para localStorage
 * - Mocks para fetch API
 * - Helpers de teste comuns
 */

// Mock do localStorage
global.localStorage = {
  store: {},
  getItem(key) {
    return this.store[key] || null;
  },
  setItem(key, value) {
    this.store[key] = String(value);
  },
  removeItem(key) {
    delete this.store[key];
  },
  clear() {
    this.store = {};
  }
};

// Mock do fetch global
global.fetch = jest.fn();

// Helper para resetar mocks entre testes
beforeEach(() => {
  localStorage.clear();
  fetch.mockClear();
});

// Helper para criar resposta fetch de sucesso
global.mockFetchSuccess = (data) => {
  fetch.mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: async () => data
  });
};

// Helper para criar resposta fetch de erro
global.mockFetchError = (status = 400, message = 'Error') => {
  fetch.mockResolvedValueOnce({
    ok: false,
    status,
    json: async () => ({ detail: message })
  });
};

// Mock do alert
global.alert = jest.fn();

// Mock do window.location
delete window.location;
window.location = { href: '', assign: jest.fn(), reload: jest.fn() };
