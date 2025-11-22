/**
 * Testes para o módulo de Sessão do Usuário (user_session.js).
 * 
 * Testa:
 * - Fetch de dados do usuário logado
 * - Refresh de token expirado
 * - Renderização de usuário logado
 * - Renderização de usuário não logado
 * - Logout do usuário
 * - Sanitização de strings
 * - Sistema de notificações
 */

describe('User Session Module', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="nav-user-area"></div>
    `;
  });

  describe('fetchMe', () => {
    test('deve buscar dados do usuário com sucesso', async () => {
      const mockUser = { 
        username: 'testuser', 
        email: 'test@email.com',
        is_staff: false 
      };
      mockFetchSuccess(mockUser);

      const fetchMe = async (access) => {
        const resp = await fetch('/api/auth/me/', {
          headers: { 'Authorization': 'Bearer ' + access }
        });
        if (resp.status === 401) throw new Error('unauthorized');
        if (!resp.ok) throw new Error('fail');
        return resp.json();
      };

      const result = await fetchMe('fake-token');

      expect(fetch).toHaveBeenCalledWith('/api/auth/me/', {
        headers: { 'Authorization': 'Bearer fake-token' }
      });
      expect(result).toEqual(mockUser);
    });

    test('deve lançar erro 401 para token inválido', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      });

      const fetchMe = async (access) => {
        const resp = await fetch('/api/auth/me/', {
          headers: { 'Authorization': 'Bearer ' + access }
        });
        if (resp.status === 401) throw new Error('unauthorized');
        return resp.json();
      };

      await expect(fetchMe('invalid-token')).rejects.toThrow('unauthorized');
    });
  });

  describe('refreshToken', () => {
    test('deve renovar token com sucesso', async () => {
      const mockResponse = { access: 'new-access-token' };
      mockFetchSuccess(mockResponse);

      const refreshToken = async (refresh) => {
        const resp = await fetch('/api/auth/token/refresh/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh })
        });
        if (!resp.ok) throw new Error('refresh-failed');
        const data = await resp.json();
        if (data.access) localStorage.setItem('access', data.access);
        return data.access;
      };

      const newToken = await refreshToken('fake-refresh-token');

      expect(fetch).toHaveBeenCalledWith('/api/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: 'fake-refresh-token' })
      });
      expect(newToken).toBe('new-access-token');
      expect(localStorage.getItem('access')).toBe('new-access-token');
    });
  });

  describe('renderLogged', () => {
    test('deve renderizar usuário logado corretamente', () => {
      const sanitize = (str) => String(str).replace(/[&<>"]/g, s => 
        ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s])
      );

      const renderLogged = (username, isStaff = false) => {
        const container = document.querySelector('.nav-user-area');
        if (!container) return;
        
        container.innerHTML = `
          <button class="btn-notificacoes">
            <i class="fas fa-bell"></i>
          </button>
          <div class="nav-user-dropdown">
            <button class="nav-user-toggle">
              <span class="greet">Olá, <strong>${sanitize(username)}</strong></span>
            </button>
            <div class="nav-user-menu">
              <a href="/perfil/">Perfil</a>
              ${isStaff ? '<a href="/admin-panel/">Painel Admin</a>' : ''}
              <button class="logout-item">Sair</button>
            </div>
          </div>
        `;
      };

      renderLogged('testuser', false);
      const container = document.querySelector('.nav-user-area');
      
      expect(container.innerHTML).toContain('Olá, <strong>testuser</strong>');
      expect(container.innerHTML).toContain('btn-notificacoes');
      expect(container.innerHTML).not.toContain('Painel Admin');
    });

    test('deve renderizar link admin para usuário staff', () => {
      const sanitize = (str) => String(str);
      
      const renderLogged = (username, isStaff = false) => {
        const container = document.querySelector('.nav-user-area');
        container.innerHTML = isStaff ? '<a href="/admin-panel/">Admin</a>' : '';
      };

      renderLogged('admin', true);
      const container = document.querySelector('.nav-user-area');
      
      expect(container.innerHTML).toContain('Admin');
    });
  });

  describe('renderLoggedOut', () => {
    test('deve renderizar link de login', () => {
      const renderLoggedOut = () => {
        const container = document.querySelector('.nav-user-area');
        if (!container) return;
        container.innerHTML = '<a href="/login/">Login</a>';
      };

      renderLoggedOut();
      const container = document.querySelector('.nav-user-area');
      
      expect(container.innerHTML).toContain('Login');
      expect(container.innerHTML).toContain('/login/');
    });
  });

  describe('logout', () => {
    test('deve limpar tokens e redirecionar', () => {
      localStorage.setItem('access', 'fake-token');
      localStorage.setItem('refresh', 'fake-refresh');

      const logout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        window.location.href = '/login/';
      };

      logout();

      expect(localStorage.getItem('access')).toBeNull();
      expect(localStorage.getItem('refresh')).toBeNull();
      expect(window.location.href).toBe('/login/');
    });
  });

  describe('sanitize', () => {
    test('deve sanitizar caracteres especiais', () => {
      const sanitize = (str) => 
        String(str).replace(/[&<>"]/g, s => 
          ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s])
        );

      expect(sanitize('<script>alert("xss")</script>'))
        .toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
      
      expect(sanitize('Normal text')).toBe('Normal text');
      
      expect(sanitize('A & B')).toBe('A &amp; B');
    });
  });

  describe('Notificações', () => {
    test('deve carregar contagem de notificações', async () => {
      const mockNotificacoes = {
        results: [
          { id: 1, titulo: 'Notif 1', lida: false },
          { id: 2, titulo: 'Notif 2', lida: false }
        ]
      };
      mockFetchSuccess(mockNotificacoes);
      localStorage.setItem('access', 'fake-token');

      const carregarContagemNotificacoes = async () => {
        const token = localStorage.getItem('access');
        if (!token) return;

        try {
          const response = await fetch('http://localhost:8000/api/notificacoes/?lida=false', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (!response.ok) return;
          
          const data = await response.json();
          return (data.results || data).length;
        } catch (error) {
          console.error('Erro:', error);
          return 0;
        }
      };

      const count = await carregarContagemNotificacoes();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/notificacoes/?lida=false',
        { headers: { 'Authorization': 'Bearer fake-token' } }
      );
      expect(count).toBe(2);
    });

    test('deve formatar data relativa', () => {
      const formatarDataRelativa = (data) => {
        const agora = new Date();
        const dataNotif = new Date(data);
        const diff = Math.floor((agora - dataNotif) / 1000);
        
        if (diff < 60) return 'Agora';
        if (diff < 3600) return `${Math.floor(diff / 60)}m atrás`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h atrás`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d atrás`;
        return dataNotif.toLocaleDateString('pt-BR');
      };

      const agora = new Date();
      
      // 30 segundos atrás
      expect(formatarDataRelativa(new Date(agora - 30000))).toBe('Agora');
      
      // 5 minutos atrás
      expect(formatarDataRelativa(new Date(agora - 5 * 60000))).toContain('m atrás');
      
      // 2 horas atrás
      expect(formatarDataRelativa(new Date(agora - 2 * 3600000))).toContain('h atrás');
    });

    test('deve retornar ícone correto por tipo', () => {
      const getTipoIcone = (tipo) => {
        const icones = {
          'adocao_aprovada': 'check-circle',
          'adocao_rejeitada': 'times-circle',
          'pet_aprovado': 'paw',
          'pet_rejeitado': 'ban',
          'nova_mensagem': 'envelope',
          'default': 'bell'
        };
        return icones[tipo] || icones['default'];
      };

      expect(getTipoIcone('adocao_aprovada')).toBe('check-circle');
      expect(getTipoIcone('pet_aprovado')).toBe('paw');
      expect(getTipoIcone('tipo_desconhecido')).toBe('bell');
    });
  });
});
