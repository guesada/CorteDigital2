// Configuração do chat - gerado dinamicamente pelo Flask
window.chatConfig = {
    userType: "{{ tipo|default('cliente', true) }}",
    userId: {{ user_id|default('null', true) }},
    userName: "{{ nome|default('Usuário', true)|safe }}"
};

window.userType = window.chatConfig.userType;
window.userId = window.chatConfig.userId;
window.userName = window.chatConfig.userName;
