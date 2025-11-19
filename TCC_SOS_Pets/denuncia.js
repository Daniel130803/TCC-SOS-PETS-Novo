const API_BASE = 'http://localhost:8000/api';
let municipiosCache = {};
let currentEstado = '';

// Carregar municípios do IBGE quando o estado for selecionado
const estadoSelect = document.getElementById('estado');
const municipioInput = document.getElementById('municipio');

estadoSelect.addEventListener('change', async function() {
    const estado = this.value;
    currentEstado = estado;
    municipioInput.value = '';
    
    if (!estado) {
        municipioInput.disabled = true;
        municipioInput.placeholder = 'Selecione um estado primeiro';
        return;
    }

    municipioInput.disabled = false;
    municipioInput.placeholder = 'Carregando municípios...';

    // Se já temos cache, não buscar novamente
    if (municipiosCache[estado]) {
        municipioInput.placeholder = 'Digite o nome do município';
        return;
    }

    try {
        const response = await fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estado}/municipios`);
        const data = await response.json();
        municipiosCache[estado] = data.map(m => m.nome).sort();
        municipioInput.placeholder = 'Digite o nome do município';
    } catch (error) {
        console.error('Erro ao carregar municípios:', error);
        municipioInput.placeholder = 'Erro ao carregar. Digite manualmente.';
    }
});

// Autocompletar município (busca fuzzy)
municipioInput.addEventListener('input', function() {
    const input = this.value.toLowerCase();
    const datalistId = 'municipios-list';
    
    // Remove datalist anterior se existir
    let datalist = document.getElementById(datalistId);
    if (datalist) {
        datalist.remove();
    }

    if (!input || !currentEstado || !municipiosCache[currentEstado]) {
        municipioInput.removeAttribute('list');
        return;
    }

    // Cria novo datalist
    datalist = document.createElement('datalist');
    datalist.id = datalistId;

    // Normaliza string para comparação (remove acentos)
    const normalize = (str) => str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const normalizedInput = normalize(input);

    // Filtra municípios
    const matches = municipiosCache[currentEstado]
        .filter(m => normalize(m).includes(normalizedInput))
        .slice(0, 10); // Limita a 10 resultados

    matches.forEach(municipio => {
        const option = document.createElement('option');
        option.value = municipio;
        datalist.appendChild(option);
    });

    document.body.appendChild(datalist);
    municipioInput.setAttribute('list', datalistId);
});

// Enviar formulário via AJAX
const form = document.querySelector('.report-form');
form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const token = localStorage.getItem('access');
    if (!token) {
        alert('Você precisa estar logado para fazer uma denúncia.');
        window.location.href = '/login/';
        return;
    }

    const formData = new FormData();
    formData.append('titulo', document.getElementById('envolvido').value || 'Denúncia anônima');
    formData.append('descricao', document.getElementById('descricao').value);
    formData.append('localizacao', `${document.getElementById('local').value}, ${document.getElementById('municipio').value}/${document.getElementById('estado').value}`);
    
    const anexo = document.getElementById('anexo').files[0];
    if (anexo) {
        formData.append('imagem', anexo);
    }

    const button = form.querySelector('button[type="submit"]');
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';

    try {
        const response = await fetch(`${API_BASE}/denuncias/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(JSON.stringify(error));
        }

        alert('Denúncia enviada com sucesso! Ela será analisada por nossa equipe.');
        form.reset();
        municipioInput.disabled = true;
        municipioInput.placeholder = 'Selecione um estado primeiro';

    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao enviar denúncia. Por favor, tente novamente.');
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
});

// Preview de arquivos
const anexoInput = document.getElementById('anexo');
const fileList = document.getElementById('file-list');

anexoInput.addEventListener('change', function() {
    fileList.innerHTML = '';
    if (this.files.length > 0) {
        Array.from(this.files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <small>(${(file.size / 1024).toFixed(1)} KB)</small>
            `;
            fileList.appendChild(fileItem);
        });
    }
});

// Desabilitar município inicialmente
municipioInput.disabled = true;
municipioInput.placeholder = 'Selecione um estado primeiro';
