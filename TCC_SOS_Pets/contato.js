/**
 * contato.js
 * 
 * Sistema de Contato com Administrador
 * - Preenche email automaticamente para usuários logados
 * - Validação de formulário com Toast
 * - Loading em botão de envio
 * - Feedback visual com sistema Toast
 */

const API_BASE = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.contact-form');
    
    // Preenche dados do usuário logado automaticamente
    preencherDadosUsuario();
    
    // Validação em tempo real
    addRealtimeValidation('email', validateEmail);
    addRealtimeValidation('telefone', (v) => v ? validateTelefone(v) : {valid: true, message: ''});
    addRealtimeValidation('mensagem', (v) => validateTexto(v, 'Mensagem', 10, 5000));
    
    // Máscaras
    applyMask('telefone', maskTelefone);
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await enviarContato();
    });
});

/**
 * Preenche email automaticamente se usuário estiver logado
 */
async function preencherDadosUsuario() {
    const token = localStorage.getItem('access');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE}/auth/me/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const userData = await response.json();
            const emailInput = document.getElementById('email');
            
            // Preenche o email se o usuário estiver logado
            if (userData.email) {
                emailInput.value = userData.email;
                emailInput.setAttribute('readonly', true);
                emailInput.style.background = '#f0f0f0';
            }
        }
    } catch (error) {
        console.log('Usuário não autenticado ou erro ao buscar dados');
    }
}

/**
 * Envia mensagem de contato para o backend
 */
async function enviarContato() {
    const assunto = document.getElementById('assunto').value;
    const email = document.getElementById('email').value.trim();
    const telefone = document.getElementById('telefone').value.trim();
    const mensagem = document.getElementById('mensagem').value.trim();
    const submitBtn = document.querySelector('.btn-submit');
    
    // Validações robustas
    const validacoes = {
        assunto: assunto ? { valid: true, message: '' } : { valid: false, message: 'Selecione um assunto' },
        email: validateEmail(email),
        mensagem: validateTexto(mensagem, 'Mensagem', 10, 5000)
    };
    
    // Adiciona validação de telefone se preenchido
    if (telefone) {
        validacoes.telefone = validateTelefone(telefone);
    }
    
    const valido = validateForm(validacoes);
    if (!valido) return;
    
    // Sanitização
    const emailLimpo = sanitizeInput(email).toLowerCase();
    const mensagemLimpa = sanitizeInput(mensagem);
    
    // Monta o assunto completo
    const assuntoCompleto = obterTextoAssunto(assunto);
    
    // Adiciona telefone à mensagem se fornecido
    let mensagemCompleta = mensagemLimpa;
    if (telefone) {
        const telefoneLimpo = telefone.replace(/\D/g, '');
        mensagemCompleta += `\n\n📱 Telefone/WhatsApp: ${telefone}`;
    }
    
    // Prepara dados
    const dados = {
        nome: emailLimpo.split('@')[0], // Usa a parte antes do @ como nome padrão
        assunto: assuntoCompleto,
        email: emailLimpo,
        mensagem: mensagemCompleta
    };
    
    // Estado de loading
    setButtonLoading(submitBtn, true);
    
    try {
        const token = localStorage.getItem('access');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Adiciona token se usuário estiver logado
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE}/contatos/`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(dados)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Erro do servidor:', errorData);
            const friendlyMessage = getFriendlyErrorMessage(errorData);
            toast.error(friendlyMessage);
            return;
        }
        
        // Sucesso
        toast.success('✅ Mensagem enviada com sucesso! Em breve você receberá uma resposta.');
        
        // Limpa o formulário
        document.querySelector('.contact-form').reset();
        
        // Se usuário estiver logado, sugere ir para Minhas Solicitações
        if (token) {
            setTimeout(() => {
                toast.info('Você pode acompanhar suas mensagens em "Minhas Solicitações"', 5000);
            }, 2000);
        }
        
    } catch (error) {
        console.error('Erro:', error);
        toast.error('Erro de conexão. Verifique sua internet e tente novamente.');
    } finally {
        setButtonLoading(submitBtn, false);
    }
}

/**
 * Retorna texto legível do assunto selecionado
 */
function obterTextoAssunto(valor) {
    const assuntos = {
        'parceria': 'Parceria',
        'sugestao': 'Sugestão para a empresa',
        'duvidas': 'Dúvidas Gerais'
    };
    return assuntos[valor] || valor;
}
