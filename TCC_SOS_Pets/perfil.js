/**
 * perfil.js
 * 
 * Gerencia a página de perfil do usuário
 * - Carrega dados do perfil via API /api/auth/me/
 * - Atualiza informações do perfil com PATCH
 * - Renova token JWT automaticamente quando expira
 * - Usa sistema Toast para feedback visual
 */

document.addEventListener('DOMContentLoaded', async function() {
    const loadingEl = document.getElementById('profile-loading');
    const errorEl = document.getElementById('profile-error');
    const formEl = document.getElementById('profile-form');
    const submitBtn = formEl?.querySelector('button[type="submit"]');

    const access = localStorage.getItem('access');
    const refresh = localStorage.getItem('refresh');

    // Verifica se está autenticado
    if (!access) {
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        return;
    }

    /**
     * Carrega dados do perfil da API
     * Renova token automaticamente se expirado
     */
    async function loadProfile() {
        try {
            const resp = await fetch('/api/auth/me/', {
                headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access') }
            });

            // Renovação automática de token
            if (resp.status === 401 && refresh) {
                const refreshResp = await fetch('/api/auth/token/refresh/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh })
                });
                
                if (refreshResp.ok) {
                    const data = await refreshResp.json();
                    localStorage.setItem('access', data.access);
                    return loadProfile(); // Retry com novo token
                }
                
                throw new Error('Token expirado');
            }

            if (!resp.ok) throw new Error('Erro ao carregar perfil');

            const data = await resp.json();
            
            // Popula formulário com dados do perfil
            document.getElementById('username').value = data.username || '';
            document.getElementById('first_name').value = data.first_name || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('telefone').value = data.telefone || '';

            loadingEl.style.display = 'none';
            formEl.style.display = 'block';
            
            // Adiciona validação em tempo real após carregar dados
            addRealtimeValidation('first_name', validateNomeCompleto);
            addRealtimeValidation('email', validateEmail);
            addRealtimeValidation('telefone', (v) => v ? validateTelefone(v) : {valid: true, message: ''});
            
            // Aplica máscara de telefone
            applyMask('telefone', maskTelefone);

        } catch (err) {
            console.error('Erro ao carregar perfil:', err);
            loadingEl.style.display = 'none';
            errorEl.style.display = 'block';
            toast.error('Erro ao carregar perfil. Faça login novamente.');
        }
    }

    await loadProfile();

    /**
     * Submissão do formulário de edição de perfil
     */
    formEl.addEventListener('submit', async function(e) {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const firstName = document.getElementById('first_name').value.trim();
        const telefone = document.getElementById('telefone').value.trim();

        // Validações robustas
        const validacoes = {
            first_name: validateNomeCompleto(firstName),
            email: validateEmail(email)
        };
        
        // Adiciona validação de telefone se preenchido
        if (telefone) {
            validacoes.telefone = validateTelefone(telefone);
        }
        
        const valido = validateForm(validacoes);
        if (!valido) return;
        
        // Sanitização
        const payload = {
            first_name: sanitizeInput(firstName),
            email: sanitizeInput(email).toLowerCase(),
            telefone: telefone.replace(/\D/g, '')
        };

        // Estado de loading no botão
        setButtonLoading(submitBtn, true);

        try {
            const resp = await fetch('/api/auth/me/', {
                method: 'PATCH',
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                toast.success('✅ Perfil atualizado com sucesso!');
            } else {
                const err = await resp.json();
                const friendlyMessage = getFriendlyErrorMessage(err);
                toast.error(friendlyMessage);
            }
        } catch (err) {
            console.error('Erro ao atualizar perfil:', err);
            toast.error('Erro de conexão. Verifique sua internet e tente novamente.');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
});
