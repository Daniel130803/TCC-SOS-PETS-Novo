const API_BASE = 'http://localhost:8000/api';
let municipiosCache = {};
let currentEstado = '';
let map = null;
let marker = null;
let geocodingTimeout = null;

// Carregar municípios do IBGE quando o estado for selecionado
const estadoSelect = document.getElementById('estado');
const municipioSelect = document.getElementById('municipio');

function populateMunicipios(municipios) {
    municipioSelect.innerHTML = '<option value="">Selecione o Município...</option>';
    
    municipios.forEach(municipio => {
        const option = document.createElement('option');
        option.value = municipio;
        option.textContent = municipio;
        municipioSelect.appendChild(option);
    });
}

estadoSelect.addEventListener('change', async function() {
    const estado = this.value;
    currentEstado = estado;
    municipioSelect.value = '';
    
    if (!estado) {
        municipioSelect.disabled = true;
        municipioSelect.innerHTML = '<option value="">Selecione um estado primeiro</option>';
        return;
    }

    municipioSelect.disabled = false;
    municipioSelect.innerHTML = '<option value="">Carregando municípios...</option>';

    // Se já temos cache, usar direto
    if (municipiosCache[estado]) {
        populateMunicipios(municipiosCache[estado]);
        return;
    }

    try {
        const response = await fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estado}/municipios`);
        const data = await response.json();
        const municipios = data.map(m => m.nome).sort();
        municipiosCache[estado] = municipios;
        populateMunicipios(municipios);
    } catch (error) {
        console.error('Erro ao carregar municípios:', error);
        municipioSelect.innerHTML = '<option value="">Erro ao carregar municípios</option>';
    }
});

// Enviar formulário via AJAX
const form = document.querySelector('.report-form');
form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const token = localStorage.getItem('access');
    if (!token) {
        toast.error('Você precisa estar logado para fazer uma denúncia.');
        setTimeout(() => { window.location.href = '/login/'; }, 1500);
        return;
    }

    const categoria = document.getElementById('categoria').value;
    const descricao = document.getElementById('descricao').value.trim();
    const localInput = document.getElementById('local').value.trim();
    const estado = document.getElementById('estado').value;
    const municipio = document.getElementById('municipio').value;
    
    // Validações robustas
    const validacoes = {
        categoria: categoria ? { valid: true, message: '' } : { valid: false, message: 'Selecione uma categoria' },
        descricao: validateTexto(descricao, 'Descrição', 30, 3000),
        local: validateTexto(localInput, 'Local', 10, 500),
        estado: estado ? { valid: true, message: '' } : { valid: false, message: 'Selecione o estado' },
        municipio: municipio ? { valid: true, message: '' } : { valid: false, message: 'Selecione o município' }
    };
    
    const valido = validateForm(validacoes);
    if (!valido) return;
    
    // Validação de arquivos
    if (arquivosSelecionados.length > 0) {
        for (let arquivo of arquivosSelecionados) {
            const tipoArquivo = arquivo.type.split('/')[0];
            
            if (tipoArquivo === 'image') {
                const validacaoImagem = validateImagem(arquivo, 5);
                if (!validacaoImagem.valid) {
                    toast.error(validacaoImagem.message);
                    return;
                }
            } else if (tipoArquivo === 'video') {
                const validacaoVideo = validateVideo(arquivo, 20);
                if (!validacaoVideo.valid) {
                    toast.error(validacaoVideo.message);
                    return;
                }
            } else {
                toast.error('Por favor, envie apenas arquivos de imagem (JPG, PNG, WebP) ou vídeo (MP4, AVI, MOV).');
                return;
            }
        }
    }

    const formData = new FormData();
    let localizacao = `${localInput}, ${municipio}/${estado}`;
    
    // Adiciona coordenadas à localização se disponíveis
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;
    
    if (latitude && longitude) {
        localizacao += ` (Coordenadas: ${latitude}, ${longitude})`;
    }
    
    // Sanitização
    const descricaoLimpa = sanitizeInput(descricao);
    const tituloAuto = descricaoLimpa.length > 50 ? descricaoLimpa.substring(0, 50) + '...' : descricaoLimpa;
    
    formData.append('titulo', tituloAuto);
    formData.append('categoria', categoria);
    formData.append('descricao', descricaoLimpa);
    formData.append('localizacao', localizacao);
    
    // Processa arquivos do array acumulado
    if (arquivosSelecionados.length > 0) {
        let primeiraImagem = true;
        let primeiroVideo = true;
        
        for (let i = 0; i < arquivosSelecionados.length; i++) {
            const arquivo = arquivosSelecionados[i];
            const tipoArquivo = arquivo.type.split('/')[0];
            
            if (tipoArquivo === 'image') {
                if (primeiraImagem) {
                    // Primeira imagem vai para o campo principal
                    formData.append('imagem', arquivo);
                    primeiraImagem = false;
                } else {
                    // Demais imagens vão para imagens_adicionais
                    formData.append('imagens_adicionais', arquivo);
                }
            } else if (tipoArquivo === 'video') {
                if (primeiroVideo) {
                    // Primeiro vídeo vai para o campo principal
                    formData.append('video', arquivo);
                    primeiroVideo = false;
                } else {
                    // Demais vídeos vão para videos_adicionais
                    formData.append('videos_adicionais', arquivo);
                }
            } else {
                toast.error('Por favor, envie apenas arquivos de imagem (JPG, PNG, GIF) ou vídeo (MP4, AVI, MOV).');
                return;
            }
        }
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
            if (response.status === 401) {
                toast.error('Sua sessão expirou. Faça login novamente.');
                localStorage.removeItem('access');
                localStorage.removeItem('refresh');
                setTimeout(() => { window.location.href = '/login/'; }, 1500);
                return;
            }
            
            const error = await response.json();
            let mensagemErro = 'Erro ao enviar denúncia.';
            
            if (error.imagem) {
                mensagemErro = 'Erro com a imagem: ' + error.imagem.join(', ');
            } else if (error.video) {
                mensagemErro = 'Erro com o vídeo: ' + error.video.join(', ');
            } else if (error.detail) {
                mensagemErro = error.detail;
            }
            
            throw new Error(mensagemErro);
        }

        toast.success('✅ Denúncia enviada com sucesso! Ela será analisada por nossa equipe.');
        form.reset();
        municipioSelect.disabled = true;
        municipioSelect.innerHTML = '<option value="">Selecione um estado primeiro</option>';
        fileList.innerHTML = '';
        arquivosSelecionados = []; // Limpa array de arquivos
        
        // Reset do mapa
        mapContainer.classList.remove('active');
        latitudeInput.value = '';
        longitudeInput.value = '';
        coordenadasDisplay.textContent = '';
        if (map) {
            map.setView([-15.7801, -47.9292], 4);
            marker.setLatLng([-15.7801, -47.9292]);
        }

    } catch (error) {
        console.error('Erro:', error);
        const friendlyMessage = getFriendlyErrorMessage(error.message);
        toast.error(friendlyMessage || 'Erro ao enviar denúncia. Por favor, tente novamente.');
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
});

// Preview de arquivos
const anexoInput = document.getElementById('anexo');
const fileList = document.getElementById('file-list');
let arquivosSelecionados = [];

anexoInput.addEventListener('change', function() {
    // Adiciona novos arquivos ao array existente ao invés de substituir
    const novosArquivos = Array.from(this.files);
    arquivosSelecionados = [...arquivosSelecionados, ...novosArquivos];
    
    // Atualiza o preview
    atualizarPreviewArquivos();
});

function atualizarPreviewArquivos() {
    fileList.innerHTML = '';
    
    if (arquivosSelecionados.length > 0) {
        let totalImagens = 0;
        let totalVideos = 0;
        let tamanhoTotal = 0;
        
        arquivosSelecionados.forEach((file, fileIndex) => {
            const tipoArquivo = file.type.split('/')[0];
            let icone = 'fa-file';
            let cor = '#999';
            let tipo = 'Arquivo';
            
            if (tipoArquivo === 'image') {
                icone = 'fa-image';
                cor = '#4CAF50';
                tipo = 'Imagem';
                totalImagens++;
            } else if (tipoArquivo === 'video') {
                icone = 'fa-video';
                cor = '#2196F3';
                tipo = 'Vídeo';
                totalVideos++;
            }
            
            tamanhoTotal += file.size;
            
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.style.display = 'flex';
            fileItem.style.justifyContent = 'space-between';
            fileItem.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                    <i class="fas ${icone}" style="color: ${cor};"></i>
                    <span><strong>${tipo}:</strong> ${file.name}</span>
                    <small>(${(file.size / 1024 / 1024).toFixed(2)} MB)</small>
                </div>
                <button type="button" onclick="removerArquivo(${fileIndex})" style="background: #f44336; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 0.8em;">
                    <i class="fas fa-times"></i> Remover
                </button>
            `;
            fileList.appendChild(fileItem);
        });
        
        // Adiciona resumo
        const resumo = document.createElement('div');
        resumo.style.cssText = 'margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 5px; font-weight: 600;';
        resumo.innerHTML = `
            <i class="fas fa-info-circle" style="color: #2196F3;"></i>
            Total: ${totalImagens} imagem(ns) + ${totalVideos} vídeo(s) = ${(tamanhoTotal / 1024 / 1024).toFixed(2)} MB
        `;
        fileList.appendChild(resumo);
    }
}

function removerArquivo(index) {
    arquivosSelecionados.splice(index, 1);
    atualizarPreviewArquivos();
}

// Desabilitar município inicialmente
municipioSelect.disabled = true;

// ===== MAPA INTERATIVO =====
const btnMostrarMapa = document.getElementById('btn-mostrar-mapa');
const mapContainer = document.getElementById('map-container');
const localInput = document.getElementById('local');
const latitudeInput = document.getElementById('latitude');
const longitudeInput = document.getElementById('longitude');
const coordenadasDisplay = document.getElementById('coordenadas-display');

// Inicializar mapa ao clicar no botão
btnMostrarMapa.addEventListener('click', function() {
    if (!estadoSelect.value || !municipioSelect.value || !localInput.value) {
        toast.warning('Por favor, preencha Estado, Município e Local antes de localizar no mapa.');
        return;
    }
    
    mapContainer.classList.add('active');
    
    // Inicializa o mapa apenas uma vez
    if (!map) {
        initMap();
    }
    
    // Faz geocoding do endereço
    geocodeAddress();
    
    // Scroll suave até o mapa
    mapContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
});

function initMap() {
    // Cria mapa centrado no Brasil
    map = L.map('map').setView([-15.7801, -47.9292], 4);
    
    // Adiciona tiles do OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Cria marcador arrastável
    marker = L.marker([-15.7801, -47.9292], {
        draggable: true,
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    // Atualiza coordenadas ao arrastar
    marker.on('dragend', function(e) {
        const position = marker.getLatLng();
        updateCoordinates(position.lat, position.lng);
    });
    
    // Atualiza coordenadas ao clicar no mapa
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        updateCoordinates(e.latlng.lat, e.latlng.lng);
    });
}

function updateCoordinates(lat, lng) {
    latitudeInput.value = lat.toFixed(6);
    longitudeInput.value = lng.toFixed(6);
    coordenadasDisplay.textContent = `📍 Coordenadas: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
}

async function geocodeAddress() {
    const endereco = `${localInput.value}, ${municipioSelect.value}, ${estadoSelect.options[estadoSelect.selectedIndex].text}, Brasil`;
    
    try {
        // Usa API Nominatim do OpenStreetMap para geocoding
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(endereco)}&limit=1`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            
            // Move mapa e marcador para a localização
            map.setView([lat, lng], 16);
            marker.setLatLng([lat, lng]);
            updateCoordinates(lat, lng);
            
            // Adiciona popup informativo
            marker.bindPopup(`<b>Local da Denúncia</b><br>${endereco}`).openPopup();
        } else {
            toast.info('Não foi possível localizar o endereço automaticamente. Você pode ajustar o marcador manualmente no mapa.');
            // Tenta pelo menos centralizar no município
            geocodeMunicipio();
        }
    } catch (error) {
        console.error('Erro no geocoding:', error);
        toast.error('Erro ao buscar localização. Você pode ajustar o marcador manualmente no mapa.');
        geocodeMunicipio();
    }
}

async function geocodeMunicipio() {
    const municipio = `${municipioSelect.value}, ${estadoSelect.options[estadoSelect.selectedIndex].text}, Brasil`;
    
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(municipio)}&limit=1`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            
            map.setView([lat, lng], 13);
            marker.setLatLng([lat, lng]);
            updateCoordinates(lat, lng);
        }
    } catch (error) {
        console.error('Erro ao localizar município:', error);
    }
}

// Atualiza localização quando usuário mudar os campos
[localInput, municipioSelect, estadoSelect].forEach(element => {
    element.addEventListener('change', function() {
        if (map && mapContainer.classList.contains('active')) {
            clearTimeout(geocodingTimeout);
            geocodingTimeout = setTimeout(geocodeAddress, 1000);
        }
    });
});
