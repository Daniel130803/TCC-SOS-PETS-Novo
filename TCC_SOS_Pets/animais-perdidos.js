// ===== CONFIGURAÇÕES GLOBAIS =====
const API_BASE_URL = 'http://127.0.0.1:8000/api';
let map = null;
let markersCluster = null;
let allPetsPerdidos = [];
let currentLocation = null;

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
    // Cria o mapa centrado no Brasil
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
async function loadPetsPerdidos() {
    try {
        const estado = document.getElementById('estado-filter')?.value || '';
        const cidade = document.getElementById('cidade-filter')?.value || '';
        
        let url = `${API_BASE_URL}/pets-perdidos/?ativo=true`;
        if (estado) url += `&estado=${estado}`;
        if (cidade) url += `&cidade=${cidade}`;
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro ao carregar pets perdidos');
        
        allPetsPerdidos = await response.json();
        renderPetsOnMap(allPetsPerdidos);
        renderPetsList(allPetsPerdidos);
    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao carregar pets perdidos. Tente novamente.');
    }
}

// ===== RENDERIZAR PETS NO MAPA =====
function renderPetsOnMap(pets) {
    // Limpa marcadores anteriores
    markersCluster.clearLayers();
    
    pets.forEach(pet => {
        // Ícone customizado baseado na espécie
        const iconUrl = pet.especie === 'cachorro' 
            ? 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
            : 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png';
        
        const customIcon = L.icon({
            iconUrl: iconUrl,
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        const marker = L.marker([pet.latitude, pet.longitude], { icon: customIcon });
        
        // Popup com detalhes do pet
        const popupContent = `
            <div class="pet-popup">
                <img src="${pet.imagem_principal_url || '/static/Estetica_site/default-pet.png'}" alt="${pet.nome}" style="width: 100%; max-height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
                <h3 style="margin: 5px 0; color: #d32f2f;">${pet.nome}</h3>
                <p style="margin: 3px 0;"><strong>Espécie:</strong> ${pet.especie_display}</p>
                <p style="margin: 3px 0;"><strong>Cor:</strong> ${pet.cor}</p>
                <p style="margin: 3px 0;"><strong>Porte:</strong> ${pet.porte_display}</p>
                <p style="margin: 3px 0;"><strong>Perdido em:</strong> ${formatDate(pet.data_perda)}</p>
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
    
    // Ajusta zoom para mostrar todos os marcadores
    if (pets.length > 0) {
        map.fitBounds(markersCluster.getBounds(), { padding: [50, 50] });
    }
}

// ===== RENDERIZAR LISTA DE PETS =====
function renderPetsList(pets) {
    const container = document.getElementById('pets-list-container');
    const noResults = document.getElementById('no-results-message');
    
    if (pets.length === 0) {
        container.innerHTML = '';
        noResults.style.display = 'block';
        return;
    }
    
    noResults.style.display = 'none';
    container.innerHTML = pets.map(pet => `
        <div class="pet-card" onclick="showPetDetails(${pet.id})">
            <div class="pet-card-image">
                <img src="${pet.imagem_principal_url || '/static/Estetica_site/default-pet.png'}" alt="${pet.nome}">
                ${pet.oferece_recompensa ? '<div class="reward-badge">💰 Recompensa</div>' : ''}
            </div>
            <div class="pet-card-content">
                <h3>${pet.nome}</h3>
                <p><i class="fas fa-paw"></i> ${pet.especie_display} - ${pet.porte_display}</p>
                <p><i class="fas fa-palette"></i> ${pet.cor}</p>
                <p><i class="fas fa-map-marker-alt"></i> ${pet.cidade}/${pet.estado}</p>
                <p><i class="fas fa-calendar"></i> Perdido em ${formatDate(pet.data_perda)}</p>
                <button class="btn-view-details">Ver Detalhes</button>
            </div>
        </div>
    `).join('');
}

// ===== MODAL DE DETALHES DO PET =====
function showPetDetails(petId) {
    const pet = allPetsPerdidos.find(p => p.id === petId);
    if (!pet) return;
    
    const modal = document.getElementById('pet-details-modal');
    const content = document.getElementById('pet-details-content');
    
    content.innerHTML = `
        <button class="modal-close" onclick="closePetDetailsModal()">&times;</button>
        <div class="pet-details-grid">
            <div class="pet-details-images">
                <img src="${pet.imagem_principal_url || '/static/Estetica_site/default-pet.png'}" alt="${pet.nome}" class="main-image">
                ${pet.fotos_adicionais && pet.fotos_adicionais.length > 0 ? `
                    <div class="additional-photos">
                        ${pet.fotos_adicionais.map(foto => `
                            <img src="${foto.imagem_url}" alt="Foto adicional" onclick="this.parentElement.previousElementSibling.src = this.src">
                        `).join('')}
                    </div>
                ` : ''}
            </div>
            <div class="pet-details-info">
                <h2>${pet.nome}</h2>
                ${pet.oferece_recompensa ? `
                    <div class="reward-banner">
                        <i class="fas fa-gift"></i>
                        <span>Recompensa de R$ ${pet.valor_recompensa}</span>
                    </div>
                ` : ''}
                
                <div class="info-section">
                    <h3><i class="fas fa-info-circle"></i> Informações Básicas</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <strong>Espécie:</strong>
                            <span>${pet.especie_display}</span>
                        </div>
                        <div class="info-item">
                            <strong>Raça:</strong>
                            <span>${pet.raca || 'Não informada'}</span>
                        </div>
                        <div class="info-item">
                            <strong>Cor:</strong>
                            <span>${pet.cor}</span>
                        </div>
                        <div class="info-item">
                            <strong>Porte:</strong>
                            <span>${pet.porte_display}</span>
                        </div>
                        <div class="info-item">
                            <strong>Sexo:</strong>
                            <span>${pet.sexo_display}</span>
                        </div>
                        <div class="info-item">
                            <strong>Idade:</strong>
                            <span>${pet.idade_aproximada || 'Não informada'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3><i class="fas fa-search"></i> Informações da Perda</h3>
                    <div class="info-item">
                        <strong>Data da Perda:</strong>
                        <span>${formatDate(pet.data_perda)}${pet.hora_perda ? ` às ${pet.hora_perda}` : ''}</span>
                    </div>
                    <div class="info-item">
                        <strong>Local:</strong>
                        <span>${pet.endereco}, ${pet.bairro} - ${pet.cidade}/${pet.estado}</span>
                    </div>
                    <div class="info-item">
                        <strong>Características Distintivas:</strong>
                        <p>${pet.caracteristicas_distintivas}</p>
                    </div>
                    <div class="info-item">
                        <strong>Descrição:</strong>
                        <p>${pet.descricao}</p>
                    </div>
                </div>
                
                <div class="info-section contact-section">
                    <h3><i class="fas fa-phone"></i> Informações de Contato</h3>
                    <div class="contact-buttons">
                        <a href="tel:${pet.telefone_contato}" class="btn-contact phone">
                            <i class="fas fa-phone"></i> ${pet.telefone_contato}
                        </a>
                        ${pet.whatsapp ? `
                            <a href="https://wa.me/55${pet.whatsapp.replace(/\D/g, '')}" target="_blank" class="btn-contact whatsapp">
                                <i class="fab fa-whatsapp"></i> WhatsApp
                            </a>
                        ` : ''}
                        <a href="mailto:${pet.email_contato}" class="btn-contact email">
                            <i class="fas fa-envelope"></i> E-mail
                        </a>
                    </div>
                    <p style="text-align: center; margin-top: 15px; color: #666; font-size: 0.9em;">
                        <i class="fas fa-heart"></i> Se você viu este pet, entre em contato!
                    </p>
                </div>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closePetDetailsModal() {
    document.getElementById('pet-details-modal').style.display = 'none';
}

// ===== MODAL "PERDI MEU PET" =====
function openLostPetModal() {
    document.getElementById('lost-pet-modal').style.display = 'flex';
    initLocationPicker('lost');
}

function closeLostPetModal() {
    document.getElementById('lost-pet-modal').style.display = 'none';
    document.getElementById('lost-pet-form').reset();
}

async function submitLostPet(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert('Você precisa estar logado para registrar um pet perdido.');
        window.location.href = '/login/';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/pets-perdidos/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao registrar pet perdido');
        }
        
        alert('Pet registrado com sucesso! Vamos ajudar a encontrá-lo.');
        closeLostPetModal();
        loadPetsPerdidos();
    } catch (error) {
        console.error('Erro:', error);
        alert(error.message);
    }
}

// ===== MODAL "ENCONTREI UM PET" =====
function openFoundPetModal() {
    document.getElementById('found-pet-modal').style.display = 'flex';
    initLocationPicker('found');
}

function closeFoundPetModal() {
    document.getElementById('found-pet-modal').style.display = 'none';
    document.getElementById('found-pet-form').reset();
}

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
            alert(`Reporte enviado! Encontramos ${result.possiveis_matches.length} possível(is) match(es). Nossa equipe entrará em contato em breve.`);
        } else {
            alert('Reporte enviado com sucesso! Nossa equipe analisará e entrará em contato se encontrarmos um match.');
        }
        
        closeFoundPetModal();
    } catch (error) {
        console.error('Erro:', error);
        alert(error.message);
    }
}

// ===== SELETOR DE LOCALIZAÇÃO NO MAPA =====
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
    
    const select = document.getElementById('estado-filter');
    if (select) {
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado;
            option.textContent = estado;
            select.appendChild(option);
        });
    }
}

// ===== EVENT LISTENERS =====
function initEventListeners() {
    // Botões de abertura de modais
    document.getElementById('btn-open-lost-pet-modal')?.addEventListener('click', openLostPetModal);
    document.getElementById('btn-open-found-pet-modal')?.addEventListener('click', openFoundPetModal);
    
    // Botões de fechamento
    document.getElementById('btn-close-lost-pet-modal')?.addEventListener('click', closeLostPetModal);
    document.getElementById('btn-close-found-pet-modal')?.addEventListener('click', closeFoundPetModal);
    
    // Submissão de formulários
    document.getElementById('lost-pet-form')?.addEventListener('submit', submitLostPet);
    document.getElementById('found-pet-form')?.addEventListener('submit', submitFoundPet);
    
    // Filtros
    document.getElementById('estado-filter')?.addEventListener('change', loadPetsPerdidos);
    document.getElementById('cidade-filter')?.addEventListener('input', debounce(loadPetsPerdidos, 500));
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

function showError(message) {
    alert(message);
}
