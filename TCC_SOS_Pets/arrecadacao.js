/**
 * arrecadacao.js
 * 
 * Sistema de Doações - Validação de Formulário
 * - Validação de CPF/CNPJ
 * - Validação de campos obrigatórios
 * - Feedback visual com Toast
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.donation-form');
    const cpfCnpjInput = document.getElementById('cpf_cnpj');
    
    // Adiciona validações em tempo real
    addRealtimeValidation('nome', validateNomeCompleto);
    addRealtimeValidation('e-mail', validateEmail);
    addRealtimeValidation('cidade', (v) => validateTexto(v, 'Cidade', 3, 100));
    
    // Máscara de CPF (adapta para CNPJ se necessário)
    if (cpfCnpjInput) {
        cpfCnpjInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                // Máscara CPF: 000.000.000-00
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            } else {
                // Máscara CNPJ: 00.000.000/0000-00
                value = value.substring(0, 14);
                value = value.replace(/^(\d{2})(\d)/, '$1.$2');
                value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
                value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
                value = value.replace(/(\d{4})(\d)/, '$1-$2');
            }
            
            e.target.value = value;
        });
        
        // Validação ao sair do campo
        cpfCnpjInput.addEventListener('blur', function() {
            const value = this.value.replace(/\D/g, '');
            
            if (value.length === 11) {
                const validacao = validateCPF(value);
                if (!validacao.valid) {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                    toast.error(validacao.message);
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            } else if (value.length === 14) {
                // CNPJ - apenas valida comprimento por enquanto
                if (value.length === 14) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                    toast.error('CNPJ deve ter 14 dígitos');
                }
            } else if (value.length > 0) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                toast.error('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos');
            }
        });
    }
    
    // Alterna exibição de detalhes de pagamento
    const paymentRadios = document.querySelectorAll('input[name="payment"]');
    const pixDetails = document.getElementById('pix-details');
    const cartaoDetails = document.getElementById('cartao-details');
    
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (pixDetails) pixDetails.style.display = this.value === 'pix' ? 'block' : 'none';
            if (cartaoDetails) cartaoDetails.style.display = this.value === 'cartao' ? 'block' : 'none';
        });
    });
    
    // Validação no submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nome = document.getElementById('nome').value.trim();
        const cpfCnpj = document.getElementById('cpf_cnpj').value.replace(/\D/g, '');
        const email = document.getElementById('e-mail').value.trim();
        const cidade = document.getElementById('cidade').value.trim();
        const estado = document.getElementById('estado').value;
        const payment = document.querySelector('input[name="payment"]:checked')?.value;
        
        const validacoes = {
            nome: validateNomeCompleto(nome),
            email: validateEmail(email),
            cidade: validateTexto(cidade, 'Cidade', 3, 100),
            estado: estado ? { valid: true, message: '' } : { valid: false, message: 'Selecione o estado' },
            payment: payment ? { valid: true, message: '' } : { valid: false, message: 'Selecione a forma de pagamento' }
        };
        
        // Valida CPF ou CNPJ
        if (cpfCnpj.length === 11) {
            validacoes.cpf_cnpj = validateCPF(cpfCnpj);
        } else if (cpfCnpj.length === 14) {
            validacoes.cpf_cnpj = { valid: true, message: '' }; // CNPJ básico
        } else {
            validacoes.cpf_cnpj = { valid: false, message: 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos' };
        }
        
        const valido = validateForm(validacoes);
        
        if (valido) {
            // Sanitiza dados
            const dadosSanitizados = {
                nome: sanitizeInput(nome),
                cpf_cnpj: cpfCnpj,
                email: sanitizeInput(email).toLowerCase(),
                cidade: sanitizeInput(cidade),
                estado: estado,
                payment: payment
            };
            
            console.log('📦 Dados de doação validados:', dadosSanitizados);
            
            // Aqui você pode enviar para a API quando implementado
            toast.success('✅ Dados validados com sucesso! Sistema de pagamento será implementado em breve.');
            
            // Por enquanto, apenas reseta o formulário
            setTimeout(() => {
                form.reset();
                if (pixDetails) pixDetails.style.display = 'none';
                if (cartaoDetails) cartaoDetails.style.display = 'none';
            }, 2000);
        }
    });
});
