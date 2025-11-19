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
