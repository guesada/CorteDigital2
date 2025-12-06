# 💇 Groomly - Sistema Profissional de Agendamento

Sistema completo de agendamento para estúdios de beleza, salões de cabeleireiro, clínicas de estética e espaços de bem-estar.

**Groomly** é a solução moderna e profissional para gerenciar agendamentos, clientes e serviços em estabelecimentos de beleza.

## 🌟 Funcionalidades

### Para Clientes
- ✅ Agendamento online de serviços
- 📅 Visualização de horários disponíveis
- 💬 Chat em tempo real com profissionais
- ⭐ Sistema de avaliações e reviews
- 🔔 Notificações de confirmação e lembretes
- 📊 Histórico de agendamentos
- 🤖 Recomendações inteligentes baseadas em IA

### Para Profissionais
- 📆 Gestão completa de agenda
- 💰 Controle de preços personalizados por serviço
- 📈 Dashboard com analytics e métricas
- 💬 Chat com clientes
- ⭐ Gestão de avaliações
- 🔔 Notificações em tempo real
- 📸 Portfolio de trabalhos
- ⏰ Configuração de horários de trabalho
- 🚫 Bloqueio de horários (folgas, compromissos)

### Recursos Técnicos
- 🔐 Autenticação segura com sessões
- 🔄 WebSocket para comunicação em tempo real
- 🤖 IA para análise de padrões e recomendações
- 📱 Interface responsiva
- 🎨 Design moderno e intuitivo
- 🔍 Validações avançadas
- 📊 Sistema de analytics
- 🗄️ Banco de dados MySQL/MariaDB

## 🚀 Tecnologias

- **Backend**: Python 3.11+, Flask
- **Banco de Dados**: MySQL/MariaDB com SQLAlchemy ORM
- **Real-time**: Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **IA/ML**: scikit-learn, pandas, numpy

## 📋 Pré-requisitos

- Python 3.11 ou superior
- MySQL 8.0 ou MariaDB 10.5+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/guesada/CorteDigital.git
cd CorteDigital
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados:
   - Crie um banco de dados MySQL
   - Copie `.env.example` para `.env`
   - Configure as variáveis de ambiente

5. Execute a aplicação:
```bash
python app.py
```

6. Acesse no navegador:
```
http://localhost:5001
```

## ⚙️ Configuração

Edite o arquivo `.env` com suas configurações:

```env
# Banco de Dados
DATABASE_URL=usuario@localhost:3306@senha@nome_banco

# Aplicação
SECRET_KEY=sua_chave_secreta_aqui
HOST=0.0.0.0
PORT=5001
FLASK_ENV=development

# Features
FEATURE_AI_RECOMMENDATIONS=true
FEATURE_CHAT=true
FEATURE_NOTIFICATIONS=true
FEATURE_REVIEWS=true
FEATURE_ANALYTICS=true
```

## 📁 Estrutura do Projeto

```
CorteDigital/
├── app.py                 # Aplicação principal
├── config.py              # Configurações
├── constants.py           # Constantes
├── db.py                  # Modelos do banco de dados
├── database_config.py     # Configuração de conexão
├── requirements.txt       # Dependências
├── .env                   # Variáveis de ambiente
├── routes/                # Rotas da aplicação
│   ├── auth.py           # Autenticação
│   ├── appointments.py   # Agendamentos
│   ├── chat.py           # Chat
│   ├── reviews.py        # Avaliações
│   ├── analytics.py      # Analytics
│   └── ...
├── services/              # Lógica de negócio
│   ├── auth_service.py
│   ├── appointment_service.py
│   ├── chat_service.py
│   └── ...
├── templates/             # Templates HTML
└── static/                # Arquivos estáticos (CSS, JS, imagens)
```

## 🗄️ Modelos de Dados

### Principais Entidades

- **Cliente**: Usuários que agendam serviços
- **Professional**: Profissionais de beleza (cabeleireiros, manicures, etc)
- **Service**: Serviços oferecidos
- **Appointment**: Agendamentos
- **Review**: Avaliações de serviços
- **ChatConversation**: Conversas entre clientes e profissionais
- **Notification**: Notificações do sistema
- **WorkingHours**: Horários de trabalho dos profissionais
- **BlockedTime**: Horários bloqueados

## 🎯 Categorias Suportadas

### Profissionais
- Cabeleireiro
- Manicure
- Pedicure
- Esteticista
- Maquiador
- Barbeiro
- Depilador
- Massagista
- Designer de Sobrancelhas

### Serviços
- Cabelo (corte, coloração, tratamentos)
- Unhas (manicure, pedicure, nail art)
- Estética Facial
- Estética Corporal
- Maquiagem
- Barba
- Depilação
- Massagem
- Sobrancelhas

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT.

## 🎨 Design

Interface moderna e responsiva desenvolvida com Bootstrap 5, focada em usabilidade e experiência do usuário.

## 👥 Autores

- **Guesada** - [guesada](https://github.com/guesada)

## 📞 Suporte

Para suporte, envie um email para suporte@groomly.com ou abra uma issue no GitHub.

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!

**Groomly** - Transformando a gestão de beleza em algo simples e eficiente.
