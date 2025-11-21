// Controla exibição do usuário logado no header
// Requer endpoints: /api/auth/me/ , /api/auth/token/refresh/

async function fetchMe(access) {
  const resp = await fetch('/api/auth/me/', {
    headers: { 'Authorization': 'Bearer ' + access }
  });
  if (resp.status === 401) throw new Error('unauthorized');
  if (!resp.ok) throw new Error('fail');
  return resp.json();
}

async function refreshToken(refresh) {
  const resp = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });
  if (!resp.ok) throw new Error('refresh-failed');
  const data = await resp.json();
  if (data.access) localStorage.setItem('access', data.access);
  return data.access;
}

function renderLogged(username, isStaff = false) {
  const container = document.querySelector('.nav-user-area');
  if (!container) return;
  container.innerHTML = '';
  
  // Botão de notificações
  const btnNotif = document.createElement('button');
  btnNotif.type = 'button';
  btnNotif.className = 'btn-notificacoes';
  btnNotif.innerHTML = `
    <i class="fas fa-bell"></i>
    <span class="notif-label">Notificações</span>
    <span class="badge-notificacoes" style="display:none;">0</span>
  `;
  btnNotif.addEventListener('click', () => abrirModalNotificacoes());
  container.appendChild(btnNotif);
  
  // Atualiza contador de notificações
  carregarContagemNotificacoes();
  
  const dropdown = document.createElement('div');
  dropdown.className = 'nav-user-dropdown';

  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'nav-user-toggle';
    toggle.setAttribute('aria-haspopup', 'true');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Menu do usuário');
    toggle.innerHTML = `<i class="fas fa-user" aria-hidden="true"></i><span class="greet">Olá, <strong>${sanitize(username)}</strong></span><span class="caret" aria-hidden="true">▾</span>`;

  const menu = document.createElement('div');
  menu.className = 'nav-user-menu';
  menu.innerHTML = `
    <a href="/perfil/"><i class="fas fa-id-card"></i> Perfil</a>
    <a href="/minhas-solicitacoes/"><i class="fas fa-clipboard-list"></i> Minhas Solicitações</a>
    ${isStaff ? '<a href="/admin-panel/"><i class="fas fa-shield-alt"></i> Painel Admin</a>' : ''}
    <hr>
    <button type="button" class="logout-item"><i class="fas fa-sign-out-alt"></i> Sair</button>
  `;

  dropdown.appendChild(toggle);
  dropdown.appendChild(menu);
  container.appendChild(dropdown);

  function closeAll() {
    menu.classList.remove('open');
    toggle.classList.remove('open');
  }
  function toggleMenu() {
    const isOpen = menu.classList.contains('open');
    closeAll();
      if (!isOpen) {
        menu.classList.add('open');
        toggle.classList.add('open');
        toggle.setAttribute('aria-expanded', 'true');
    }
  }

  toggle.addEventListener('click', (e) => { e.stopPropagation(); toggleMenu(); });
  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) closeAll();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll(); });

  menu.querySelector('.logout-item').addEventListener('click', () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login/';
  });

    // garante fechado inicialmente
    closeAll();
}

function renderLoggedOut() {
  const container = document.querySelector('.nav-user-area');
  if (!container) return;
  container.innerHTML = '';
  const link = document.createElement('a');
  link.href = '/login/';
  link.innerHTML = '<i class="fas fa-user"></i><span>Login</span>';
  container.appendChild(link);
}

async function initSession() {
  const access = localStorage.getItem('access');
  const refresh = localStorage.getItem('refresh');
  if (!access) { renderLoggedOut(); return; }
  try {
    const me = await fetchMe(access);
    renderLogged(me.username || 'Usuário', me.is_staff || false);
  } catch (e) {
    if (e.message === 'unauthorized' && refresh) {
      try {
        const newAccess = await refreshToken(refresh);
        if (newAccess) {
          const me = await fetchMe(newAccess);
          renderLogged(me.username || 'Usuário', me.is_staff || false);
          return;
        }
      } catch (_) { /* falha no refresh */ }
    }
    renderLoggedOut();
  }
}

document.addEventListener('DOMContentLoaded', initSession);

// Sanitização simples para evitar injeção quando inserimos innerHTML
function sanitize(str) {
  return String(str).replace(/[&<>"]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
}

// ===== SISTEMA DE NOTIFICAÇÕES =====

// Torna funções globais para serem acessadas pelos event listeners
window.abrirModalNotificacoes = abrirModalNotificacoes;
window.fecharModalNotificacoes = fecharModalNotificacoes;
window.marcarComoLida = marcarComoLida;
window.renderizarNotificacoes = renderizarNotificacoes;

async function carregarContagemNotificacoes() {
  const token = localStorage.getItem('access');
  if (!token) return;
  
  try {
    const response = await fetch('http://localhost:8000/api/notificacoes/?lida=false', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) return;
    
    const data = await response.json();
    const notificacoes = data.results || data;
    const count = notificacoes.length;
    
    const badge = document.querySelector('.badge-notificacoes');
    const btnNotif = document.querySelector('.btn-notificacoes');
    
    if (badge && btnNotif) {
      if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'flex';
        btnNotif.classList.add('has-notifications'); // Ícone verde
      } else {
        badge.style.display = 'none';
        btnNotif.classList.remove('has-notifications'); // Ícone cinza
      }
    }
  } catch (error) {
    console.error('Erro ao carregar notificações:', error);
  }
}

async function carregarNotificacoes() {
  const token = localStorage.getItem('access');
  if (!token) return [];
  
  try {
    const response = await fetch('http://localhost:8000/api/notificacoes/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) throw new Error('Erro ao carregar notificações');
    
    const data = await response.json();
    return data.results || data;
  } catch (error) {
    console.error('Erro:', error);
    return [];
  }
}

async function marcarComoLida(id) {
  const token = localStorage.getItem('access');
  if (!token) return;
  
  try {
    const response = await fetch(`http://localhost:8000/api/notificacoes/${id}/marcar_lida/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      carregarContagemNotificacoes();
    }
  } catch (error) {
    console.error('Erro ao marcar como lida:', error);
  }
}

function abrirModalNotificacoes() {
  // Cria dropdown se não existir
  let dropdown = document.getElementById('dropdown-notificacoes');
  
  if (!dropdown) {
    dropdown = document.createElement('div');
    dropdown.id = 'dropdown-notificacoes';
    dropdown.className = 'notificacoes-dropdown';
    dropdown.innerHTML = `
      <div class="notif-dropdown-header">
        <h3>Notificações</h3>
      </div>
      <div class="notif-dropdown-body" id="lista-notificacoes">
        <div style="text-align: center; padding: 2rem;">
          <i class="fas fa-spinner fa-spin" style="font-size: 2rem;"></i>
          <p>Carregando...</p>
        </div>
      </div>
    `;
    document.body.appendChild(dropdown);
    
    // Fecha ao clicar fora
    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && !e.target.closest('.btn-notificacoes')) {
        fecharModalNotificacoes();
      }
    });
  }
  
  // Toggle dropdown
  if (dropdown.classList.contains('open')) {
    fecharModalNotificacoes();
  } else {
    // Posiciona dropdown abaixo do botão
    const btnNotif = document.querySelector('.btn-notificacoes');
    const rect = btnNotif.getBoundingClientRect();
    dropdown.style.top = `${rect.bottom + 10}px`;
    dropdown.style.right = `${window.innerWidth - rect.right}px`;
    
    dropdown.classList.add('open');
    renderizarNotificacoes();
  }
}

function fecharModalNotificacoes() {
  const dropdown = document.getElementById('dropdown-notificacoes');
  if (dropdown) dropdown.classList.remove('open');
}

async function renderizarNotificacoes() {
  const container = document.getElementById('lista-notificacoes');
  if (!container) return;
  
  const notificacoes = await carregarNotificacoes();
  
  if (notificacoes.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: #999;">
        <i class="fas fa-bell-slash" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
        <p style="font-size: 1.1rem;">Nenhuma notificação</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = notificacoes.map(n => {
    const dataFormatada = formatarDataRelativa(n.data_criacao);
    const lidaClass = n.lida ? 'lida' : 'nao-lida';
    const temContatos = n.tipo === 'adocao_aprovada' && (n.contato_telefone || n.contato_email);
    
    return `
      <div class="notif-item-dropdown ${lidaClass}" data-id="${n.id}" onclick="abrirDetalheNotificacao(${n.id})">
        <div class="notif-icon-wrapper">
          <i class="fas fa-${getTipoIcone(n.tipo)}"></i>
        </div>
        <div class="notif-content-wrapper">
          <div class="notif-titulo-dropdown">${n.titulo}</div>
          <div class="notif-mensagem-dropdown">${n.mensagem}</div>
          ${temContatos ? '<div class="notif-tag-contato"><i class="fas fa-address-card"></i> Dados de contato disponíveis</div>' : ''}
          <div class="notif-data-dropdown">${dataFormatada}</div>
        </div>
        ${!n.lida ? '<div class="notif-indicator"></div>' : ''}
      </div>
    `;
  }).join('');
}

// Nova função para abrir modal com detalhes da notificação
async function abrirDetalheNotificacao(notifId) {
  const token = localStorage.getItem('access');
  if (!token) return;
  
  try {
    // Busca dados da notificação
    const response = await fetch(`http://localhost:8000/api/notificacoes/${notifId}/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) return;
    
    const n = await response.json();
    
    // Marca como lida se não estiver
    if (!n.lida) {
      await marcarComoLida(notifId);
    }
    
    // Fecha dropdown
    fecharModalNotificacoes();
    
    // Cria modal de detalhes
    let modalDetalhes = document.getElementById('modal-detalhes-notificacao');
    
    if (!modalDetalhes) {
      modalDetalhes = document.createElement('div');
      modalDetalhes.id = 'modal-detalhes-notificacao';
      modalDetalhes.className = 'modal-overlay';
      document.body.appendChild(modalDetalhes);
      
      // Fecha ao clicar fora
      modalDetalhes.addEventListener('click', (e) => {
        if (e.target === modalDetalhes) {
          modalDetalhes.classList.remove('visible');
          setTimeout(() => modalDetalhes.remove(), 300);
        }
      });
    }
    
    // Monta conteúdo do modal
    let conteudoExtra = '';
    if (n.tipo === 'adocao_aprovada' && (n.contato_telefone || n.contato_email)) {
      conteudoExtra = `
        <div class="notif-contatos-modal">
          <h3><i class="fas fa-address-card"></i> Dados de Contato</h3>
          <div class="contatos-grid">
            ${n.contato_telefone && n.contato_telefone !== 'Não informado' ? `
              <a href="https://wa.me/55${n.contato_telefone.replace(/\D/g, '')}" target="_blank" class="btn-contato btn-whatsapp">
                <i class="fab fa-whatsapp"></i> WhatsApp: ${n.contato_telefone}
              </a>
            ` : ''}
            ${n.contato_email && n.contato_email !== 'Não informado' ? `
              <a href="mailto:${n.contato_email}" class="btn-contato btn-email">
                <i class="fas fa-envelope"></i> Email: ${n.contato_email}
              </a>
            ` : ''}
            ${n.contato_endereco && n.contato_endereco !== 'Não informado' ? `
              <div class="endereco-box">
                <i class="fas fa-map-marker-alt"></i>
                <span><strong>Endereço:</strong> ${n.contato_endereco}</span>
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }
    
    modalDetalhes.innerHTML = `
      <div class="modal-content modal-notificacao-detalhe">
        <div class="modal-header-detalhe">
          <div class="header-info-detalhe">
            <i class="fas fa-${getTipoIcone(n.tipo)}"></i>
            <h2>${n.titulo}</h2>
          </div>
          <button class="modal-close" onclick="fecharModalDetalheNotificacao()">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body-detalhe">
          <p class="notif-mensagem-completa">${n.mensagem}</p>
          ${conteudoExtra}
          <div class="notif-data-completa">
            <i class="fas fa-clock"></i>
            ${new Date(n.data_criacao).toLocaleString('pt-BR')}
          </div>
          ${n.link ? `
            <a href="${n.link}" class="btn-ver-mais">
              <i class="fas fa-external-link-alt"></i> Ver mais detalhes
            </a>
          ` : ''}
        </div>
      </div>
    `;
    
    // Mostra modal com animação
    setTimeout(() => {
      modalDetalhes.classList.add('visible');
    }, 10);
    
    // Atualiza contador e lista
    await carregarContagemNotificacoes();
    
  } catch (error) {
    console.error('Erro ao abrir detalhes:', error);
  }
}

function fecharModalDetalheNotificacao() {
  const modalDetalhes = document.getElementById('modal-detalhes-notificacao');
  if (modalDetalhes) {
    modalDetalhes.classList.remove('visible');
    setTimeout(() => modalDetalhes.remove(), 300);
  }
}

function getTipoIcone(tipo) {
  const icones = {
    'adocao_aprovada': 'check-circle',
    'adocao_rejeitada': 'times-circle',
    'pet_aprovado': 'paw',
    'pet_rejeitado': 'ban',
    'nova_mensagem': 'envelope',
    'default': 'bell'
  };
  return icones[tipo] || icones['default'];
}

function formatarDataRelativa(data) {
  const agora = new Date();
  const dataNotif = new Date(data);
  const diff = Math.floor((agora - dataNotif) / 1000);
  
  if (diff < 60) return 'Agora';
  if (diff < 3600) return `${Math.floor(diff / 60)}m atrás`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h atrás`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d atrás`;
  return dataNotif.toLocaleDateString('pt-BR');
}

function getTipoIcon(tipo) {
  const icons = {
    'adocao_aprovada': 'fas fa-check-circle',
    'adocao_rejeitada': 'fas fa-times-circle',
    'animal_aprovado': 'fas fa-paw',
    'animal_rejeitado': 'fas fa-ban',
    'interesse_adocao': 'fas fa-heart',
    'denuncia': 'fas fa-exclamation-triangle'
  };
  return icons[tipo] || 'fas fa-bell';
}

// Atualiza notificações a cada 30 segundos
setInterval(() => {
  if (localStorage.getItem('access')) {
    carregarContagemNotificacoes();
  }
}, 30000);
