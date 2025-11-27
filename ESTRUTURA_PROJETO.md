# 📁 Estrutura do Projeto Corte Digital

## 🎯 Organização de Arquivos

### JavaScript (`static/js/`)

```
static/js/
├── shared/              # Módulos compartilhados entre cliente e barbeiro
│   ├── api.js          # Configuração de API e helpers de requisição
│   ├── auth.js         # Funções de autenticação (login, cadastro, logout)
│   ├── navigation.js   # Funções de navegação entre telas
│   ├── theme.js        # Gerenciamento de tema claro/escuro
│   ├── utils.js        # Funções utilitárias (formatação, debounce, etc)
│   ├── notifications.js # Sistema de notificações
│   └── micro-interactions.js # Animações e interações
│
├── barbeiro/           # Módulos específicos do barbeiro
│   └── barbeiro-dashboard.js # Dashboard profissional do barbeiro
│
├── cliente/            # Módulos específicos do cliente
│   └── novo-agendamento.js # Sistema de agendamento do cliente
│
├── app.js             # [LEGADO] Arquivo antigo (será removido)
└── index.js           # Arquivo principal que carrega todos os módulos
```

### CSS (`static/css/`)

```
static/css/
├── shared/             # Estilos compartilhados
│   ├── styles.css     # Estilos base e variáveis CSS
│   ├── visual-improvements.css # Melhorias visuais gerais
│   ├── modern-upgrade.css # Componentes modernos
│   ├── notifications.css # Estilos de notificações
│   └── proximos-agendamentos.css # Cards de agendamentos
│
├── barbeiro/          # Estilos do barbeiro
│   ├── barbeiro-professional.css # Dashboard profissional
│   └── agenda-inteligente.css # Agenda inteligente
│
└── cliente/           # Estilos do cliente
    ├── dashboard-intuitiva.css # Dashboard do cliente
    ├── cliente-upgrade.css # Melhorias visuais do cliente
    ├── novo-agendamento.css # Formulário de agendamento
    ├── booking-form.css # Formulário de reserva
    ├── calendar-picker.css # Seletor de calendário
    └── progressive-booking.css # Agendamento progressivo
```

## 🔄 Ordem de Carregamento

### Para Barbeiro (`templates/barbeiro_dashboard.html`):

```html
<!-- CSS -->
<link rel="stylesheet" href="css/shared/styles.css">
<link rel="stylesheet" href="css/shared/visual-improvements.css">
<link rel="stylesheet" href="css/shared/modern-upgrade.css">
<link rel="stylesheet" href="css/shared/notifications.css">
<link rel="stylesheet" href="css/barbeiro/agenda-inteligente.css">
<link rel="stylesheet" href="css/barbeiro/barbeiro-professional.css">

<!-- JavaScript -->
<script src="js/shared/api.js"></script>
<script src="js/shared/utils.js"></script>
<script src="js/shared/theme.js"></script>
<script src="js/shared/navigation.js"></script>
<script src="js/shared/auth.js"></script>
<script src="js/shared/notifications.js"></script>
<script src="js/shared/micro-interactions.js"></script>
<script src="js/barbeiro/barbeiro-dashboard.js"></script>
<script src="js/index.js"></script>
```

### Para Cliente (`templates/cliente_dashboard.html`):

```html
<!-- CSS -->
<link rel="stylesheet" href="css/shared/styles.css">
<link rel="stylesheet" href="css/shared/visual-improvements.css">
<link rel="stylesheet" href="css/shared/modern-upgrade.css">
<link rel="stylesheet" href="css/shared/notifications.css">
<link rel="stylesheet" href="css/cliente/dashboard-intuitiva.css">
<link rel="stylesheet" href="css/cliente/novo-agendamento.css">

<!-- JavaScript -->
<script src="js/shared/api.js"></script>
<script src="js/shared/utils.js"></script>
<script src="js/shared/theme.js"></script>
<script src="js/shared/navigation.js"></script>
<script src="js/shared/auth.js"></script>
<script src="js/shared/notifications.js"></script>
<script src="js/shared/micro-interactions.js"></script>
<script src="js/cliente/novo-agendamento.js"></script>
<script src="js/index.js"></script>
```

## 📦 Módulos

### Shared Modules

#### `api.js`
- Configuração de endpoints da API
- Helper `apiRequest()` para requisições HTTP
- Tratamento de erros centralizado

#### `auth.js`
- `fazerLogin()` - Autenticação de usuários
- `fazerCadastro()` - Registro de novos usuários
- `logout()` - Encerrar sessão

#### `navigation.js`
- `showScreen()` - Navegar entre telas
- `showSection()` - Mostrar seções específicas
- `switchTab()` - Alternar entre abas

#### `theme.js`
- `toggleTheme()` - Alternar tema claro/escuro
- `initTheme()` - Inicializar tema salvo

#### `utils.js`
- `formatCurrency()` - Formatar valores monetários
- `formatDate()` - Formatar datas
- `debounce()` - Debounce de funções
- `throttle()` - Throttle de funções

### Barbeiro Modules

#### `barbeiro-dashboard.js`
- Dashboard profissional com métricas de negócio
- Agenda inteligente
- Gerenciamento de agendamentos
- Estatísticas e gráficos

### Cliente Modules

#### `novo-agendamento.js`
- Sistema de agendamento progressivo
- Seleção de barbeiro e serviço
- Calendário e horários disponíveis
- Confirmação de agendamento

## 🎨 Benefícios da Nova Estrutura

✅ **Modularização** - Código organizado em módulos específicos
✅ **Reutilização** - Componentes compartilhados entre cliente e barbeiro
✅ **Manutenibilidade** - Fácil localizar e modificar funcionalidades
✅ **Performance** - Carrega apenas o necessário para cada página
✅ **Escalabilidade** - Fácil adicionar novos módulos
✅ **Clareza** - Estrutura de pastas intuitiva

## 🚀 Próximos Passos

1. ✅ Criar estrutura de pastas
2. ✅ Dividir app.js em módulos
3. ✅ Mover arquivos para pastas corretas
4. ✅ Atualizar template do barbeiro
5. ⏳ Atualizar template do cliente
6. ⏳ Remover app.js legado
7. ⏳ Testar todas as funcionalidades
