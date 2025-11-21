// Sistema de Contato com Administrador
const API_BASE = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.contact-form');
    const assuntoSelect = document.getElementById('assunto');
    const emailInput = document.getElementById('email');
    const mensagemTextarea = document.getElementById('mensagem');
    
    // Preenche dados do usuário logado automaticamente
    preencherDadosUsuario();
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await enviarContato();
    });
});

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

async function enviarContato() {
    const assunto = document.getElementById('assunto').value;
    const email = document.getElementById('email').value;
    const telefone = document.getElementById('telefone').value;
    const mensagem = document.getElementById('mensagem').value;
    
    // Validações
    if (!assunto || !email || !mensagem) {
        mostrarAlerta('Por favor, preencha todos os campos obrigatórios', 'erro');
        return;
    }
    
    if (!validarEmail(email)) {
        mostrarAlerta('Por favor, insira um e-mail válido', 'erro');
        return;
    }
    
    // Monta o assunto completo
    const assuntoCompleto = obterTextoAssunto(assunto);
    
    // Adiciona telefone à mensagem se fornecido
    let mensagemCompleta = mensagem;
    if (telefone) {
        mensagemCompleta += `\n\n📱 Telefone/WhatsApp: ${telefone}`;
    }
    
    // Prepara dados - nome será preenchido pelo backend se usuário estiver logado
    // Caso contrário, usa o email como nome temporário
    const dados = {
        nome: email.split('@')[0], // Usa a parte antes do @ como nome padrão
        assunto: assuntoCompleto,
        email: email,
        mensagem: mensagemCompleta
    };
    
    // Mostra loading
    const submitBtn = document.querySelector('.btn-submit');
    const textoOriginal = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    submitBtn.disabled = true;
    
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
            throw new Error(errorData.detail || 'Erro ao enviar mensagem');
        }
        
        const resultado = await response.json();
        
        // Sucesso
        mostrarAlerta('Mensagem enviada com sucesso! Em breve você receberá uma resposta.', 'sucesso');
        
        // Limpa o formulário
        document.querySelector('.contact-form').reset();
        
        // Se usuário estiver logado, sugere ir para Minhas Solicitações
        if (token) {
            setTimeout(() => {
                if (confirm('Deseja acompanhar suas mensagens em "Minhas Solicitações"?')) {
                    window.location.href = '/minhas-solicitacoes/?tab=contatos';
                }
            }, 2000);
        }
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarAlerta(error.message || 'Erro ao enviar mensagem. Tente novamente.', 'erro');
    } finally {
        submitBtn.innerHTML = textoOriginal;
        submitBtn.disabled = false;
    }
}

function obterTextoAssunto(valor) {
    const assuntos = {
        'parceria': 'Parceria',
        'sugestao': 'Sugestão para a empresa',
        'duvidas': 'Dúvidas Gerais'
    };
    return assuntos[valor] || valor;
}

function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function mostrarAlerta(mensagem, tipo) {
    // Remove alertas anteriores
    const alertaExistente = document.querySelector('.alerta-contato');
    if (alertaExistente) {
        alertaExistente.remove();
    }
    
    // Cria novo alerta
    const alerta = document.createElement('div');
    alerta.className = `alerta-contato alerta-${tipo}`;
    alerta.innerHTML = `
        <div class="alerta-conteudo">
            <i class="fas fa-${tipo === 'sucesso' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${mensagem}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="alerta-fechar">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Adiciona estilos
    const style = document.createElement('style');
    style.textContent = `
        .alerta-contato {
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 99999;
            min-width: 350px;
            max-width: 500px;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .alerta-sucesso {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            border-left: 5px solid #28a745;
            color: #155724;
        }
        
        .alerta-erro {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            border-left: 5px solid #dc3545;
            color: #721c24;
        }
        
        .alerta-conteudo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .alerta-conteudo i:first-child {
            font-size: 1.5rem;
        }
        
        .alerta-conteudo span {
            flex: 1;
            font-weight: 600;
        }
        
        .alerta-fechar {
            background: rgba(0,0,0,0.1);
            border: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .alerta-fechar:hover {
            background: rgba(0,0,0,0.2);
            transform: rotate(90deg);
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(alerta);
    
    // Remove automaticamente após 5 segundos
    setTimeout(() => {
        alerta.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => alerta.remove(), 300);
    }, 5000);
}
