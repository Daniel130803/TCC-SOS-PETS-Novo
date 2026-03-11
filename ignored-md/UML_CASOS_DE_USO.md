# Diagramas UML - Casos de Uso
## S.O.S Pets

---

## 1. Diagrama Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         S.O.S PETS - CASOS DE USO                            │
└─────────────────────────────────────────────────────────────────────────────┘

        Visitante                 Usuário                 Doador               Admin
            │                       │                       │                   │
            │                       │                       │                   │
    ┌───────┴───────┐      ┌────────┴────────┐     ┌──────┴──────┐    ┌──────┴──────┐
    │               │      │                 │     │             │    │             │
    ▼               ▼      ▼                 ▼     ▼             ▼    ▼             ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  UC01: Visualizar Animais          UC06: Cadastrar Animal                   │
│  UC02: Buscar/Filtrar              UC07: Gerenciar Meus Pets                │
│  UC03: Ver Detalhes                UC08: Solicitar Adoção                    │
│  UC04: Registrar-se                UC09: Avaliar Solicitações                │
│  UC05: Fazer Login                 UC10: Reportar Pet Perdido                │
│                                    UC11: Reportar Pet Encontrado             │
│  UC12: Fazer Denúncia              UC13: Acompanhar Denúncia                │
│  UC14: Entrar em Contato           UC15: Receber Notificações               │
│  UC16: Realizar Doação             UC17: Visualizar Histórias               │
│  UC18: Moderar Conteúdo            UC19: Gerenciar Denúncias                │
│  UC20: Aprovar Adoções             UC21: Gerenciar Usuários                 │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Módulo de Adoção

### Diagrama de Casos de Uso

```
┌────────────────────────────────────────────────────────────────────────┐
│                      MÓDULO DE ADOÇÃO                                  │
└────────────────────────────────────────────────────────────────────────┘

    Visitante                                  Usuário (Adotante)
        │                                            │
        │                                            │
        │                                            │
        │   ┌──────────────────────────┐            │
        ├──►│ UC01: Visualizar         │            │
        │   │ Animais Disponíveis      │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        ├──►│ UC02: Buscar e Filtrar   │◄───────────┤
        │   │ Animais                  │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        ├──►│ UC03: Ver Detalhes       │◄───────────┤
        │   │ do Animal                │            │
        │   └──────────────────────────┘            │
        │                                            │
        │                               ┌────────────────────────────┐
        │                               │ UC08: Solicitar Adoção     │◄────┐
        │                               └────────────────────────────┘     │
        │                                            │                     │
        │                                            │ <<extend>>          │
        │                                            ▼                     │
        │                               ┌────────────────────────────┐    │
        │                               │ Preencher Formulário       │    │
        │                               │ de Adotante                │    │
        │                               └────────────────────────────┘    │
        │                                            │                     │
        │                                            │ <<include>>         │
        │                                            ▼                     │
        │                               ┌────────────────────────────┐    │
        │                               │ Enviar Mensagem            │    │
        │                               │ ao Doador                  │    │
        │                               └────────────────────────────┘    │
        │                                                                  │
                                                                           │
    Usuário (Doador de Pet)                                              │
        │                                                                  │
        │   ┌──────────────────────────┐                                 │
        ├──►│ UC06: Cadastrar Animal   │                                 │
        │   │ para Adoção              │                                 │
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<include>>                                        │
        │            ▼                                                     │
        │   ┌──────────────────────────┐                                 │
        │   │ Upload de Fotos          │                                 │
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<include>>                                        │
        │            ▼                                                     │
        │   ┌──────────────────────────┐                                 │
        │   │ Definir Localização      │                                 │
        │   └──────────────────────────┘                                 │
        │                                                                  │
        │   ┌──────────────────────────┐                                 │
        ├──►│ UC07: Gerenciar          │                                 │
        │   │ Meus Pets                │                                 │
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<extend>>                                         │
        │            ├────────────────┐                                   │
        │            ▼                ▼                                   │
        │   ┌─────────────┐  ┌─────────────┐                            │
        │   │   Editar    │  │   Excluir   │                            │
        │   │   Animal    │  │   Animal    │                            │
        │   └─────────────┘  └─────────────┘                            │
        │                                                                  │
        │   ┌──────────────────────────┐                                 │
        ├──►│ UC09: Avaliar            │                                 │
        │   │ Solicitações de Adoção   │─────────────────────────────────┤
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<extend>>                                         │
        │            ├────────────────┬──────────────────┐               │
        │            ▼                ▼                  ▼               │
        │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
        │   │  Aprovar    │  │  Rejeitar   │  │  Visualizar │          │
        │   │ Solicitação │  │ Solicitação │  │   Perfil    │          │
        │   └─────────────┘  └─────────────┘  └─────────────┘          │
        │            │                │                                   │
        │            │                │                                   │
        │            └────────────────┴─────────────────────────┐        │
        │                                                        ▼        │
        │                                           ┌────────────────────┐│
        │                                           │ UC15: Receber      ││
        │                                           │ Notificações       ││
        │                                           └────────────────────┘│
```

### UC01: Visualizar Animais Disponíveis

**Ator Principal**: Visitante, Usuário

**Pré-condições**: Nenhuma

**Fluxo Principal**:
1. O ator acessa a página de adoção
2. O sistema exibe a galeria de animais disponíveis
3. O sistema mostra informações resumidas (foto, nome, espécie, idade, localização)
4. O ator pode visualizar os animais em cards organizados

**Pós-condições**: Galeria de animais exibida

**Fluxos Alternativos**:
- **FA01**: Nenhum animal disponível
  - O sistema exibe mensagem "Nenhum animal disponível no momento"

---

### UC02: Buscar e Filtrar Animais

**Ator Principal**: Visitante, Usuário

**Pré-condições**: UC01 executado

**Fluxo Principal**:
1. O ator seleciona filtros desejados (espécie, porte, sexo, estado, cidade)
2. O sistema aplica os filtros
3. O sistema exibe apenas animais que atendem aos critérios
4. O ator pode limpar filtros para ver todos os animais

**Pós-condições**: Lista de animais filtrada

**Fluxos Alternativos**:
- **FA01**: Nenhum resultado encontrado
  - O sistema exibe mensagem "Nenhum animal encontrado com estes critérios"
  - O sistema sugere remover alguns filtros

---

### UC03: Ver Detalhes do Animal

**Ator Principal**: Visitante, Usuário

**Pré-condições**: UC01 ou UC02 executado

**Fluxo Principal**:
1. O ator clica em um animal da galeria
2. O sistema abre modal/página com detalhes completos
3. O sistema exibe: fotos, nome, espécie, raça, idade, porte, peso, características, histórico de saúde, personalidade, localização, informações do doador
4. Se usuário logado, o sistema exibe botão "Solicitar Adoção"

**Pós-condições**: Detalhes do animal exibidos

---

### UC06: Cadastrar Animal para Adoção

**Ator Principal**: Usuário (Doador)

**Pré-condições**: Usuário autenticado

**Fluxo Principal**:
1. O usuário acessa "Cadastrar Pet para Adoção"
2. O sistema exibe formulário
3. O usuário preenche dados obrigatórios (nome, espécie, idade, porte, sexo, descrição)
4. O usuário adiciona foto principal
5. O usuário pode adicionar fotos adicionais
6. O usuário informa localização (estado, cidade, bairro)
7. O usuário marca características especiais (vacinado, castrado, etc)
8. O usuário submete o formulário
9. O sistema valida os dados
10. O sistema salva o animal
11. O sistema exibe mensagem de sucesso

**Pós-condições**: Animal cadastrado e disponível para adoção

**Fluxos Alternativos**:
- **FA01**: Dados inválidos
  - O sistema exibe mensagens de erro nos campos
  - O usuário corrige e reenvia

- **FA02**: Usuário não autenticado
  - O sistema redireciona para login
  - Após login, retorna ao formulário

---

### UC07: Gerenciar Meus Pets

**Ator Principal**: Usuário (Doador)

**Pré-condições**: Usuário autenticado e possui pets cadastrados

**Fluxo Principal**:
1. O usuário acessa "Meus Pets Cadastrados"
2. O sistema lista todos os pets do usuário
3. O sistema exibe status de cada pet (disponível, em negociação, adotado)
4. O usuário pode editar ou excluir um pet
5. O sistema exibe quantidade de solicitações recebidas por pet

**Pós-condições**: Lista de pets do usuário exibida

**Extensões**:
- **E01**: Editar Animal
  - O usuário clica em "Editar"
  - O sistema carrega formulário preenchido
  - O usuário altera informações
  - O sistema salva alterações

- **E02**: Excluir Animal
  - O usuário clica em "Excluir"
  - O sistema solicita confirmação
  - O usuário confirma
  - O sistema remove o animal (ou marca como inativo)

---

### UC08: Solicitar Adoção

**Ator Principal**: Usuário (Adotante)

**Pré-condições**: 
- Usuário autenticado
- UC03 executado

**Fluxo Principal**:
1. O usuário visualiza detalhes de um animal
2. O usuário clica em "Solicitar Adoção"
3. O sistema exibe formulário de solicitação
4. O usuário preenche mensagem para o doador
5. O usuário submete a solicitação
6. O sistema valida os dados
7. O sistema cria a solicitação
8. O sistema envia notificação ao doador
9. O sistema exibe mensagem de confirmação

**Pós-condições**: 
- Solicitação criada com status "Pendente"
- Doador notificado

**Fluxos Alternativos**:
- **FA01**: Usuário já tem solicitação pendente para este animal
  - O sistema exibe mensagem informando
  - O sistema não permite nova solicitação

---

### UC09: Avaliar Solicitações de Adoção

**Ator Principal**: Usuário (Doador)

**Pré-condições**: 
- Usuário autenticado
- Possui pets com solicitações

**Fluxo Principal**:
1. O usuário acessa "Solicitações Recebidas"
2. O sistema lista todas as solicitações pendentes
3. O usuário visualiza detalhes do solicitante
4. O usuário pode aprovar ou rejeitar
5. O usuário escreve uma resposta (opcional)
6. O sistema atualiza status da solicitação
7. O sistema notifica o adotante
8. Se aprovado, o sistema marca animal como "Em negociação"

**Pós-condições**: 
- Status da solicitação atualizado
- Adotante notificado

**Extensões**:
- **E01**: Visualizar Perfil do Solicitante
  - O usuário clica em "Ver Perfil"
  - O sistema exibe informações públicas do solicitante

---

## 3. Módulo de Pets Perdidos

### Diagrama de Casos de Uso

```
┌────────────────────────────────────────────────────────────────────────┐
│                    MÓDULO DE PETS PERDIDOS                             │
└────────────────────────────────────────────────────────────────────────┘

    Visitante                                  Usuário (Dono)
        │                                            │
        │   ┌──────────────────────────┐            │
        ├──►│ Visualizar Mapa          │◄───────────┤
        │   │ de Pets Perdidos         │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Filtrar por Localização  │            │
        │   │ e Características        │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        ├──►│ Ver Detalhes             │◄───────────┤
        │   │ do Pet Perdido           │            │
        │   └──────────────────────────┘            │
        │                                            │
        │                               ┌────────────────────────────┐
        │                               │ UC10: Reportar             │
        │                               │ Pet Perdido                │◄────┐
        │                               └────────────────────────────┘     │
        │                                            │                     │
        │                                            │ <<include>>         │
        │                                            ▼                     │
        │                               ┌────────────────────────────┐    │
        │                               │ Selecionar Localização     │    │
        │                               │ no Mapa (Leaflet)          │    │
        │                               └────────────────────────────┘    │
        │                                            │                     │
        │                                            │ <<include>>         │
        │                                            ▼                     │
        │                               ┌────────────────────────────┐    │
        │                               │ Upload de Múltiplas        │    │
        │                               │ Fotos                      │    │
        │                               └────────────────────────────┘    │
        │                                            │                     │
        │                                            │ <<extend>>          │
        │                                            ▼                     │
        │                               ┌────────────────────────────┐    │
        │                               │ Oferecer Recompensa        │    │
        │                               └────────────────────────────┘    │
        │                                                                  │
        │                                                                  │
    Usuário (Encontrou)                                                   │
        │                                                                  │
        │   ┌──────────────────────────┐                                 │
        ├──►│ UC11: Reportar           │                                 │
        │   │ Pet Encontrado           │─────────────────────────────────┤
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<include>>                                        │
        │            ▼                                                     │
        │   ┌──────────────────────────┐                                 │
        │   │ Sistema Faz Matching     │                                 │
        │   │ Automático               │                                 │
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<extend>>                                         │
        │            ▼                                                     │
        │   ┌──────────────────────────┐                                 │
        │   │ Notificar Possíveis      │                                 │
        │   │ Donos                    │                                 │
        │   └──────────────────────────┘                                 │
        │                                                                  │
    Usuário (Dono)                                                        │
        │                                                                  │
        │   ┌──────────────────────────┐                                 │
        ├──►│ Gerenciar Meus           │                                 │
        │   │ Pets Perdidos            │                                 │
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<extend>>                                         │
        │            ├────────────────┐                                   │
        │            ▼                ▼                                   │
        │   ┌─────────────┐  ┌─────────────┐                            │
        │   │  Atualizar  │  │   Marcar    │                            │
        │   │ Informações │  │    Como     │                            │
        │   │             │  │ Encontrado  │                            │
        │   └─────────────┘  └─────────────┘                            │
        │                                                                  │
        │   ┌──────────────────────────┐                                 │
        ├──►│ Visualizar Matches       │                                 │
        │   │ de Pets Encontrados      │─────────────────────────────────┤
        │   └──────────────────────────┘                                 │
        │            │                                                     │
        │            │ <<extend>>                                         │
        │            ▼                                                     │
        │   ┌──────────────────────────┐                                 │
        │   │ Entrar em Contato        │                                 │
        │   │ com Quem Encontrou       │                                 │
        │   └──────────────────────────┘                                 │
```

### UC10: Reportar Pet Perdido

**Ator Principal**: Usuário (Dono)

**Pré-condições**: Usuário autenticado

**Fluxo Principal**:
1. O usuário acessa página "Animais Perdidos"
2. O usuário clica em "Perdi meu Pet"
3. O sistema exibe modal com formulário
4. O usuário preenche dados do pet (nome, espécie, raça, cor, porte, sexo, idade)
5. O usuário adiciona características distintivas
6. O usuário descreve circunstâncias da perda
7. O usuário informa data e hora da perda
8. O usuário clica em "Mostrar Mapa"
9. O sistema exibe mini-mapa com Leaflet.js
10. O usuário clica no mapa para marcar localização exata
11. O sistema captura latitude e longitude
12. O usuário faz upload de foto principal
13. O usuário pode adicionar fotos adicionais
14. O usuário informa dados de contato (telefone, WhatsApp, email)
15. O usuário pode marcar "Oferece recompensa" e informar valor
16. O usuário submete o formulário
17. O sistema valida os dados
18. O sistema salva o pet perdido com status "perdido" e ativo=true
19. O sistema adiciona pin vermelho no mapa principal
20. O sistema exibe mensagem de sucesso

**Pós-condições**: 
- Pet perdido registrado
- Pin vermelho aparece no mapa
- Sistema inicia busca automática de matches

**Fluxos Alternativos**:
- **FA01**: Dados obrigatórios faltando
  - O sistema destaca campos obrigatórios
  - O usuário completa e reenvia

- **FA02**: Localização não selecionada
  - O sistema exibe aviso "Clique no mapa para marcar onde perdeu o pet"

---

### UC11: Reportar Pet Encontrado

**Ator Principal**: Usuário (Encontrou)

**Pré-condições**: Nenhuma (pode ser anônimo ou autenticado)

**Fluxo Principal**:
1. O usuário acessa página "Animais Perdidos"
2. O usuário clica em "Encontrei um Pet"
3. O sistema exibe modal com formulário
4. O usuário descreve o pet encontrado
5. O usuário seleciona características (espécie, cor, porte, sexo)
6. O usuário informa data e hora que encontrou
7. O usuário marca no mapa onde encontrou
8. O sistema captura coordenadas
9. O usuário faz upload de foto
10. O usuário informa contato
11. O usuário submete
12. O sistema valida
13. O sistema salva reporte com status "encontrado"
14. **O sistema executa algoritmo de matching automático**:
    - Busca pets perdidos em raio de 10km
    - Compara características (espécie, cor, porte, sexo)
    - Calcula score de similaridade
    - Ordena por score
15. O sistema notifica donos de pets com alta similaridade
16. O sistema adiciona pin verde no mapa
17. O sistema exibe mensagem de sucesso

**Pós-condições**: 
- Reporte de pet encontrado salvo
- Possíveis donos notificados
- Pin verde no mapa

---

### Visualizar Matches de Pets Encontrados

**Ator Principal**: Usuário (Dono)

**Pré-condições**: 
- Usuário autenticado
- Possui pet perdido registrado

**Fluxo Principal**:
1. O usuário recebe notificação de possível match
2. O usuário acessa "Meus Pets Perdidos"
3. O sistema lista seus pets perdidos
4. O sistema exibe badge com número de matches
5. O usuário clica em "Ver Matches"
6. O sistema lista pets encontrados similares
7. O sistema exibe para cada match:
   - Foto do pet encontrado
   - Score de similaridade (%)
   - Distância em km
   - Características
   - Data/hora encontrado
   - Localização
8. O usuário pode clicar em "Ver Contato"
9. O sistema exibe telefone e email de quem encontrou
10. O usuário entra em contato

**Pós-condições**: Usuário visualizou matches e obteve contato

---

### Marcar Pet como Encontrado

**Ator Principal**: Usuário (Dono)

**Pré-condições**: 
- Usuário autenticado
- Possui pet perdido registrado
- Pet foi reencontrado

**Fluxo Principal**:
1. O usuário acessa "Meus Pets Perdidos"
2. O usuário clica em "Marcar como Encontrado"
3. O sistema solicita confirmação
4. O usuário confirma
5. O sistema atualiza status para "encontrado"
6. O sistema marca ativo=false
7. O sistema remove pin do mapa
8. O sistema exibe mensagem de parabéns

**Pós-condições**: 
- Pet marcado como encontrado
- Pin removido do mapa
- Registro mantido para histórico

---

## 4. Módulo de Denúncias

### Diagrama de Casos de Uso

```
┌────────────────────────────────────────────────────────────────────────┐
│                      MÓDULO DE DENÚNCIAS                               │
└────────────────────────────────────────────────────────────────────────┘

    Visitante/Usuário                              Admin
        │                                            │
        │   ┌──────────────────────────┐            │
        ├──►│ UC12: Fazer Denúncia     │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<extend>>                    │
        │            ├───────────────┐               │
        │            ▼               ▼               │
        │   ┌─────────────┐  ┌─────────────┐        │
        │   │  Anônima    │  │   Nominada  │        │
        │   └─────────────┘  └─────────────┘        │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Upload de Evidências     │            │
        │   │ (Fotos/Vídeos)           │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Sistema Gera Protocolo   │            │
        │   └──────────────────────────┘            │
        │                                            │
        │   ┌──────────────────────────┐            │
        ├──►│ UC13: Acompanhar         │            │
        │   │ Denúncia                 │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Buscar por Protocolo     │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Ver Histórico de         │            │
        │   │ Atualizações             │            │
        │   └──────────────────────────┘            │
        │                                            │
        │                               ┌────────────────────────────┐
        │                               │ UC19: Gerenciar            │
        │                               │ Denúncias                  │
        │                               └────────────────────────────┘
        │                                            │
        │                                            │ <<extend>>
        │                                            ├───────────────┐
        │                                            ▼               ▼
        │                               ┌─────────────┐  ┌─────────────┐
        │                               │  Avaliar    │  │  Atualizar  │
        │                               │  Denúncia   │  │   Status    │
        │                               └─────────────┘  └─────────────┘
        │                                            │               │
        │                                            │ <<extend>>    │
        │                                            ▼               │
        │                               ┌────────────────────────────┴┐
        │                               │ Adicionar Observações       │
        │                               │ e Ações Tomadas             │
        │                               └─────────────────────────────┘
```

### UC12: Fazer Denúncia

**Ator Principal**: Visitante, Usuário

**Pré-condições**: Nenhuma

**Fluxo Principal**:
1. O ator acessa página "Denúncia"
2. O sistema exibe formulário
3. O ator seleciona tipo de denúncia (maus-tratos, abandono, agressão, criação ilegal, outros)
4. O ator seleciona categoria específica
5. O ator descreve detalhadamente a situação
6. O ator informa endereço da ocorrência (rua, bairro, cidade, estado)
7. O ator informa data e hora da ocorrência
8. O ator pode fazer upload de fotos (até 5)
9. O ator pode fazer upload de vídeos (até 2)
10. O ator escolhe se quer denúncia anônima ou nominada
11. Se nominada, o ator preenche nome, email, telefone
12. O ator submete o formulário
13. O sistema valida os dados
14. O sistema salva a denúncia
15. **O sistema gera protocolo único** (ex: DEN-20251123-001)
16. O sistema exibe protocolo ao usuário
17. O sistema envia email de confirmação (se não anônima)

**Pós-condições**: 
- Denúncia registrada com status "Pendente"
- Protocolo gerado
- Admin notificado

**Fluxos Alternativos**:
- **FA01**: Denúncia Anônima
  - O usuário marca "Denúncia Anônima"
  - O sistema não solicita dados pessoais
  - O sistema permite apenas acompanhamento por protocolo

- **FA02**: Evidências muito grandes
  - O sistema valida tamanho dos arquivos
  - O sistema exibe mensagem de erro
  - O usuário reduz qualidade ou remove arquivos

---

### UC13: Acompanhar Denúncia

**Ator Principal**: Visitante, Usuário

**Pré-condições**: Possui protocolo de denúncia

**Fluxo Principal**:
1. O ator acessa "Acompanhar Denúncia"
2. O sistema exibe campo para protocolo
3. O ator insere o protocolo
4. O sistema busca a denúncia
5. O sistema exibe status atual
6. O sistema exibe histórico de atualizações:
   - Data/hora
   - Status anterior → novo status
   - Observações do moderador (se houver)
7. O ator pode ver timeline completa

**Pós-condições**: Status da denúncia visualizado

**Fluxos Alternativos**:
- **FA01**: Protocolo inválido
  - O sistema exibe "Protocolo não encontrado"
  - O sistema sugere verificar o número

---

### UC19: Gerenciar Denúncias (Admin)

**Ator Principal**: Admin

**Pré-condições**: Admin autenticado

**Fluxo Principal**:
1. O admin acessa painel de denúncias
2. O sistema lista todas as denúncias
3. O sistema permite filtrar por:
   - Status (pendente, em análise, resolvida, arquivada)
   - Tipo
   - Data
   - Localização
4. O admin clica em uma denúncia
5. O sistema exibe detalhes completos
6. O admin visualiza evidências (fotos, vídeos)
7. O admin pode:
   - Alterar status
   - Adicionar observações
   - Registrar ações tomadas
   - Arquivar denúncia
8. O sistema salva alterações
9. O sistema registra no histórico
10. Se mudança de status, o sistema notifica denunciante (se não anônima)

**Pós-condições**: 
- Denúncia atualizada
- Histórico registrado
- Denunciante notificado (se aplicável)

---

## 5. Módulo de Comunicação

### Diagrama de Casos de Uso

```
┌────────────────────────────────────────────────────────────────────────┐
│                    MÓDULO DE COMUNICAÇÃO                               │
└────────────────────────────────────────────────────────────────────────┘

    Visitante/Usuário                              Admin
        │                                            │
        │   ┌──────────────────────────┐            │
        ├──►│ UC14: Entrar em Contato  │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Selecionar Assunto       │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Escrever Mensagem        │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Sistema Gera Protocolo   │            │
        │   └──────────────────────────┘            │
        │                                            │
    Usuário                                          │
        │                                            │
        │   ┌──────────────────────────┐            │
        ├──►│ UC15: Receber            │◄───────────┤
        │   │ Notificações             │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<extend>>                    │
        │            ├────────────────┬──────────────┤
        │            ▼                ▼              ▼
        │   ┌─────────────┐  ┌─────────────┐  ┌──────────┐
        │   │ Solicitação │  │ Aprovação/  │  │  Match   │
        │   │  de Adoção  │  │  Rejeição   │  │Pet Perdido│
        │   └─────────────┘  └─────────────┘  └──────────┘
        │            │                ▼              │
        │            ├────────────────┴──────────────┤
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Marcar como Lida         │            │
        │   └──────────────────────────┘            │
        │            │                               │
        │            │ <<include>>                   │
        │            ▼                               │
        │   ┌──────────────────────────┐            │
        │   │ Acessar Link/Recurso     │            │
        │   └──────────────────────────┘            │
```

### UC14: Entrar em Contato

**Ator Principal**: Visitante, Usuário

**Pré-condições**: Nenhuma

**Fluxo Principal**:
1. O ator acessa página "Contato"
2. O sistema exibe formulário
3. O ator preenche nome, email, telefone
4. O ator seleciona assunto (Dúvida, Sugestão, Problema, Parceria, Outro)
5. O ator escreve mensagem
6. O ator submete
7. O sistema valida dados
8. O sistema salva contato
9. O sistema gera protocolo (CONT-AAAAMMDD-NNN)
10. O sistema exibe mensagem de sucesso com protocolo
11. O sistema envia email de confirmação
12. O sistema notifica admin

**Pós-condições**: 
- Mensagem enviada
- Protocolo gerado
- Admin notificado

---

### UC15: Receber Notificações

**Ator Principal**: Usuário

**Pré-condições**: Usuário autenticado

**Fluxo Principal**:
1. O sistema detecta evento que gera notificação:
   - Nova solicitação de adoção
   - Solicitação aprovada/rejeitada
   - Match de pet perdido
   - Resposta de denúncia
2. O sistema cria notificação no banco
3. O sistema exibe badge com contador no ícone de sino
4. O usuário clica no ícone de notificações
5. O sistema abre dropdown com lista
6. O sistema exibe últimas 5 notificações não lidas
7. O usuário clica em uma notificação
8. O sistema marca como lida
9. O sistema redireciona para o recurso relacionado

**Pós-condições**: 
- Notificação visualizada
- Marcada como lida
- Usuário direcionado ao recurso

**Tipos de Notificação**:
- **Solicitação de Adoção**: "João Silva enviou solicitação para adotar Rex"
- **Aprovação**: "Sua solicitação para adotar Mel foi aprovada!"
- **Rejeição**: "Sua solicitação para adotar Thor foi rejeitada"
- **Match Pet Perdido**: "Encontramos 2 possíveis matches para Atena!"
- **Denúncia Atualizada**: "Sua denúncia DEN-20251120-001 foi atualizada"

---

## 6. Módulo Administrativo

### Diagrama de Casos de Uso

```
┌────────────────────────────────────────────────────────────────────────┐
│                     MÓDULO ADMINISTRATIVO                              │
└────────────────────────────────────────────────────────────────────────┘

    Admin
      │
      │   ┌──────────────────────────┐
      ├──►│ UC18: Moderar Conteúdo   │
      │   └──────────────────────────┘
      │            │
      │            │ <<extend>>
      │            ├────────────────┬──────────────────┐
      │            ▼                ▼                  ▼
      │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
      │   │  Aprovar/   │  │   Editar    │  │   Remover   │
      │   │ Reprovar    │  │  Conteúdo   │  │  Conteúdo   │
      │   │   Animal    │  │ Inadequado  │  │ Inapropriado│
      │   └─────────────┘  └─────────────┘  └─────────────┘
      │
      │   ┌──────────────────────────┐
      ├──►│ UC19: Gerenciar          │
      │   │ Denúncias                │ (já descrito acima)
      │   └──────────────────────────┘
      │
      │   ┌──────────────────────────┐
      ├──►│ UC20: Aprovar Adoções    │
      │   │ (Validação Final)        │
      │   └──────────────────────────┘
      │            │
      │            │ <<include>>
      │            ▼
      │   ┌──────────────────────────┐
      │   │ Marcar Animal como       │
      │   │ Adotado Oficialmente     │
      │   └──────────────────────────┘
      │
      │   ┌──────────────────────────┐
      ├──►│ UC21: Gerenciar Usuários │
      │   └──────────────────────────┘
      │            │
      │            │ <<extend>>
      │            ├────────────────┬──────────────────┐
      │            ▼                ▼                  ▼
      │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
      │   │  Visualizar │  │   Bloquear  │  │ Desbloquear │
      │   │   Perfis    │  │   Usuário   │  │   Usuário   │
      │   └─────────────┘  └─────────────┘  └─────────────┘
      │
      │   ┌──────────────────────────┐
      ├──►│ Visualizar Dashboard     │
      │   │ com Estatísticas         │
      │   └──────────────────────────┘
      │            │
      │            │ <<include>>
      │            ▼
      │   ┌──────────────────────────┐
      │   │ - Total de Adoções       │
      │   │ - Pets Perdidos Ativos   │
      │   │ - Denúncias Pendentes    │
      │   │ - Novos Usuários         │
      │   └──────────────────────────┘
```

---

## 7. Resumo de Atores e Responsabilidades

| Ator | Descrição | Principais Casos de Uso |
|------|-----------|-------------------------|
| **Visitante** | Usuário não autenticado | UC01, UC02, UC03, UC12, UC14 |
| **Usuário** | Usuário autenticado | UC04, UC05, UC08, UC10, UC11, UC13, UC15 |
| **Doador de Pet** | Usuário que cadastra pets | UC06, UC07, UC09 |
| **Adotante** | Usuário que solicita adoção | UC08 |
| **Dono (Pet Perdido)** | Usuário que perdeu pet | UC10, Visualizar Matches |
| **Encontrou Pet** | Usuário que encontrou pet | UC11 |
| **Admin** | Administrador do sistema | UC18, UC19, UC20, UC21 |

---

## 8. Glossário

- **UC**: Use Case (Caso de Uso)
- **Ator**: Entidade que interage com o sistema
- **Fluxo Principal**: Sequência normal de eventos
- **Fluxo Alternativo (FA)**: Variação do fluxo principal
- **Extensão (E)**: Comportamento opcional
- **Pré-condição**: Estado necessário antes da execução
- **Pós-condição**: Estado resultante após execução
- **<<include>>**: Relacionamento obrigatório
- **<<extend>>**: Relacionamento opcional
- **Matching**: Algoritmo de correspondência de pets
- **Protocolo**: Código único de rastreamento

---

**Versão**: 1.0  
**Última Atualização**: 23/11/2025  
**Autor**: Daniel
**Projeto**: TCC - S.O.S Pets
