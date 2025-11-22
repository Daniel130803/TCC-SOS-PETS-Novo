// ===== CONFIGURAÇÕES GLOBAIS =====
const API_BASE_URL = 'http://127.0.0.1:8000/api';
let map = null;
let markersCluster = null;
let allPetsPerdidos = [];
let currentLocation = null;

// Mapas dos modais
let mapLost = null;
let markerLost = null;
let mapFound = null;
let markerFound = null;

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadPetsPerdidos();
    initEventListeners();
    loadEstados();
    getUserLocation();
});

// ===== MAPA COM LEAFLET =====
function initMap() {
    // Cria o mapa centrado no Brasil (sem zoom inicial)
    map = L.map('map-container').setView([-14.235, -51.9253], 4);
    
    // Adiciona tiles do OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Inicializa cluster de marcadores
    markersCluster = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true
    });
    
    map.addLayer(markersCluster);
}

// ===== CARREGAR PETS PERDIDOS =====
async function loadPetsPerdidos(debug = false) {
    try {
        const estado = document.getElementById('estado-filter')?.value || '';
        const cidade = document.getElementById('cidade-filter')?.value || '';
        const especie = document.getElementById('especie-filter')?.value || '';
        
        // Se debug=true, carrega TODOS os pets sem filtro de ativo
        let url = `${API_BASE_URL}/pets-perdidos/`;
        
        // Adiciona filtros
        const params = [];
        if (!debug) params.push('ativo=true'); // Só filtra por ativo se não for debug
        if (estado) params.push(`estado=${estado}`);
        if (cidade) params.push(`cidade=${cidade}`);
        if (especie) params.push(`especie=${especie}`);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        console.log('🔍 Carregando pets perdidos da URL:', url);
        console.log('🐛 Modo debug:', debug ? 'SIM (todos os pets)' : 'NÃO (apenas ativos)');
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro ao carregar pets perdidos');
        
        const data = await response.json();
        console.log('📦 Dados recebidos da API:', data);
        console.log('📊 Tipo de dados:', typeof data);
        console.log('🔍 É array?', Array.isArray(data));
        console.log('🔍 Tem results?', data.results ? 'Sim' : 'Não');
        console.log('🔍 Estrutura do objeto:', Object.keys(data));
        
        // A API pode retornar um array direto ou um objeto com 'results'
        allPetsPerdidos = Array.isArray(data) ? data : (data.results || []);
        
        console.log(`✅ Total de pets carregados: ${allPetsPerdidos.length}`);
        if (allPetsPerdidos.length > 0) {
            console.log('🐾 Primeiro pet:', allPetsPerdidos[0]);
        } else {
            console.warn('⚠️ Nenhum pet foi retornado pela API');
            console.warn('⚠️ Verifique se o filtro ativo=true está correto');
            console.warn('⚠️ Verifique se o pet foi salvo com ativo=true no backend');
        }
        
        renderPetsOnMap(allPetsPerdidos);
        renderPetsList(allPetsPerdidos);
    } catch (error) {
        console.error('❌ Erro:', error);
        showError('Erro ao carregar pets perdidos. Tente novamente.');
        // Renderiza listas vazias em caso de erro
        renderPetsOnMap([]);
        renderPetsList([]);
    }
}

// ===== RENDERIZAR PETS NO MAPA =====
function renderPetsOnMap(pets) {
    // Limpa marcadores anteriores
    markersCluster.clearLayers();
    
    console.log(`📍 Renderizando ${pets.length} pets no mapa`);
    
    pets.forEach(pet => {
        // Verifica se tem coordenadas válidas
        if (!pet.latitude || !pet.longitude) {
            console.warn(`⚠️ Pet ${pet.nome} (ID: ${pet.id}) sem coordenadas válidas:`, {
                latitude: pet.latitude,
                longitude: pet.longitude
            });
            return; // Pula este pet
        }
        
        console.log(`✅ Adicionando marcador para ${pet.nome}:`, {
            lat: pet.latitude,
            lng: pet.longitude,
            status: pet.status
        });
        
        // Ícone customizado baseado no status (perdido=vermelho, encontrado=verde)
        let iconColor = 'red'; // padrão para perdido
        if (pet.status === 'encontrado') {
            iconColor = 'green';
        }
        
        const iconUrl = `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${iconColor}.png`;
        
        const customIcon = L.icon({
            iconUrl: iconUrl,
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        const marker = L.marker([pet.latitude, pet.longitude], { icon: customIcon });
        
        // Cor do título baseado no status
        const titleColor = iconColor === 'red' ? '#d32f2f' : '#4CAF50';
        const statusText = pet.status === 'encontrado' ? 'Encontrado' : 'Perdido';
        
        // Popup com detalhes do pet
        const popupContent = `
            <div class="pet-popup">
                <img src="${pet.imagem_principal_url || '/static/Estetica_site/default-pet.png'}" alt="${pet.nome}" style="width: 100%; max-height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
                <h3 style="margin: 5px 0; color: ${titleColor};">${pet.nome}</h3>
                <p style="margin: 3px 0;"><strong>Status:</strong> <span style="color: ${titleColor};">${statusText}</span></p>
                <p style="margin: 3px 0;"><strong>Espécie:</strong> ${pet.especie_display}</p>
                <p style="margin: 3px 0;"><strong>Cor:</strong> ${pet.cor}</p>
                <p style="margin: 3px 0;"><strong>Porte:</strong> ${pet.porte_display}</p>
                <p style="margin: 3px 0;"><strong>${statusText} em:</strong> ${formatDate(pet.status === 'encontrado' ? pet.data_encontro : pet.data_perda)}</p>
                <p style="margin: 3px 0;"><strong>Local:</strong> ${pet.bairro}, ${pet.cidade}/${pet.estado}</p>
                ${pet.oferece_recompensa ? `<p style="margin: 3px 0; color: #4CAF50;"><strong>💰 Recompensa: R$ ${pet.valor_recompensa}</strong></p>` : ''}
                <button onclick="showPetDetails(${pet.id})" style="
                    width: 100%;
                    padding: 8px;
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 10px;
                    font-weight: bold;
                ">Ver Detalhes Completos</button>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        markersCluster.addLayer(marker);
    });
    
    // Ajusta zoom do mapa baseado nos filtros
    const estadoFiltro = document.getElementById('estado-filter')?.value;
    const cidadeFiltro = document.getElementById('cidade-filter')?.value;
    
    if (cidadeFiltro && pets.length > 0) {
        // Foca na cidade - pega coordenadas da cidade
        const petsComCoord = pets.filter(p => p.latitude && p.longitude);
        if (petsComCoord.length > 0) {
            const latSum = petsComCoord.reduce((sum, p) => sum + parseFloat(p.latitude), 0);
            const lngSum = petsComCoord.reduce((sum, p) => sum + parseFloat(p.longitude), 0);
            const latAvg = latSum / petsComCoord.length;
            const lngAvg = lngSum / petsComCoord.length;
            map.setView([latAvg, lngAvg], 12);
        }
    } else if (estadoFiltro && pets.length > 0) {
        // Foca no estado - zoom médio
        const petsComCoord = pets.filter(p => p.latitude && p.longitude);
        if (petsComCoord.length > 0) {
            const latSum = petsComCoord.reduce((sum, p) => sum + parseFloat(p.latitude), 0);
            const lngSum = petsComCoord.reduce((sum, p) => sum + parseFloat(p.longitude), 0);
            const latAvg = latSum / petsComCoord.length;
            const lngAvg = lngSum / petsComCoord.length;
            map.setView([latAvg, lngAvg], 7);
        }
    } else {
        // Sem filtros ativos - sempre foca no Brasil com zoom 4
        map.setView([-14.235, -51.9253], 4);
    }
}

// ===== RENDERIZAR LISTA DE PETS =====
function renderPetsList(pets) {
    const container = document.getElementById('pets-list-container');
    const noResults = document.getElementById('no-results-message');
    
    if (!container) {
        console.error('❌ Container pets-list-container não encontrado');
        return;
    }
    
    if (pets.length === 0) {
        container.innerHTML = '';
        if (noResults) noResults.style.display = 'block';
        return;
    }
    
    if (noResults) noResults.style.display = 'none';
    container.innerHTML = pets.map(pet => `
        <div class="animal-card" data-id="${pet.id}" onclick="showPetDetails(${pet.id})" style="position: relative;">
            <div class="card-image-container" style="position: relative;">
                <img src="${pet.imagem_principal_url || '/static/Estetica_site/default-pet.png'}" alt="${pet.nome}">
                ${pet.oferece_recompensa ? '<div class="reward-badge" style="position: absolute; top: 10px; right: 10px; background: linear-gradient(135deg, #FFD700, #FFA500); color: #333; padding: 5px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; z-index: 2;"><i class="fas fa-gift"></i> Recompensa</div>' : ''}
                <div class="status-badge" style="position: absolute; top: 10px; left: 10px; padding: 5px 15px; border-radius: 20px; font-weight: bold; color: white; background: ${pet.status === 'perdido' ? '#d32f2f' : '#4CAF50'}; z-index: 2;">${pet.status === 'perdido' ? 'PERDIDO' : 'ENCONTRADO'}</div>
            </div>
            <div class="card-content">
                <div class="card-header">
                    <h4>${pet.nome}</h4>
                    <div class="card-icons">
                        ${pet.sexo === 'femea' ? '<i class="fas fa-venus" title="Fêmea"></i>' : pet.sexo === 'macho' ? '<i class="fas fa-mars" title="Macho"></i>' : ''}
                    </div>
                </div>
                <p class="location"><i class="fas fa-map-marker-alt"></i> ${pet.cidade}/${pet.estado}</p>
                <div class="details-hidden">
                    <span>${pet.especie_display}</span>
                    <span>${pet.porte_display}</span>
                </div>
                <p style="color: #666; font-size: 0.9rem; margin: 8px 0;"><i class="fas fa-calendar"></i> ${formatDate(pet.data_perda)}</p>
                <button class="card-button">Ver Detalhes Completos</button>
            </div>
        </div>
    `).join('');
}

// ===== MODAL DE DETALHES DO PET =====
function showPetDetails(petId) {
    console.log('🔍 Abrindo detalhes do pet ID:', petId);
    const pet = allPetsPerdidos.find(p => p.id === petId);
    if (!pet) {
        console.error('❌ Pet não encontrado:', petId);
        return;
    }
    
    console.log('✅ Pet encontrado:', pet);
    
    const modal = document.getElementById('pet-details-modal');
    const content = document.getElementById('pet-details-content');
    
    if (!modal || !content) {
        console.error('❌ Elementos do modal não encontrados!');
        return;
    }
    
    const statusColor = pet.status === 'perdido' ? '#d32f2f' : '#4CAF50';
    const statusText = pet.status === 'perdido' ? 'PERDIDO' : 'ENCONTRADO';
    
    content.innerHTML = `
        <div style="position: relative; max-width: 1000px; width: 100%; background: white; border-radius: 0; max-height: 100vh; overflow-y: auto; margin: 0;">
            <button class="modal-close" onclick="closePetDetailsModal()" style="position: absolute; top: 15px; right: 15px; width: 40px; height: 40px; border: none; background: rgba(0,0,0,0.7); color: white; font-size: 24px; border-radius: 50%; cursor: pointer; z-index: 1001; display: flex; align-items: center; justify-content: center; transition: all 0.3s;">&times;</button>
            
            <div style="background: ${statusColor}; color: white; padding: 25px; border-radius: 0;">
                <h2 style="margin: 0; font-size: 32px; font-weight: bold;">
                    <i class="fas fa-paw"></i> ${pet.nome}
                </h2>
                <div style="background: rgba(255,255,255,0.25); display: inline-block; padding: 8px 20px; border-radius: 25px; margin-top: 12px; font-weight: bold; font-size: 16px;">
                    ${statusText}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 45% 55%; gap: 0; min-height: 500px;">
                <div style="padding: 30px; background: #f9f9f9;">
                    <img src="${pet.imagem_principal_url || '/static/Estetica_site/default-pet.png'}" alt="${pet.nome}" style="width: 100%; height: auto; max-height: 450px; object-fit: contain; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.15); background: white; padding: 10px;">
                    
                    ${pet.fotos_adicionais && pet.fotos_adicionais.length > 0 ? `
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px;">
                            ${pet.fotos_adicionais.map(foto => `
                                <img src="${foto.imagem_url}" alt="Foto adicional" style="width: 100%; height: 90px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 3px solid #ddd; transition: all 0.3s;" onclick="this.parentElement.previousElementSibling.src = this.src; this.style.borderColor='${statusColor}';" onmouseover="this.style.borderColor='${statusColor}';" onmouseout="this.style.borderColor='#ddd';">
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${pet.oferece_recompensa ? `
                        <div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: #222; padding: 25px; border-radius: 12px; margin-top: 25px; text-align: center; font-size: 20px; font-weight: bold; box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);">
                            <i class="fas fa-gift" style="font-size: 32px; margin-bottom: 10px; display: block;"></i>
                            Recompensa de<br>R$ ${pet.valor_recompensa}
                        </div>
                    ` : ''}
                </div>
                
                <div style="padding: 30px; overflow-y: auto; max-height: 100vh;">
                    <div style="background: #fff; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <h3 style="margin-top: 0; color: #333; border-bottom: 3px solid ${statusColor}; padding-bottom: 12px; font-size: 20px;">
                            <i class="fas fa-info-circle"></i> Informações Básicas
                        </h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 15px;">
                            <div style="padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor}; display: block; margin-bottom: 5px;">Espécie:</strong>
                                <span style="font-size: 15px;">${pet.especie_display}</span>
                            </div>
                            <div style="padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor}; display: block; margin-bottom: 5px;">Raça:</strong>
                                <span style="font-size: 15px;">${pet.raca || 'Não informada'}</span>
                            </div>
                            <div style="padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor}; display: block; margin-bottom: 5px;">Cor:</strong>
                                <span style="font-size: 15px;">${pet.cor}</span>
                            </div>
                            <div style="padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor}; display: block; margin-bottom: 5px;">Porte:</strong>
                                <span style="font-size: 15px;">${pet.porte_display}</span>
                            </div>
                            <div style="padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor}; display: block; margin-bottom: 5px;">Sexo:</strong>
                                <span style="font-size: 15px;">${pet.sexo_display}</span>
                            </div>
                            <div style="padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor}; display: block; margin-bottom: 5px;">Idade:</strong>
                                <span style="font-size: 15px;">${pet.idade_aproximada || 'Não informada'}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #fff; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <h3 style="margin-top: 0; color: #333; border-bottom: 3px solid ${statusColor}; padding-bottom: 12px; font-size: 20px;">
                            <i class="fas fa-map-marker-alt"></i> Informações da ${pet.status === 'perdido' ? 'Perda' : 'Localização'}
                        </h3>
                        <div style="margin-top: 15px; line-height: 1.8;">
                            <p style="margin: 12px 0; padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor};">Data:</strong><br>
                                <span style="font-size: 15px;">${formatDate(pet.data_perda)}${pet.hora_perda ? ` às ${pet.hora_perda}` : ''}</span>
                            </p>
                            <p style="margin: 12px 0; padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor};">Local:</strong><br>
                                <span style="font-size: 15px;">${pet.endereco}, ${pet.bairro} - ${pet.cidade}/${pet.estado}</span>
                            </p>
                            <p style="margin: 12px 0; padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor};">Características:</strong><br>
                                <span style="font-size: 15px;">${pet.caracteristicas_distintivas}</span>
                            </p>
                            <p style="margin: 12px 0; padding: 12px; background: #f8f8f8; border-radius: 8px;">
                                <strong style="color: ${statusColor};">Descrição:</strong><br>
                                <span style="font-size: 15px;">${pet.descricao}</span>
                            </p>
                        </div>
                    </div>
                    
                    <div style="background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                        <h3 style="margin-top: 0; color: #333; border-bottom: 3px solid ${statusColor}; padding-bottom: 12px; font-size: 20px;">
                            <i class="fas fa-phone"></i> Informações de Contato
                        </h3>
                        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                            <a href="tel:${pet.telefone_contato}" style="background: #4CAF50; color: white; padding: 15px; text-decoration: none; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px; transition: all 0.3s; display: block;">
                                <i class="fas fa-phone"></i> ${pet.telefone_contato}
                            </a>
                            ${pet.whatsapp ? `
                                <a href="https://wa.me/55${pet.whatsapp.replace(/\D/g, '')}" target="_blank" style="background: #25D366; color: white; padding: 15px; text-decoration: none; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px; transition: all 0.3s; display: block;">
                                    <i class="fab fa-whatsapp"></i> WhatsApp
                                </a>
                            ` : ''}
                            <a href="mailto:${pet.email_contato}" style="background: #2196F3; color: white; padding: 15px; text-decoration: none; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px; transition: all 0.3s; display: block;">
                                <i class="fas fa-envelope"></i> E-mail
                            </a>
                        </div>
                        <p style="text-align: center; margin-top: 20px; color: #666; font-size: 15px; line-height: 1.6;">
                            <i class="fas fa-heart" style="color: #e91e63; font-size: 18px;"></i><br>
                            <strong>Se você viu este pet, entre em contato!</strong>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove todas as classes primeiro
    modal.className = 'modal-overlay';
    
    // FORÇAR ESTILOS COM MÁXIMA ESPECIFICIDADE (sem padding para remover barra branca)
    modal.setAttribute('style', 'display: flex !important; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; z-index: 999999 !important; background: rgba(0, 0, 0, 0.8) !important; justify-content: center !important; align-items: center !important; backdrop-filter: blur(4px) !important; opacity: 1 !important; visibility: visible !important; pointer-events: auto !important; padding: 0 !important;');
    
    document.body.style.overflow = 'hidden';
    
    // Scroll para o topo
    window.scrollTo(0, 0);
    
    // Força reflow
    void modal.offsetHeight;
    
    const computedStyle = window.getComputedStyle(modal);
    console.log('✅ Modal configurado:', {
        display: computedStyle.display,
        opacity: computedStyle.opacity,
        visibility: computedStyle.visibility,
        zIndex: computedStyle.zIndex,
        position: computedStyle.position
    });
    
    console.log('✅ Modal de detalhes aberto');
}

function closePetDetailsModal() {
    console.log('🚪 Fechando modal de detalhes...');
    const modal = document.getElementById('pet-details-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.style.visibility = 'hidden';
        modal.style.opacity = '0';
        document.body.style.overflow = '';
        console.log('✅ Modal fechado');
    }
}

// Torna função global para onclick
window.closePetDetailsModal = closePetDetailsModal;

// ===== MODAL "PERDI MEU PET" =====
// Funções movidas para o HTML inline para garantir funcionamento

async function submitLostPet(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access');
    
    console.log('🐾 Iniciando submissão do formulário de pet perdido');
    
    if (!token) {
        toast.error('Você precisa estar logado para registrar um pet perdido.');
        setTimeout(() => { window.location.href = '/login/'; }, 1500);
        return;
    }
    
    // Validações robustas
    const nome = document.getElementById('lost-nome').value.trim();
    const especie = document.getElementById('lost-especie').value;
    const cor = document.getElementById('lost-cor').value.trim();
    const caracteristicas = document.getElementById('lost-caracteristicas').value.trim();
    const descricao = document.getElementById('lost-descricao').value.trim();
    const endereco = document.getElementById('lost-endereco').value.trim();
    const bairro = document.getElementById('lost-bairro').value.trim();
    const cidade = document.getElementById('lost-cidade').value.trim();
    const latitude = document.getElementById('lost-latitude').value;
    const longitude = document.getElementById('lost-longitude').value;
    
    const validacoes = {
        nome: validateTexto(nome, 'Nome do Pet', 2, 100),
        especie: especie ? { valid: true, message: '' } : { valid: false, message: 'Selecione a espécie' },
        cor: validateTexto(cor, 'Cor', 3, 50),
        caracteristicas: validateTexto(caracteristicas, 'Características', 10, 500),
        descricao: validateTexto(descricao, 'Descrição', 20, 2000),
        endereco: validateTexto(endereco, 'Endereço', 5, 300),
        bairro: validateTexto(bairro, 'Bairro', 3, 100),
        cidade: validateTexto(cidade, 'Cidade', 3, 100),
        localizacao: (latitude && longitude) ? { valid: true, message: '' } : { valid: false, message: 'Clique em "Localizar no Mapa" e selecione a localização' }
    };
    
    // Valida imagem se presente
    const imagem = document.getElementById('lost-imagem-principal')?.files[0];
    if (imagem) {
        validacoes.imagem = validateImagem(imagem, 5);
    }
    
    const valido = validateForm(validacoes);
    if (!valido) return;
    
    const formData = new FormData(event.target);
    
    // Sanitiza campos de texto
    formData.set('nome', sanitizeInput(nome));
    formData.set('cor', sanitizeInput(cor));
    formData.set('caracteristicas_distintivas', sanitizeInput(caracteristicas));
    formData.set('descricao', sanitizeInput(descricao));
    formData.set('endereco', sanitizeInput(endereco));
    formData.set('bairro', sanitizeInput(bairro));
    formData.set('cidade', sanitizeInput(cidade));
    
    // Log dos dados do formulário
    console.log('📋 Dados do formulário validados e sanitizados');
    
    try {
        console.log('🚀 Enviando requisição para:', `${API_BASE_URL}/pets-perdidos/`);
        
        const response = await fetch(`${API_BASE_URL}/pets-perdidos/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        console.log('📡 Resposta recebida:', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Erro da API (texto):', errorText);
            
            let errorData;
            try {
                errorData = JSON.parse(errorText);
                console.error('❌ Erro da API (JSON):', errorData);
            } catch (e) {
                errorData = { detail: errorText || 'Erro ao registrar pet perdido' };
            }
            
            // Mostra mensagens de erro mais específicas
            if (errorData.latitude || errorData.longitude) {
                throw new Error('Por favor, clique em "Localizar no Mapa" e selecione a localização onde o pet foi perdido.');
            }
            
            if (errorData.detail) {
                throw new Error(errorData.detail);
            }
            
            // Se houver erros de validação de campos
            const errorMessages = [];
            for (const [field, messages] of Object.entries(errorData)) {
                if (Array.isArray(messages)) {
                    errorMessages.push(`${field}: ${messages.join(', ')}`);
                } else if (typeof messages === 'string') {
                    errorMessages.push(`${field}: ${messages}`);
                }
            }
            
            if (errorMessages.length > 0) {
                throw new Error('Erros de validação:\n' + errorMessages.join('\n'));
            }
            
            throw new Error('Erro ao registrar pet perdido');
        }
        
        const result = await response.json();
        console.log('✅ Pet registrado com sucesso:', result);
        
        toast.success('✅ Pet registrado com sucesso! Vamos ajudar a encontrá-lo.');
        if(window.fecharModalLost) window.fecharModalLost();
        loadPetsPerdidos();
    } catch (error) {
        console.error('💥 Erro durante submissão:', error);
        const friendlyMessage = getFriendlyErrorMessage(error.message);
        toast.error(friendlyMessage);
    }
}

// ===== MODAL "ENCONTREI UM PET" =====
// Funções movidas para o HTML inline para garantir funcionamento

async function submitFoundPet(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    try {
        const response = await fetch(`${API_BASE_URL}/pets-encontrados/`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao enviar reporte');
        }
        
        const result = await response.json();
        
        // Mostra mensagem de sucesso com possíveis matches
        if (result.possiveis_matches && result.possiveis_matches.length > 0) {
            toast.success(`✅ Reporte enviado! Encontramos ${result.possiveis_matches.length} possível(is) match(es). Nossa equipe entrará em contato em breve.`, 6000);
        } else {
            toast.success('Reporte enviado com sucesso! Nossa equipe analisará e entrará em contato se encontrarmos um match.');
        }
        
        if(window.fecharModalFound) window.fecharModalFound();
    } catch (error) {
        console.error('Erro:', error);
        const friendlyMessage = getFriendlyErrorMessage(error.message);
        toast.error(friendlyMessage);
    }
}

// ===== SELETOR DE LOCALIZAÇÃO NO MAPA (DESCONTINUADO) =====
// Substituído por initMapLost() e initMapFound()
/*
let locationPickerMap = null;
let locationMarker = null;

function initLocationPicker(type) {
    const mapId = type === 'lost' ? 'location-picker-map-lost' : 'location-picker-map-found';
    const mapContainer = document.getElementById(mapId);
    
    if (!mapContainer) return;
    
    // Remove mapa anterior se existir
    if (locationPickerMap) {
        locationPickerMap.remove();
    }
    
    // Cria novo mapa
    setTimeout(() => {
        locationPickerMap = L.map(mapId).setView(currentLocation || [-14.235, -51.9253], currentLocation ? 13 : 4);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(locationPickerMap);
        
        // Click no mapa para selecionar localização
        locationPickerMap.on('click', function(e) {
            if (locationMarker) {
                locationPickerMap.removeLayer(locationMarker);
            }
            
            locationMarker = L.marker(e.latlng).addTo(locationPickerMap);
            
            // Atualiza campos de latitude e longitude
            document.getElementById(`${type}-latitude`).value = e.latlng.lat;
            document.getElementById(`${type}-longitude`).value = e.latlng.lng;
            
            // Busca endereço reverso
            reverseGeocode(e.latlng.lat, e.latlng.lng, type);
        });
    }, 100);
}

async function reverseGeocode(lat, lng, type) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`);
        const data = await response.json();
        
        if (data.address) {
            document.getElementById(`${type}-cidade`).value = data.address.city || data.address.town || data.address.village || '';
            document.getElementById(`${type}-estado`).value = data.address.state_code || '';
            document.getElementById(`${type}-bairro`).value = data.address.suburb || data.address.neighbourhood || '';
            document.getElementById(`${type}-endereco`).value = data.display_name || '';
        }
    } catch (error) {
        console.error('Erro ao buscar endereço:', error);
    }
}
*/

// ===== GEOLOCALIZAÇÃO DO USUÁRIO =====
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                currentLocation = [position.coords.latitude, position.coords.longitude];
                map.setView(currentLocation, 13);
            },
            error => console.log('Geolocalização não permitida:', error)
        );
    }
}

// ===== CARREGAR ESTADOS =====
async function loadEstados() {
    const estados = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ];
    
    // Popular filtro de estado
    const filterSelect = document.getElementById('estado-filter');
    if (filterSelect) {
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado;
            option.textContent = estado;
            filterSelect.appendChild(option);
        });
    }
    
    // Popular select de estado no modal "Perdi meu Pet"
    const lostEstadoSelect = document.getElementById('lost-estado');
    if (lostEstadoSelect) {
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado;
            option.textContent = estado;
            lostEstadoSelect.appendChild(option);
        });
    }
    
    // Popular select de estado no modal "Encontrei um Pet"
    const foundEstadoSelect = document.getElementById('found-estado');
    if (foundEstadoSelect) {
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado;
            option.textContent = estado;
            foundEstadoSelect.appendChild(option);
        });
    }
}

// ===== CARREGAR CIDADES DO ESTADO =====
async function loadCidadesForEstado(estado) {
    const cidadeSelect = document.getElementById('cidade-filter');
    if (!cidadeSelect) return;
    
    // Limpa e desabilita se nenhum estado selecionado
    if (!estado) {
        cidadeSelect.innerHTML = '<option value="">Escolha um estado</option>';
        cidadeSelect.disabled = true;
        return;
    }
    
    // Habilita e mostra loading
    cidadeSelect.disabled = false;
    cidadeSelect.innerHTML = '<option value="">Carregando cidades...</option>';
    
    try {
        // Busca pets do estado para extrair cidades únicas
        const response = await fetch(`${API_BASE_URL}/pets-perdidos/?estado=${estado}&ativo=true`);
        const data = await response.json();
        const pets = data.results || data;
        
        // Extrai cidades únicas
        const cidades = [...new Set(pets.map(p => p.cidade).filter(c => c))].sort();
        
        cidadeSelect.innerHTML = '<option value="">Todas as cidades</option>';
        cidades.forEach(cidade => {
            const option = document.createElement('option');
            option.value = cidade;
            option.textContent = cidade;
            cidadeSelect.appendChild(option);
        });
        
        console.log(`✅ ${cidades.length} cidades carregadas para ${estado}`);
    } catch (error) {
        console.error('❌ Erro ao carregar cidades:', error);
        cidadeSelect.innerHTML = '<option value="">Erro ao carregar</option>';
    }
}

// ===== EVENT LISTENERS =====
function initEventListeners() {
    // Modais são gerenciados por event listeners inline no HTML
    
    // Submissão de formulários
    document.getElementById('lost-pet-form')?.addEventListener('submit', submitLostPet);
    document.getElementById('found-pet-form')?.addEventListener('submit', submitFoundPet);
    
    // Filtros
    document.getElementById('estado-filter')?.addEventListener('change', async function() {
        await loadCidadesForEstado(this.value);
        loadPetsPerdidos();
    });
    document.getElementById('cidade-filter')?.addEventListener('change', loadPetsPerdidos);
    document.getElementById('especie-filter')?.addEventListener('change', loadPetsPerdidos);
    
    // Fechar modal de detalhes ao clicar fora (padrão funcional de adocao.html)
    const modalDetails = document.getElementById('pet-details-modal');
    if (modalDetails) {
        modalDetails.addEventListener('click', (e) => {
            if (e.target === modalDetails) {
                console.log('👆 Clique fora do modal detectado');
                closePetDetailsModal();
            }
        });
        console.log('✅ Event listener do modal de detalhes adicionado');
    }
    
    // Botões de mapas nos modais
    document.getElementById('btn-mostrar-mapa-lost')?.addEventListener('click', function() {
        const container = document.getElementById('map-container-lost');
        container.style.display = 'block';
        if (!mapLost) {
            setTimeout(() => initMapLost(), 100);
        }
        container.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    
    document.getElementById('btn-mostrar-mapa-found')?.addEventListener('click', function() {
        const container = document.getElementById('map-container-found');
        container.style.display = 'block';
        if (!mapFound) {
            setTimeout(() => initMapFound(), 100);
        }
        container.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
}

// ===== MAPAS DOS MODAIS =====
function initMapLost() {
    mapLost = L.map('location-picker-map-lost').setView([-15.7801, -47.9292], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(mapLost);
    
    markerLost = L.marker([-15.7801, -47.9292], {
        draggable: true,
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(mapLost);
    
    markerLost.on('dragend', function(e) {
        const pos = markerLost.getLatLng();
        updateCoordinatesLost(pos.lat, pos.lng);
    });
    
    mapLost.on('click', function(e) {
        markerLost.setLatLng(e.latlng);
        updateCoordinatesLost(e.latlng.lat, e.latlng.lng);
    });
    
    // Geocoding automático se cidade/estado preenchidos
    const cidade = document.getElementById('lost-cidade')?.value;
    const estado = document.getElementById('lost-estado')?.value;
    if (cidade && estado) {
        geocodeLostAddress(cidade, estado);
    }
}

function initMapFound() {
    mapFound = L.map('location-picker-map-found').setView([-15.7801, -47.9292], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(mapFound);
    
    markerFound = L.marker([-15.7801, -47.9292], {
        draggable: true,
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(mapFound);
    
    markerFound.on('dragend', function(e) {
        const pos = markerFound.getLatLng();
        updateCoordinatesFound(pos.lat, pos.lng);
    });
    
    mapFound.on('click', function(e) {
        markerFound.setLatLng(e.latlng);
        updateCoordinatesFound(e.latlng.lat, e.latlng.lng);
    });
    
    // Geocoding automático se cidade/estado preenchidos
    const cidade = document.getElementById('found-cidade')?.value;
    const estado = document.getElementById('found-estado')?.value;
    if (cidade && estado) {
        geocodeFoundAddress(cidade, estado);
    }
}

function updateCoordinatesLost(lat, lng) {
    document.getElementById('lost-latitude').value = lat.toFixed(6);
    document.getElementById('lost-longitude').value = lng.toFixed(6);
    document.getElementById('coordenadas-display-lost').textContent = 
        `📍 Coordenadas: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
}

function updateCoordinatesFound(lat, lng) {
    document.getElementById('found-latitude').value = lat.toFixed(6);
    document.getElementById('found-longitude').value = lng.toFixed(6);
    document.getElementById('coordenadas-display-found').textContent = 
        `📍 Coordenadas: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
}

async function geocodeLostAddress(cidade, estado) {
    const endereco = `${cidade}, ${estado}, Brasil`;
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(endereco)}&limit=1`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            
            mapLost.setView([lat, lng], 13);
            markerLost.setLatLng([lat, lng]);
            updateCoordinatesLost(lat, lng);
        }
    } catch (error) {
        console.error('Erro no geocoding:', error);
    }
}

async function geocodeFoundAddress(cidade, estado) {
    const endereco = `${cidade}, ${estado}, Brasil`;
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(endereco)}&limit=1`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            
            mapFound.setView([lat, lng], 13);
            markerFound.setLatLng([lat, lng]);
            updateCoordinatesFound(lat, lng);
        }
    } catch (error) {
        console.error('Erro no geocoding:', error);
    }
}

// ===== UTILITÁRIOS =====
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Exibe mensagem de erro usando Toast
 */
function showError(message) {
    toast.error(message);
}
