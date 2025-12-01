/**
 * Chat Page - Sistema de Mensagens Completo
 */

class ChatPage {
    constructor() {
        this.socket = null;
        this.currentConversationId = null;
        this.currentOtherUser = null;
        this.conversations = [];
        this.typingTimeout = null;
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.connectSocket();
        this.attachEventListeners();
        this.loadConversations();
    }
    
    connectSocket() {
        this.socket = io({
            transports: ['websocket', 'polling']
        });
        
        this.socket.on('connect', () => {
            console.log('✅ Chat conectado');
            this.showToast('Conectado', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Chat desconectado');
            this.showToast('Desconectado - Tentando reconectar...', 'error');
        });
        
        this.socket.on('new_message', (message) => {
            this.handleNewMessage(message);
        });
        
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
        
        this.socket.on('messages_read', (data) => {
            console.log('Mensagens lidas:', data);
        });
        
        this.socket.on('conversation_updated', (data) => {
            this.loadConversations();
        });
    }
    
    attachEventListeners() {
        // Input de mensagem
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        messageInput.addEventListener('input', (e) => {
            this.handleInputChange(e);
        });
        
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Busca
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.filterConversations(e.target.value);
        });
        
        // Toggle busca
        document.getElementById('searchToggleBtn').addEventListener('click', () => {
            const searchBar = document.getElementById('searchBar');
            searchBar.style.display = searchBar.style.display === 'none' ? 'flex' : 'none';
        });
        
        // Nova conversa
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.openNewChatModal();
        });
    }
    
    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations');
            const data = await response.json();
            
            if (data.success) {
                this.conversations = data.conversations;
                this.renderConversations();
            }
        } catch (error) {
            console.error('Erro ao carregar conversas:', error);
            this.showToast('Erro ao carregar conversas', 'error');
        }
    }
    
    renderConversations() {
        const container = document.getElementById('conversationsContainer');
        
        if (this.conversations.length === 0) {
            container.innerHTML = `
                <div class="conversations-loading">
                    <div class="empty-icon">
                        <i class="fas fa-inbox"></i>
                    </div>
                    <p>Nenhuma conversa ainda</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.conversations.map(conv => {
            const initials = this.getInitials(conv.other_user_nome);
            const time = this.formatTime(conv.last_message_at);
            const unreadClass = conv.unread_count > 0 ? 'unread' : '';
            const activeClass = this.currentConversationId === conv.id ? 'active' : '';
            
            return `
                <div class="conversation-item ${unreadClass} ${activeClass}" 
                     data-conversation-id="${conv.id}"
                     data-user-id="${conv.other_user_id}"
                     data-user-name="${conv.other_user_nome}">
                    <div class="conversation-avatar">${initials}</div>
                    <div class="conversation-content">
                        <div class="conversation-header">
                            <span class="conversation-name">${conv.other_user_nome}</span>
                            <span class="conversation-time">${time}</span>
                        </div>
                        <div class="conversation-preview">${conv.last_message || 'Sem mensagens'}</div>
                    </div>
                    ${conv.unread_count > 0 ? `
                        <div class="conversation-meta">
                            <div class="unread-badge">${conv.unread_count}</div>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        // Adiciona event listeners
        container.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                const conversationId = parseInt(item.dataset.conversationId);
                const userName = item.dataset.userName;
                const userId = parseInt(item.dataset.userId);
                this.openConversation(conversationId, userName, userId);
            });
        });
    }
    
    async openConversation(conversationId, userName, userId) {
        this.currentConversationId = conversationId;
        this.currentOtherUser = { id: userId, name: userName };
        
        // Atualiza UI
        document.getElementById('chatEmpty').style.display = 'none';
        document.getElementById('chatActive').style.display = 'flex';
        
        const initials = this.getInitials(userName);
        document.getElementById('activeUserAvatar').textContent = initials;
        document.getElementById('activeUserName').textContent = userName;
        document.getElementById('typingAvatar').textContent = initials;
        
        // Marca conversa como ativa
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-conversation-id="${conversationId}"]`)?.classList.add('active');
        
        // Carrega mensagens
        await this.loadMessages(conversationId);
        
        // Entra na sala do WebSocket
        this.socket.emit('join_conversation', { conversation_id: conversationId });
        
        // Foca no input
        document.getElementById('messageInput').focus();
    }
    
    async loadMessages(conversationId) {
        try {
            const response = await fetch(`/api/chat/messages/${conversationId}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderMessages(data.messages);
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Erro ao carregar mensagens:', error);
            this.showToast('Erro ao carregar mensagens', 'error');
        }
    }
    
    renderMessages(messages) {
        const container = document.getElementById('messagesContainer');
        
        // Agrupa mensagens por data
        const groupedMessages = this.groupMessagesByDate(messages);
        
        container.innerHTML = '';
        
        Object.keys(groupedMessages).forEach(date => {
            // Adiciona divisor de data
            const divider = document.createElement('div');
            divider.className = 'messages-date-divider';
            divider.innerHTML = `<span>${date}</span>`;
            container.appendChild(divider);
            
            // Adiciona mensagens
            groupedMessages[date].forEach(msg => {
                const messageEl = this.createMessageElement(msg);
                container.appendChild(messageEl);
            });
        });
    }
    
    createMessageElement(msg) {
        const isSent = msg.sender_tipo === window.userType;
        const initials = this.getInitials(msg.sender_nome);
        const time = this.formatMessageTime(msg.created_at);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">${initials}</div>
            <div class="message-content">
                <div class="message-bubble">${this.escapeHtml(msg.message)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        return messageDiv;
    }
    
    groupMessagesByDate(messages) {
        const groups = {};
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        messages.forEach(msg => {
            const msgDate = new Date(msg.created_at);
            let dateLabel;
            
            if (this.isSameDay(msgDate, today)) {
                dateLabel = 'Hoje';
            } else if (this.isSameDay(msgDate, yesterday)) {
                dateLabel = 'Ontem';
            } else {
                dateLabel = msgDate.toLocaleDateString('pt-BR', { 
                    day: '2-digit', 
                    month: 'long',
                    year: msgDate.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
                });
            }
            
            if (!groups[dateLabel]) {
                groups[dateLabel] = [];
            }
            groups[dateLabel].push(msg);
        });
        
        return groups;
    }
    
    isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }
    
    handleInputChange(e) {
        const input = e.target;
        const sendBtn = document.getElementById('sendBtn');
        
        // Auto-resize
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
        
        // Habilita/desabilita botão
        sendBtn.disabled = !input.value.trim();
        
        // Indicador de digitação
        if (this.currentConversationId) {
            if (!this.isTyping && input.value.trim()) {
                this.isTyping = true;
                this.socket.emit('typing', {
                    conversation_id: this.currentConversationId,
                    is_typing: true
                });
            }
            
            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                this.isTyping = false;
                this.socket.emit('typing', {
                    conversation_id: this.currentConversationId,
                    is_typing: false
                });
            }, 1000);
        }
    }
    
    sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || !this.currentConversationId) return;
        
        // Envia via WebSocket
        this.socket.emit('send_message', {
            conversation_id: this.currentConversationId,
            message: message
        });
        
        // Limpa input
        input.value = '';
        input.style.height = 'auto';
        document.getElementById('sendBtn').disabled = true;
        
        // Para indicador de digitação
        if (this.isTyping) {
            this.isTyping = false;
            this.socket.emit('typing', {
                conversation_id: this.currentConversationId,
                is_typing: false
            });
        }
    }
    
    handleNewMessage(message) {
        if (message.conversation_id === this.currentConversationId) {
            // Adiciona mensagem à conversa atual
            const container = document.getElementById('messagesContainer');
            const messageEl = this.createMessageElement(message);
            container.appendChild(messageEl);
            this.scrollToBottom();
        } else {
            // Atualiza lista de conversas
            this.loadConversations();
        }
    }
    
    handleUserTyping(data) {
        const indicator = document.getElementById('typingIndicatorContainer');
        if (data.is_typing) {
            indicator.style.display = 'block';
            this.scrollToBottom();
        } else {
            indicator.style.display = 'none';
        }
    }
    
    filterConversations(query) {
        const items = document.querySelectorAll('.conversation-item');
        const lowerQuery = query.toLowerCase();
        
        items.forEach(item => {
            const name = item.dataset.userName.toLowerCase();
            if (name.includes(lowerQuery)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    async openNewChatModal() {
        const modal = document.getElementById('newChatModal');
        modal.classList.add('active');
        
        // Carrega lista de usuários disponíveis
        try {
            const userType = window.userType === 'cliente' ? 'barbeiro' : 'cliente';
            const response = await fetch(`/api/users/${userType}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderUsersList(data.users);
            }
        } catch (error) {
            console.error('Erro ao carregar usuários:', error);
        }
    }
    
    renderUsersList(users) {
        const container = document.getElementById('newChatUsersList');
        
        container.innerHTML = users.map(user => {
            const initials = this.getInitials(user.nome);
            return `
                <div class="user-item" data-user-id="${user.id}" data-user-name="${user.nome}">
                    <div class="conversation-avatar">${initials}</div>
                    <div class="conversation-content">
                        <div class="conversation-name">${user.nome}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Event listeners
        container.querySelectorAll('.user-item').forEach(item => {
            item.addEventListener('click', async () => {
                const userId = parseInt(item.dataset.userId);
                const userName = item.dataset.userName;
                await this.startNewConversation(userId, userName);
            });
        });
    }
    
    async startNewConversation(userId, userName) {
        try {
            const response = await fetch(`/api/chat/conversation/${userId}`);
            const data = await response.json();
            
            if (data.success) {
                this.closeNewChatModal();
                await this.loadConversations();
                this.openConversation(data.conversation_id, userName, userId);
            }
        } catch (error) {
            console.error('Erro ao criar conversa:', error);
            this.showToast('Erro ao criar conversa', 'error');
        }
    }
    
    closeNewChatModal() {
        document.getElementById('newChatModal').classList.remove('active');
    }
    
    scrollToBottom() {
        const container = document.getElementById('messagesContainer');
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('connectionToast');
        toast.querySelector('span').textContent = message;
        toast.className = `connection-toast ${type}`;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    getInitials(name) {
        return name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
    }
    
    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'agora';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}d`;
        
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    }
    
    formatMessageTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Funções globais
function closeNewChatModal() {
    document.getElementById('newChatModal').classList.remove('active');
}

function toggleInfoPanel() {
    const panel = document.getElementById('chatInfo');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

// Inicializa
let chatPage;
document.addEventListener('DOMContentLoaded', () => {
    chatPage = new ChatPage();
});
