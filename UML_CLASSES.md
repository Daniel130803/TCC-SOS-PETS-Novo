# Diagrama UML - Classes
## S.O.S Pets

---

## 1. Visão Geral

Este documento apresenta o diagrama de classes completo do sistema S.O.S Pets, mostrando todas as entidades do domínio, seus atributos, métodos e relacionamentos. O modelo foi desenvolvido utilizando Django ORM com 19 classes principais.

### Principais Módulos
- **Autenticação e Usuários**: Usuario
- **Animais**: Animal, AnimalFoto, AnimalVideo
- **Adoção**: AnimalParaAdocao, SolicitacaoAdocao
- **Pets Perdidos**: PetPerdido, PetPerdidoFoto, ReportePetEncontrado, ReportePetEncontradoFoto
- **Denúncias**: Denuncia, DenunciaImagem, DenunciaVideo, DenunciaHistorico
- **Comunicação**: Notificacao, Contato

---

## 2. Diagrama de Classes Completo

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      MODELO DE CLASSES - S.O.S PETS                         │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐
│         django.contrib.auth     │
│            <<Framework>>         │
├─────────────────────────────────┤
│           User                  │
├─────────────────────────────────┤
│ + username: CharField           │
│ + email: EmailField             │
│ + password: CharField           │
│ + first_name: CharField         │
│ + last_name: CharField          │
│ + is_active: BooleanField       │
│ + is_staff: BooleanField        │
│ + is_superuser: BooleanField    │
│ + date_joined: DateTimeField    │
├─────────────────────────────────┤
│ + set_password()                │
│ + check_password()              │
│ + save()                        │
└─────────────────────────────────┘
              △
              │ OneToOne
              │ (extends)
              │
┌─────────────────────────────────┐
│          Usuario                │
├─────────────────────────────────┤
│ + user: OneToOneField(User)     │
│ + telefone: CharField(15)       │
│ + endereco: TextField           │
│ + data_criacao: DateTimeField   │
│ + data_atualizacao: DateTime    │
├─────────────────────────────────┤
│ + __str__() : str               │
│ + save()                        │
└─────────────────────────────────┘
              △
              │ ForeignKey
              │ (dono)
┌─────────────┼─────────────┐
│             │             │
▼             ▼             ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│      Animal          │  │   PetPerdido         │  │    Denuncia          │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ + dono: FK(Usuario)  │  │ + dono: FK(Usuario)  │  │ + denunciante: FK    │
│ + nome: CharField    │  │ + nome: CharField    │  │ + tipo: CharField    │
│ + especie: CharField │  │ + especie: CharField │  │ + descricao: Text    │
│ + raca: CharField    │  │ + raca: CharField    │  │ + endereco: Text     │
│ + idade: Integer     │  │ + idade: Integer     │  │ + cidade: CharField  │
│ + sexo: CharField    │  │ + sexo: CharField    │  │ + estado: CharField  │
│ + porte: CharField   │  │ + porte: CharField   │  │ + latitude: Decimal  │
│ + descricao: Text    │  │ + cor: CharField     │  │ + longitude: Decimal │
│ + estado: CharField  │  │ + descricao: Text    │  │ + protocolo: Char    │
│ + cidade: CharField  │  │ + data_perdido: Date │  │ + anonima: Boolean   │
│ + imagem_url: URL    │  │ + local_perdido: Text│  │ + status: CharField  │
│ + data_criacao: Date │  │ + cidade: CharField  │  │ + data_criacao: Date │
│ + data_atualizacao   │  │ + estado: CharField  │  │ + moderador: FK(User)│
│ + is_active: Boolean │  │ + latitude: Decimal  │  │ + data_avaliacao     │
├──────────────────────┤  │ + longitude: Decimal │  │ + observacoes_mod    │
│ + __str__() : str    │  │ + recompensa: Decimal│  │ + categoria: Char    │
│ + save()             │  │ + ativo: Boolean     │  ├──────────────────────┤
└──────────────────────┘  │ + status: CharField  │  │ + __str__() : str    │
         △                │ + data_encontrado    │  │ + gerar_protocolo()  │
         │                │ + encontrado_por: FK │  │ + save()             │
         │                ├──────────────────────┤  └──────────────────────┘
         │                │ + __str__() : str    │            △
         │ OneToOne       │ + save()             │            │
         │ (extends)      │ + marcar_encontrado()│            │ ForeignKey
         │                └──────────────────────┘            │ (denuncia)
┌────────┴───────────┐             △                          │
│ AnimalParaAdocao   │             │                          │
├────────────────────┤             │ ForeignKey      ┌────────┴────────────┐
│ + animal: OneToOne │             │ (pet_perdido)   │ DenunciaHistorico   │
│ + vacinado: Boolean│    ┌────────┴───────────┐     ├─────────────────────┤
│ + castrado: Boolean│    │ PetPerdidoFoto     │     │ + denuncia: FK      │
│ + adestrado: Bool  │    ├────────────────────┤     │ + status_anterior   │
│ + temperamento: Text│   │ + pet: FK          │     │ + status_novo       │
│ + caracteristicas  │    │ + foto: ImageField │     │ + observacao: Text  │
│ + adotado: Boolean │    │ + descricao: Text  │     │ + alterado_por: FK  │
│ + adotado_por: FK  │    │ + data_upload      │     │ + data_alteracao    │
│ + data_adocao: Date│    ├────────────────────┤     ├─────────────────────┤
├────────────────────┤    │ + __str__() : str  │     │ + __str__() : str   │
│ + __str__() : str  │    └────────────────────┘     │ + save()            │
│ + save()           │                                └─────────────────────┘
└────────────────────┘    ┌────────────────────┐
         △                │ReportePetEncontrado│     ┌─────────────────────┐
         │                ├────────────────────┤     │   DenunciaImagem    │
         │ ForeignKey     │ + pet_perdido: FK  │     ├─────────────────────┤
         │ (animal)       │ + encontrou: FK    │     │ + denuncia: FK      │
         │                │ + descricao: Text  │     │ + imagem: ImageField│
┌────────┴──────────┐     │ + local: Text      │     │ + descricao: Text   │
│ SolicitacaoAdocao │     │ + cidade: CharField│     │ + data_upload: Date │
├───────────────────┤     │ + estado: CharField│     ├─────────────────────┤
│ + animal: FK      │     │ + latitude: Decimal│     │ + __str__() : str   │
│ + solicitante: FK │     │ + longitude: Decimal│    └─────────────────────┘
│ + mensagem: Text  │     │ + data_encontrado  │
│ + status: CharField│    │ + distancia_km     │     ┌─────────────────────┐
│ + data_solicitacao│     │ + score_similaridade│    │   DenunciaVideo     │
│ + data_resposta   │     │ + contato_feito    │     ├─────────────────────┤
│ + resposta_doador │     │ + visto: Boolean   │     │ + denuncia: FK      │
├───────────────────┤     ├────────────────────┤     │ + video: FileField  │
│ + __str__() : str │     │ + __str__() : str  │     │ + descricao: Text   │
│ + save()          │     │ + calcular_distancia│    │ + data_upload: Date │
│ + aprovar()       │     │ + save()           │     ├─────────────────────┤
│ + rejeitar()      │     └────────────────────┘     │ + __str__() : str   │
└───────────────────┘              △                 └─────────────────────┘
                                   │
         ┌─────────────────────────┘
         │ ForeignKey
         │ (reporte)
         │
┌────────┴──────────────────┐
│ReportePetEncontradoFoto   │
├───────────────────────────┤
│ + reporte: FK             │
│ + foto: ImageField        │
│ + descricao: Text         │
│ + data_upload: DateTime   │
├───────────────────────────┤
│ + __str__() : str         │
└───────────────────────────┘


┌─────────────────────────────────┐
│        Notificacao              │
├─────────────────────────────────┤
│ + usuario: ForeignKey(Usuario)  │
│ + tipo: CharField(50)           │
│ + titulo: CharField(200)        │
│ + mensagem: TextField           │
│ + link: CharField(500)          │
│ + lida: BooleanField            │
│ + data_criacao: DateTimeField   │
│ + data_leitura: DateTimeField   │
├─────────────────────────────────┤
│ + __str__() : str               │
│ + marcar_como_lida()            │
│ + save()                        │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│           Contato               │
├─────────────────────────────────┤
│ + nome: CharField(100)          │
│ + email: EmailField             │
│ + telefone: CharField(15)       │
│ + assunto: CharField(200)       │
│ + mensagem: TextField           │
│ + protocolo: CharField(30)      │
│ + data_contato: DateTimeField   │
│ + status: CharField(20)         │
│ + data_leitura: DateTimeField   │
│ + data_resposta: DateTimeField  │
│ + resposta: TextField           │
├─────────────────────────────────┤
│ + __str__() : str               │
│ + gerar_protocolo() : str       │
│ + save()                        │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│         AnimalFoto              │
├─────────────────────────────────┤
│ + animal: ForeignKey(Animal)    │
│ + imagem: ImageField            │
│ + url: URLField                 │
│ + descricao: CharField(200)     │
│ + data_upload: DateTimeField    │
├─────────────────────────────────┤
│ + __str__() : str               │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│        AnimalVideo              │
├─────────────────────────────────┤
│ + animal: ForeignKey(Animal)    │
│ + video: FileField              │
│ + url: URLField                 │
│ + descricao: CharField(200)     │
│ + data_upload: DateTimeField    │
├─────────────────────────────────┤
│ + __str__() : str               │
└─────────────────────────────────┘
```

---

## 3. Relacionamentos Entre Classes

### 3.1 Usuario (1) ←→ (1) User
- **Tipo**: OneToOneField
- **Descrição**: Extensão do modelo User padrão do Django
- **Cascade**: CASCADE (deletar User deleta Usuario)
- **Campos relacionados**: `usuario.user` / `user.usuario`

### 3.2 Animal (N) ←→ (1) Usuario
- **Tipo**: ForeignKey
- **Descrição**: Cada animal pertence a um dono
- **Cascade**: CASCADE (deletar Usuario deleta todos seus Animais)
- **Campos relacionados**: `animal.dono` / `usuario.animal_set`

### 3.3 AnimalParaAdocao (1) ←→ (1) Animal
- **Tipo**: OneToOneField
- **Descrição**: Extensão de Animal com dados específicos de adoção
- **Cascade**: CASCADE (deletar Animal deleta AnimalParaAdocao)
- **Campos relacionados**: `animal_adocao.animal` / `animal.animalparaadocao`

### 3.4 SolicitacaoAdocao (N) ←→ (1) AnimalParaAdocao
- **Tipo**: ForeignKey
- **Descrição**: Várias solicitações para um mesmo animal
- **Cascade**: CASCADE
- **Campos relacionados**: `solicitacao.animal` / `animal.solicitacoes`

### 3.5 SolicitacaoAdocao (N) ←→ (1) Usuario
- **Tipo**: ForeignKey
- **Descrição**: Cada solicitação tem um solicitante
- **Cascade**: CASCADE
- **Campos relacionados**: `solicitacao.solicitante` / `usuario.solicitacoes_enviadas`

### 3.6 PetPerdido (N) ←→ (1) Usuario
- **Tipo**: ForeignKey
- **Descrição**: Cada pet perdido tem um dono
- **Cascade**: CASCADE
- **Campos relacionados**: `pet_perdido.dono` / `usuario.pets_perdidos`

### 3.7 PetPerdidoFoto (N) ←→ (1) PetPerdido
- **Tipo**: ForeignKey
- **Descrição**: Múltiplas fotos por pet perdido
- **Cascade**: CASCADE
- **Campos relacionados**: `foto.pet_perdido` / `pet_perdido.fotos`

### 3.8 ReportePetEncontrado (N) ←→ (1) PetPerdido
- **Tipo**: ForeignKey
- **Descrição**: Vários reportes podem apontar para o mesmo pet perdido
- **Cascade**: SET_NULL (manter histórico mesmo se pet perdido for deletado)
- **Campos relacionados**: `reporte.pet_perdido` / `pet_perdido.reportes`

### 3.9 ReportePetEncontrado (N) ←→ (1) Usuario
- **Tipo**: ForeignKey (encontrou)
- **Descrição**: Quem encontrou o pet
- **Cascade**: CASCADE
- **Campos relacionados**: `reporte.encontrou` / `usuario.pets_encontrados`

### 3.10 ReportePetEncontradoFoto (N) ←→ (1) ReportePetEncontrado
- **Tipo**: ForeignKey
- **Descrição**: Múltiplas fotos por reporte
- **Cascade**: CASCADE
- **Campos relacionados**: `foto.reporte` / `reporte.fotos`

### 3.11 Denuncia (N) ←→ (1) Usuario
- **Tipo**: ForeignKey (denunciante)
- **Descrição**: Denúncias podem ser anônimas (null=True)
- **Cascade**: SET_NULL
- **Campos relacionados**: `denuncia.denunciante` / `usuario.denuncias`

### 3.12 Denuncia (N) ←→ (1) User (moderador)
- **Tipo**: ForeignKey
- **Descrição**: Moderador que avaliou a denúncia
- **Cascade**: SET_NULL
- **Campos relacionados**: `denuncia.moderador` / `user.denuncias_moderadas`

### 3.13 DenunciaImagem (N) ←→ (1) Denuncia
- **Tipo**: ForeignKey
- **Descrição**: Múltiplas imagens por denúncia
- **Cascade**: CASCADE
- **Campos relacionados**: `imagem.denuncia` / `denuncia.imagens`

### 3.14 DenunciaVideo (N) ←→ (1) Denuncia
- **Tipo**: ForeignKey
- **Descrição**: Múltiplos vídeos por denúncia
- **Cascade**: CASCADE
- **Campos relacionados**: `video.denuncia` / `denuncia.videos`

### 3.15 DenunciaHistorico (N) ←→ (1) Denuncia
- **Tipo**: ForeignKey
- **Descrição**: Histórico de mudanças de status
- **Cascade**: CASCADE
- **Campos relacionados**: `historico.denuncia` / `denuncia.historico`

### 3.16 Notificacao (N) ←→ (1) Usuario
- **Tipo**: ForeignKey
- **Descrição**: Múltiplas notificações por usuário
- **Cascade**: CASCADE
- **Campos relacionados**: `notificacao.usuario` / `usuario.notificacoes`

### 3.17 AnimalFoto (N) ←→ (1) Animal
- **Tipo**: ForeignKey
- **Descrição**: Múltiplas fotos por animal
- **Cascade**: CASCADE
- **Campos relacionados**: `foto.animal` / `animal.fotos`

### 3.18 AnimalVideo (N) ←→ (1) Animal
- **Tipo**: ForeignKey
- **Descrição**: Múltiplos vídeos por animal
- **Cascade**: CASCADE
- **Campos relacionados**: `video.animal` / `animal.videos`

---

## 4. Detalhamento das Classes

### 4.1 Usuario

**Herança**: Composição com django.contrib.auth.User (OneToOneField)

**Atributos:**
- `user`: OneToOneField(User, CASCADE) - Referência ao usuário Django
- `telefone`: CharField(15, blank=True) - Telefone opcional
- `endereco`: TextField(blank=True) - Endereço completo
- `data_criacao`: DateTimeField(auto_now_add=True) - Data de cadastro
- `data_atualizacao`: DateTimeField(auto_now=True) - Última atualização

**Métodos:**
- `__str__()`: Retorna username do User associado
- `save()`: Sobrescrito para lógica customizada

**Relacionamentos:**
- Possui vários Animal (dono)
- Possui vários PetPerdido (dono)
- Possui várias Denuncia (denunciante)
- Possui várias Notificacao
- Possui várias SolicitacaoAdocao (solicitante)
- Possui vários ReportePetEncontrado (encontrou)

---

### 4.2 Animal

**Descrição**: Classe base para todos os animais do sistema

**Atributos:**
- `dono`: ForeignKey(Usuario, CASCADE) - Dono do animal
- `nome`: CharField(100) - Nome do animal
- `especie`: CharField(20) - "cachorro", "gato", "outro"
- `raca`: CharField(100, blank=True) - Raça (opcional)
- `idade`: IntegerField(null=True) - Idade em anos
- `sexo`: CharField(10) - "macho", "femea"
- `porte`: CharField(20) - "pequeno", "medio", "grande"
- `descricao`: TextField - Descrição detalhada
- `estado`: CharField(2) - Sigla UF
- `cidade`: CharField(100) - Nome da cidade
- `imagem_url`: URLField(blank=True) - URL da imagem principal
- `data_criacao`: DateTimeField(auto_now_add=True)
- `data_atualizacao`: DateTimeField(auto_now=True)
- `is_active`: BooleanField(default=True) - Registro ativo

**Métodos:**
- `__str__()`: Retorna "{nome} - {especie}"
- `save()`: Validações antes de salvar

**Relacionamentos:**
- Pertence a um Usuario (dono)
- Pode ter um AnimalParaAdocao (extensão)
- Possui várias AnimalFoto
- Possui vários AnimalVideo

**Validações:**
- Espécie: deve ser "cachorro", "gato" ou "outro"
- Sexo: deve ser "macho" ou "femea"
- Porte: deve ser "pequeno", "medio" ou "grande"
- Estado: deve ser sigla válida de UF

---

### 4.3 AnimalParaAdocao

**Herança**: Extensão de Animal (OneToOneField)

**Atributos:**
- `animal`: OneToOneField(Animal, CASCADE) - Animal base
- `vacinado`: BooleanField(default=False) - Possui vacinas em dia
- `castrado`: BooleanField(default=False) - É castrado
- `adestrado`: BooleanField(default=False) - Possui adestramento
- `temperamento`: TextField - Descrição do comportamento
- `caracteristicas_especiais`: TextField(blank=True) - Necessidades especiais
- `adotado`: BooleanField(default=False) - Foi adotado
- `adotado_por`: ForeignKey(Usuario, SET_NULL, null=True) - Quem adotou
- `data_adocao`: DateTimeField(null=True) - Quando foi adotado

**Métodos:**
- `__str__()`: Retorna "Adoção: {animal.nome}"
- `save()`: Atualiza is_active do animal quando adotado

**Relacionamentos:**
- Estende um Animal (animal)
- Possui várias SolicitacaoAdocao
- Adotado por um Usuario (adotado_por)

---

### 4.4 SolicitacaoAdocao

**Descrição**: Representa solicitação de adoção de um usuário

**Atributos:**
- `animal`: ForeignKey(AnimalParaAdocao, CASCADE) - Animal desejado
- `solicitante`: ForeignKey(Usuario, CASCADE) - Quem solicita
- `mensagem`: TextField - Mensagem ao doador
- `status`: CharField(20) - "pendente", "aprovada", "rejeitada", "cancelada"
- `data_solicitacao`: DateTimeField(auto_now_add=True)
- `data_resposta`: DateTimeField(null=True) - Quando foi respondida
- `resposta_doador`: TextField(blank=True) - Resposta do doador

**Métodos:**
- `__str__()`: Retorna "Solicitação de {solicitante} para {animal}"
- `save()`: Cria notificação ao salvar
- `aprovar()`: Aprova solicitação e cria notificação
- `rejeitar()`: Rejeita solicitação e cria notificação

**Relacionamentos:**
- Pertence a um AnimalParaAdocao (animal)
- Pertence a um Usuario (solicitante)

**Regras de Negócio:**
- Status padrão: "pendente"
- Ao aprovar: atualiza animal.adotado = True, animal.adotado_por = solicitante
- Rejeita automaticamente outras solicitações pendentes do mesmo animal

---

### 4.5 PetPerdido

**Descrição**: Registro de pet perdido com geolocalização

**Atributos:**
- `dono`: ForeignKey(Usuario, CASCADE) - Dono do pet
- `nome`: CharField(100) - Nome do pet
- `especie`: CharField(20) - "cachorro", "gato", "outro"
- `raca`: CharField(100, blank=True) - Raça
- `idade`: IntegerField(null=True) - Idade aproximada
- `sexo`: CharField(10) - "macho", "femea"
- `porte`: CharField(20) - "pequeno", "medio", "grande"
- `cor`: CharField(100) - Cor predominante
- `descricao`: TextField - Características detalhadas
- `data_perdido`: DateField - Quando perdeu
- `local_perdido`: TextField - Descrição do local
- `cidade`: CharField(100) - Cidade onde perdeu
- `estado`: CharField(2) - Estado (UF)
- `latitude`: DecimalField(9, 6, null=True) - Coordenada GPS
- `longitude`: DecimalField(9, 6, null=True) - Coordenada GPS
- `recompensa`: DecimalField(10, 2, null=True) - Valor da recompensa
- `ativo`: BooleanField(default=True) - Ainda está perdido
- `status`: CharField(20) - "perdido", "encontrado"
- `data_encontrado`: DateTimeField(null=True) - Quando foi encontrado
- `encontrado_por`: ForeignKey(Usuario, SET_NULL, null=True) - Quem encontrou

**Métodos:**
- `__str__()`: Retorna "Pet Perdido: {nome} - {cidade}/{estado}"
- `save()`: Validações e geocoding
- `marcar_encontrado(encontrado_por)`: Marca como encontrado

**Relacionamentos:**
- Pertence a um Usuario (dono)
- Possui várias PetPerdidoFoto
- Possui vários ReportePetEncontrado

**Funcionalidades Especiais:**
- **Geolocalização**: Armazena latitude/longitude
- **Matching Automático**: Sistema compara com ReportePetEncontrado (raio 10km)
- **Pin no Mapa**: Exibe marcador vermelho no Leaflet.js

---

### 4.6 PetPerdidoFoto

**Descrição**: Fotos do pet perdido para facilitar identificação

**Atributos:**
- `pet_perdido`: ForeignKey(PetPerdido, CASCADE) - Pet associado
- `foto`: ImageField(upload_to='pets_perdidos/') - Imagem
- `descricao`: TextField(blank=True) - Descrição da foto
- `data_upload`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Foto de {pet_perdido.nome}"

**Validações:**
- Formato: JPG, JPEG, PNG
- Tamanho máximo: 5MB
- Dimensões mínimas: 200x200px

---

### 4.7 ReportePetEncontrado

**Descrição**: Reporte de pet encontrado com matching automático

**Atributos:**
- `pet_perdido`: ForeignKey(PetPerdido, SET_NULL, null=True) - Match sugerido
- `encontrou`: ForeignKey(Usuario, CASCADE) - Quem encontrou
- `descricao`: TextField - Descrição do pet encontrado
- `local_encontrado`: TextField - Onde encontrou
- `cidade`: CharField(100)
- `estado`: CharField(2)
- `latitude`: DecimalField(9, 6) - Coordenada GPS
- `longitude`: DecimalField(9, 6) - Coordenada GPS
- `data_encontrado`: DateTimeField(auto_now_add=True)
- `distancia_km`: DecimalField(5, 2, null=True) - Distância do pet perdido
- `score_similaridade`: DecimalField(5, 2, null=True) - Score 0-100%
- `contato_feito`: BooleanField(default=False) - Dono foi contatado
- `visto`: BooleanField(default=False) - Dono visualizou

**Métodos:**
- `__str__()`: Retorna "Pet Encontrado em {cidade} por {encontrou}"
- `calcular_distancia(pet_perdido)`: Calcula distância em km usando Haversine
- `save()`: Executa matching automático e notifica donos

**Relacionamentos:**
- Associado a um PetPerdido (match)
- Pertence a um Usuario (encontrou)
- Possui várias ReportePetEncontradoFoto

**Algoritmo de Matching:**
1. Busca PetPerdido com `ativo=True` em raio de 10km
2. Compara espécie, porte, sexo
3. Calcula score de similaridade (0-100%)
4. Notifica donos de pets com match > 50%

---

### 4.8 ReportePetEncontradoFoto

**Descrição**: Fotos do pet encontrado

**Atributos:**
- `reporte`: ForeignKey(ReportePetEncontrado, CASCADE)
- `foto`: ImageField(upload_to='pets_encontrados/')
- `descricao`: TextField(blank=True)
- `data_upload`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Foto de Pet Encontrado em {reporte.cidade}"

---

### 4.9 Denuncia

**Descrição**: Denúncia de maus-tratos ou abandono

**Atributos:**
- `denunciante`: ForeignKey(Usuario, SET_NULL, null=True) - Pode ser anônima
- `tipo`: CharField(50) - "maus-tratos", "abandono", "agressao", etc
- `descricao`: TextField - Descrição detalhada
- `endereco`: TextField - Local da ocorrência
- `cidade`: CharField(100)
- `estado`: CharField(2)
- `latitude`: DecimalField(9, 6, null=True)
- `longitude`: DecimalField(9, 6, null=True)
- `protocolo`: CharField(30, unique=True) - Protocolo único
- `anonima`: BooleanField(default=False)
- `status`: CharField(20) - "pendente", "em_analise", "resolvida", "arquivada"
- `data_criacao`: DateTimeField(auto_now_add=True)
- `moderador`: ForeignKey(User, SET_NULL, null=True) - Admin que avaliou
- `data_avaliacao`: DateTimeField(null=True)
- `observacoes_moderador`: TextField(blank=True)
- `categoria`: CharField(50, blank=True)

**Métodos:**
- `__str__()`: Retorna "Denúncia {protocolo} - {status}"
- `gerar_protocolo()`: Gera código único "DEN-AAAAMMDD-NNN"
- `save()`: Gera protocolo automaticamente

**Relacionamentos:**
- Pertence a um Usuario opcional (denunciante)
- Avaliada por um User (moderador)
- Possui várias DenunciaImagem
- Possui vários DenunciaVideo
- Possui vários DenunciaHistorico

**Tipos de Denúncia:**
- `maus-tratos`: Violência física
- `abandono`: Animal abandonado
- `agressao`: Agressão a animal
- `criacao_ilegal`: Criação clandestina
- `outro`: Outros tipos

**Fluxo de Status:**
```
pendente → em_analise → resolvida
                    ↓
                arquivada
```

---

### 4.10 DenunciaImagem

**Descrição**: Evidências fotográficas da denúncia

**Atributos:**
- `denuncia`: ForeignKey(Denuncia, CASCADE)
- `imagem`: ImageField(upload_to='denuncias/')
- `descricao`: TextField(blank=True)
- `data_upload`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Imagem da {denuncia.protocolo}"

---

### 4.11 DenunciaVideo

**Descrição**: Evidências em vídeo da denúncia

**Atributos:**
- `denuncia`: ForeignKey(Denuncia, CASCADE)
- `video`: FileField(upload_to='denuncias/videos/')
- `descricao`: TextField(blank=True)
- `data_upload`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Vídeo da {denuncia.protocolo}"

**Validações:**
- Formato: MP4, AVI, MOV
- Tamanho máximo: 20MB

---

### 4.12 DenunciaHistorico

**Descrição**: Histórico de mudanças de status da denúncia

**Atributos:**
- `denuncia`: ForeignKey(Denuncia, CASCADE)
- `status_anterior`: CharField(20)
- `status_novo`: CharField(20)
- `observacao`: TextField(blank=True)
- `alterado_por`: ForeignKey(User, SET_NULL, null=True)
- `data_alteracao`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Histórico {denuncia.protocolo}: {status_anterior} → {status_novo}"
- `save()`: Cria automaticamente ao mudar status

**Funcionalidade:**
- Rastreabilidade completa de todas mudanças
- Identifica quem fez cada alteração
- Registra observações do moderador

---

### 4.13 Notificacao

**Descrição**: Sistema de notificações para usuários

**Atributos:**
- `usuario`: ForeignKey(Usuario, CASCADE) - Destinatário
- `tipo`: CharField(50) - Tipo da notificação
- `titulo`: CharField(200) - Título curto
- `mensagem`: TextField - Mensagem completa
- `link`: CharField(500, blank=True) - Link para recurso relacionado
- `lida`: BooleanField(default=False) - Foi lida
- `data_criacao`: DateTimeField(auto_now_add=True)
- `data_leitura`: DateTimeField(null=True)

**Métodos:**
- `__str__()`: Retorna "Notificação para {usuario}: {titulo}"
- `marcar_como_lida()`: Marca notificação como lida
- `save()`: Validações

**Tipos de Notificação:**
- `solicitacao_adocao`: Nova solicitação de adoção recebida
- `aprovacao_adocao`: Sua solicitação foi aprovada
- `rejeicao_adocao`: Sua solicitação foi rejeitada
- `pet_match`: Possível match de pet perdido/encontrado
- `denuncia_atualizada`: Status da denúncia mudou
- `contato_resposta`: Sua mensagem de contato foi respondida

**Estrutura do Link:**
```
/animais-adocao/{id}/           → Animal para adoção
/solicitacoes/{id}/             → Solicitação de adoção
/pets-perdidos/{id}/            → Pet perdido
/denuncias/{protocolo}/         → Denúncia
/contatos/{protocolo}/          → Contato
```

---

### 4.14 Contato

**Descrição**: Mensagens de contato com administrador

**Atributos:**
- `nome`: CharField(100) - Nome do remetente
- `email`: EmailField - Email para resposta
- `telefone`: CharField(15, blank=True) - Telefone opcional
- `assunto`: CharField(200) - Assunto da mensagem
- `mensagem`: TextField - Conteúdo
- `protocolo`: CharField(30, unique=True) - Protocolo de acompanhamento
- `data_contato`: DateTimeField(auto_now_add=True)
- `status`: CharField(20) - "pendente", "lida", "respondida"
- `data_leitura`: DateTimeField(null=True)
- `data_resposta`: DateTimeField(null=True)
- `resposta`: TextField(blank=True) - Resposta do admin

**Métodos:**
- `__str__()`: Retorna "Contato {protocolo}: {assunto}"
- `gerar_protocolo()`: Gera código "CONT-AAAAMMDD-NNN"
- `save()`: Gera protocolo automaticamente

**Fluxo de Status:**
```
pendente → lida → respondida
```

---

### 4.15 AnimalFoto

**Descrição**: Fotos adicionais de animais

**Atributos:**
- `animal`: ForeignKey(Animal, CASCADE)
- `imagem`: ImageField(upload_to='animais/')
- `url`: URLField(blank=True) - URL externa opcional
- `descricao`: CharField(200, blank=True)
- `data_upload`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Foto de {animal.nome}"

---

### 4.16 AnimalVideo

**Descrição**: Vídeos de animais

**Atributos:**
- `animal`: ForeignKey(Animal, CASCADE)
- `video`: FileField(upload_to='animais/videos/')
- `url`: URLField(blank=True)
- `descricao`: CharField(200, blank=True)
- `data_upload`: DateTimeField(auto_now_add=True)

**Métodos:**
- `__str__()`: Retorna "Vídeo de {animal.nome}"

---

## 5. Herança e Extensão

### 5.1 Padrão de Extensão com OneToOneField

O sistema utiliza **composição** em vez de herança múltipla do Django:

```python
# Animal é a classe base
class Animal(models.Model):
    dono = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    # ... outros campos

# AnimalParaAdocao estende Animal
class AnimalParaAdocao(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE)
    vacinado = models.BooleanField(default=False)
    # ... campos específicos de adoção
```

**Vantagens:**
- ✅ Flexibilidade: Um Animal pode ou não estar para adoção
- ✅ Separação de responsabilidades
- ✅ Evita problemas de herança múltipla do Django

### 5.2 Extensão do User do Django

```python
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15, blank=True)
    # ... campos extras
```

**Por que não herdar de AbstractUser:**
- ✅ Mantém compatibilidade com sistema de auth do Django
- ✅ Facilita uso de bibliotecas third-party
- ✅ Permite adicionar campos sem modificar User

---

## 6. Enumerações e Choices

### 6.1 Status de SolicitacaoAdocao
```python
STATUS_CHOICES = [
    ('pendente', 'Pendente'),
    ('aprovada', 'Aprovada'),
    ('rejeitada', 'Rejeitada'),
    ('cancelada', 'Cancelada'),
]
```

### 6.2 Espécie de Animal
```python
ESPECIE_CHOICES = [
    ('cachorro', 'Cachorro'),
    ('gato', 'Gato'),
    ('outro', 'Outro'),
]
```

### 6.3 Sexo de Animal
```python
SEXO_CHOICES = [
    ('macho', 'Macho'),
    ('femea', 'Fêmea'),
]
```

### 6.4 Porte de Animal
```python
PORTE_CHOICES = [
    ('pequeno', 'Pequeno'),
    ('medio', 'Médio'),
    ('grande', 'Grande'),
]
```

### 6.5 Status de PetPerdido
```python
STATUS_CHOICES = [
    ('perdido', 'Perdido'),
    ('encontrado', 'Encontrado'),
]
```

### 6.6 Tipo de Denúncia
```python
TIPO_CHOICES = [
    ('maus-tratos', 'Maus-tratos'),
    ('abandono', 'Abandono'),
    ('agressao', 'Agressão'),
    ('criacao_ilegal', 'Criação Ilegal'),
    ('outro', 'Outro'),
]
```

### 6.7 Status de Denúncia
```python
STATUS_CHOICES = [
    ('pendente', 'Pendente'),
    ('em_analise', 'Em Análise'),
    ('resolvida', 'Resolvida'),
    ('arquivada', 'Arquivada'),
]
```

### 6.8 Tipo de Notificação
```python
TIPO_CHOICES = [
    ('solicitacao_adocao', 'Solicitação de Adoção'),
    ('aprovacao_adocao', 'Aprovação de Adoção'),
    ('rejeicao_adocao', 'Rejeição de Adoção'),
    ('pet_match', 'Match de Pet'),
    ('denuncia_atualizada', 'Denúncia Atualizada'),
    ('contato_resposta', 'Resposta de Contato'),
]
```

### 6.9 Status de Contato
```python
STATUS_CHOICES = [
    ('pendente', 'Pendente'),
    ('lida', 'Lida'),
    ('respondida', 'Respondida'),
]
```

---

## 7. Índices e Otimizações

### 7.1 Índices por Classe

**Animal:**
- `db_index=True`: dono, especie, estado, cidade, is_active
- Índice composto: (estado, cidade, especie)

**AnimalParaAdocao:**
- `db_index=True`: adotado, vacinado, castrado

**PetPerdido:**
- `db_index=True`: dono, ativo, status, estado, cidade
- Índice geoespacial: (latitude, longitude)

**Denuncia:**
- `db_index=True`: status, protocolo (unique)
- Índice composto: (estado, cidade, status)

**Notificacao:**
- `db_index=True`: usuario, lida, tipo
- Índice composto: (usuario, lida, data_criacao)

### 7.2 Estratégias de Otimização

**Select Related (ForeignKey/OneToOne):**
```python
# Evita N+1 queries
Animal.objects.select_related('dono', 'dono__user')
AnimalParaAdocao.objects.select_related('animal', 'animal__dono')
```

**Prefetch Related (Many-to-Many/Reverse FK):**
```python
# Carrega fotos de múltiplos pets de uma vez
PetPerdido.objects.prefetch_related('fotos', 'reportes')
```

**Only/Defer:**
```python
# Carrega apenas campos necessários
Animal.objects.only('id', 'nome', 'especie')
```

---

## 8. Validações e Constraints

### 8.1 Validações a Nível de Modelo

**Animal:**
- `clean()`: Valida estado UF, espécie, sexo, porte
- `save()`: Normaliza campos (lowercase estados)

**PetPerdido:**
- `clean()`: Valida latitude/longitude (-90 a 90, -180 a 180)
- `save()`: Verifica data_perdido não pode ser futura

**Denuncia:**
- `clean()`: Protocolo único, status válido
- `save()`: Gera protocolo se não existir

### 8.2 Constraints de Banco de Dados

```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(idade__gte=0),
            name='idade_positiva'
        ),
        models.CheckConstraint(
            check=models.Q(latitude__gte=-90) & models.Q(latitude__lte=90),
            name='latitude_valida'
        ),
        models.UniqueConstraint(
            fields=['protocolo'],
            name='protocolo_unico'
        ),
    ]
```

### 8.3 Validações de Arquivos

**Imagens:**
- Formatos: JPG, JPEG, PNG
- Tamanho máximo: 5MB
- Dimensões mínimas: 200x200px
- Validação MIME real (não apenas extensão)

**Vídeos:**
- Formatos: MP4, AVI, MOV
- Tamanho máximo: 20MB
- Validação MIME real

**Implementação:**
```python
# validators.py
def validate_image_file(file):
    # Valida tamanho
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Arquivo muito grande")
    
    # Valida MIME type
    mime = magic.from_buffer(file.read(2048), mime=True)
    if mime not in ['image/jpeg', 'image/png']:
        raise ValidationError("Formato inválido")
```

---

## 9. Métodos Especiais

### 9.1 Métodos de Protocolo

**Geração de Protocolo Único:**
```python
def gerar_protocolo(prefixo='DEN'):
    """
    Gera protocolo único no formato: PREFIX-AAAAMMDD-NNN
    Exemplo: DEN-20251123-001
    """
    hoje = date.today()
    prefixo_data = f"{prefixo}-{hoje.strftime('%Y%m%d')}"
    
    # Busca último protocolo do dia
    ultimo = Denuncia.objects.filter(
        protocolo__startswith=prefixo_data
    ).order_by('-protocolo').first()
    
    if ultimo:
        # Incrementa contador
        numero = int(ultimo.protocolo.split('-')[-1]) + 1
    else:
        numero = 1
    
    return f"{prefixo_data}-{numero:03d}"
```

### 9.2 Cálculo de Distância (Haversine)

```python
from math import radians, cos, sin, asin, sqrt

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula distância em km entre duas coordenadas GPS
    usando fórmula de Haversine
    """
    # Converte para radianos
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Raio da Terra em km
    r = 6371
    
    return c * r
```

### 9.3 Matching de Pets

```python
def buscar_matches(reporte):
    """
    Busca pets perdidos próximos ao reporte de pet encontrado
    Retorna lista ordenada por score de similaridade
    """
    matches = []
    
    # Busca pets perdidos ativos em raio de 10km
    pets_perdidos = PetPerdido.objects.filter(
        ativo=True,
        estado=reporte.estado
    )
    
    for pet in pets_perdidos:
        if not (pet.latitude and pet.longitude):
            continue
        
        # Calcula distância
        distancia = calcular_distancia(
            pet.latitude, pet.longitude,
            reporte.latitude, reporte.longitude
        )
        
        if distancia > 10:  # Fora do raio
            continue
        
        # Calcula score de similaridade
        score = 0
        if pet.especie == reporte.especie:
            score += 40
        if pet.porte == reporte.porte:
            score += 30
        if pet.sexo == reporte.sexo:
            score += 30
        
        matches.append({
            'pet': pet,
            'distancia_km': round(distancia, 2),
            'score': score
        })
    
    # Ordena por score (maior primeiro)
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return matches
```

---

## 10. Signals (Sinais do Django)

### 10.1 Criação Automática de Usuario

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def criar_usuario(sender, instance, created, **kwargs):
    """Cria Usuario automaticamente quando User é criado"""
    if created:
        Usuario.objects.create(user=instance)
```

### 10.2 Notificações Automáticas

```python
@receiver(post_save, sender=SolicitacaoAdocao)
def notificar_solicitacao(sender, instance, created, **kwargs):
    """Notifica dono quando há nova solicitação"""
    if created:
        Notificacao.objects.create(
            usuario=instance.animal.animal.dono,
            tipo='solicitacao_adocao',
            titulo='Nova Solicitação de Adoção',
            mensagem=f'{instance.solicitante.user.username} solicitou adotar {instance.animal.animal.nome}',
            link=f'/solicitacoes/{instance.id}/'
        )
```

### 10.3 Histórico de Denúncia

```python
@receiver(pre_save, sender=Denuncia)
def registrar_mudanca_status(sender, instance, **kwargs):
    """Cria histórico quando status muda"""
    if instance.pk:  # Já existe
        old = Denuncia.objects.get(pk=instance.pk)
        if old.status != instance.status:
            DenunciaHistorico.objects.create(
                denuncia=instance,
                status_anterior=old.status,
                status_novo=instance.status,
                alterado_por=instance.moderador
            )
```

---

## 11. Permissões e Controle de Acesso

### 11.1 Permissões por Modelo

**Animal:**
- `add_animal`: Qualquer usuário autenticado
- `change_animal`: Apenas dono
- `delete_animal`: Apenas dono
- `view_animal`: Público

**Denuncia:**
- `add_denuncia`: Qualquer um (inclusive anônimo)
- `change_denuncia`: Apenas staff (moderadores)
- `delete_denuncia`: Apenas superuser
- `view_denuncia`: Denunciante ou staff

**SolicitacaoAdocao:**
- `add_solicitacaoadocao`: Usuário autenticado
- `change_solicitacaoadocao`: Dono do animal (aprovar/rejeitar)
- `delete_solicitacaoadocao`: Solicitante (cancelar)

### 11.2 Regras de Negócio

**Adoção:**
- Usuário não pode solicitar próprio animal
- Apenas uma solicitação ativa por usuário por animal
- Dono pode aprovar apenas uma solicitação

**Pet Perdido:**
- Apenas dono pode editar/excluir
- Qualquer usuário pode reportar pet encontrado
- Dono recebe notificação de todos matches

**Denúncia:**
- Pode ser anônima
- Apenas staff pode moderar
- Histórico é imutável

---

## 12. Tabela Resumo das Classes

| Classe | Tipo | Relacionamentos | Principais Métodos |
|--------|------|----------------|-------------------|
| **Usuario** | Entidade | User (1:1) | `__str__()`, `save()` |
| **Animal** | Entidade Base | Usuario (N:1), AnimalParaAdocao (1:1) | `__str__()`, `save()` |
| **AnimalParaAdocao** | Extensão | Animal (1:1), SolicitacaoAdocao (1:N) | `__str__()`, `save()` |
| **SolicitacaoAdocao** | Transação | AnimalParaAdocao (N:1), Usuario (N:1) | `__str__()`, `aprovar()`, `rejeitar()` |
| **PetPerdido** | Entidade | Usuario (N:1), PetPerdidoFoto (1:N) | `__str__()`, `marcar_encontrado()` |
| **PetPerdidoFoto** | Mídia | PetPerdido (N:1) | `__str__()` |
| **ReportePetEncontrado** | Transação | PetPerdido (N:1), Usuario (N:1) | `__str__()`, `calcular_distancia()` |
| **ReportePetEncontradoFoto** | Mídia | ReportePetEncontrado (N:1) | `__str__()` |
| **Denuncia** | Entidade | Usuario (N:1), DenunciaHistorico (1:N) | `__str__()`, `gerar_protocolo()` |
| **DenunciaImagem** | Mídia | Denuncia (N:1) | `__str__()` |
| **DenunciaVideo** | Mídia | Denuncia (N:1) | `__str__()` |
| **DenunciaHistorico** | Auditoria | Denuncia (N:1), User (N:1) | `__str__()`, `save()` |
| **Notificacao** | Sistema | Usuario (N:1) | `__str__()`, `marcar_como_lida()` |
| **Contato** | Comunicação | - | `__str__()`, `gerar_protocolo()` |
| **AnimalFoto** | Mídia | Animal (N:1) | `__str__()` |
| **AnimalVideo** | Mídia | Animal (N:1) | `__str__()` |

---

## 13. Glossário

**OneToOneField**: Relacionamento 1:1 - Uma instância se relaciona com exatamente uma instância de outro modelo.

**ForeignKey**: Relacionamento N:1 - Várias instâncias podem se relacionar com uma instância de outro modelo.

**CASCADE**: Ao deletar pai, deleta todos filhos relacionados.

**SET_NULL**: Ao deletar pai, seta campo relacionado como NULL (requer `null=True`).

**PROTECT**: Impede deleção de pai se houver filhos relacionados.

**DecimalField**: Campo numérico de precisão fixa (ideal para coordenadas GPS e valores monetários).

**ImageField**: Campo para upload de imagens (requer Pillow).

**FileField**: Campo para upload de arquivos genéricos.

**auto_now_add**: Define data/hora automaticamente na criação.

**auto_now**: Atualiza data/hora automaticamente a cada save.

**blank=True**: Campo pode ser vazio no formulário (validação).

**null=True**: Campo pode ser NULL no banco de dados.

**unique=True**: Valor deve ser único em toda tabela.

**db_index=True**: Cria índice no banco para buscas rápidas.

**Haversine**: Fórmula para calcular distância entre coordenadas GPS considerando curvatura da Terra.

**Geolocalização**: Armazenamento e busca baseada em coordenadas geográficas (latitude/longitude).

**Matching**: Algoritmo que compara pets perdidos com reportes de pets encontrados.

**Signal**: Mecanismo do Django para executar código automaticamente quando certos eventos ocorrem.

**Prefetch**: Otimização que carrega relacionamentos em queries separadas (evita N+1).

**Select Related**: Otimização que carrega relacionamentos com JOIN SQL.

**Protocolo**: Código único de rastreamento (formato: PREFIX-AAAAMMDD-NNN).

**MIME Type**: Tipo de arquivo real (verificado por conteúdo, não extensão).

---

**Versão**: 1.0  
**Última Atualização**: 23/11/2025  
**Autor**: Daniel
**Projeto**: TCC - S.O.S Pets

---

## Observações Finais

Este diagrama representa o modelo de dados completo do sistema S.O.S Pets em 23/11/2025. O modelo utiliza:

- **19 classes principais** organizadas em 6 módulos funcionais
- **Relacionamentos complexos** com ForeignKey e OneToOneField
- **Geolocalização** com latitude/longitude e algoritmo de matching
- **Sistema de protocolos** únicos para rastreamento
- **Validações robustas** em múltiplas camadas
- **Otimizações** com índices e select_related/prefetch_related
- **Auditoria completa** com históricos e timestamps

O design prioriza **separação de responsabilidades**, **escalabilidade** e **integridade referencial**, seguindo as melhores práticas do Django e padrões de mercado.
