/**
 * Sistema de Chat em Tempo Real
 * Estilo Twitter DM
 */

class ChatSystem {
    constructor() {
        this.socket = null;
        this.currentConversationId = null;
        this.conversations = [];
        this.typingTimeout = null;
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.createChatUI();
        this.connectSocket();
        this.attachEventListeners();
        this.loadConversations();
    }
    
    createChatUI() {
        const chatHTML = `
            <div class="chat-container">
                <button class="chat-button" id="chatToggle">
                    <i class="fas fa-comments"></i>
                    <span class="unread-badge" id="chatUnreadBadge" style="display: none;">0</span>
                </button>
                
                <div class="chat-window" id="chatWindow">
                    <div class="chat-header">
                        <div class="chat-header-left">
                            <button class="chat-back-btn" id="chatBackBtn">
                                <i class="fas fa-arrow-left"></i>
                            </button>
                            <div class="chat-header-title" id="chatHeaderTitle">Mensagens</div>
                        </div>
                        <button class="chat-close-btn" id="chatCloseBtn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="connection-status" id="connectionStatus">
                        Conectando...
                    </div>
                    
                    <div class="chat-body">
                        <!-- Lista de Conversas -->
                        <div class="conversations-list" id="conversationsList">
                            <div class="conversations-empty">
                                <i class="fas fa-comments"></i>
                                <p>Nenhuma conversa ainda</p>
                            </div>
                        </div>
                        
                        <!-- Visualização de Mensagens -->
                        <div class="messages-view" id="messagesView">
                            <div class="messages-container" id="messagesContainer"></div>
                            
                            <div class="typing-indicator" id="typingIndicator">
                                <div class="typing-dots">
                                    <span class="typing-dot"></span>
                                    <span class="typing-dot"></span>
                                    <span class="typing-dot"></span>
                                </div>
                                <span>digitando...</span>
                            </div>
                            
                            <div class="message-input-container">
                                <div class="message-input-wrapper">
                                    <textarea 
                                        class="message-input" 
                                        id="messageInput" 
                                        placeholder="Digite uma mensagem..."
                                        rows="1"
                                    ></textarea>
                                    <button class="send-button" id="sendButton" disabled>
                                        <i class="fas fa-paper-plane"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatHTML);
    }
    
    attachEventListeners() {
        // Toggle chat window
        document.getElementById('chatToggle').addEventListener('click', () => {
            this.toggleChat();
        });
        
        document.getElementById('chatCloseBtn').addEventListener('click', () => {
            this.closeChat();
        });
        
        // Voltar para lista de conversas
        document.getElementById('chatBackBtn').addEventListener('click', () => {
            this.showConversationsList();
        });
        
        // Input de mensagem
        const messageInput = document.getElementById('messageInput');
        messageInput.addEventListener('input', (e) => {
            this.handleInputChange(e);
        });
        
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Botão enviar
        document.getElementById('sendButton').addEventListener('click', () => {
            this.sendMessage();
        });
    }
    
    connectSocket() {
        // Conecta ao servidor SocketIO
        this.socket = io({
            transports: ['websocket', 'polling']
        });
        
        this.socket.on('connect', () => {
            console.log('Chat conectado');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Chat desconectado');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('connected', (data) => {
            console.log('Usuário conectado:', data.user_id);
        });
        
        this.socket.on('new_message', (message) => {
            this.handleNewMessage(message);
        });
        
        this.socket.on('messages_read', (data) => {
            this.handleMessagesRead(data);
        });
        
        this.socket.on('conversation_updated', (data) => {
            this.handleConversationUpdate(data);
        });
        
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
        
        this.socket.on('error', (data) => {
            console.error('Erro no chat:', data.message);
        });
    }
    
    updateConnectionStatus(connected) {
        const status = document.getElementById('connectionStatus');
        if (connected) {
            status.textContent = 'Conectado';
            status.className = 'connection-status connected';
            setTimeout(() => {
                status.style.display = 'none';
            }, 2000);
        } else {
            status.textContent = 'Desconectado - Tentando reconectar...';
            status.className = 'connection-status disconnected';
            status.style.display = 'block';
        }
    }
    
    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations');
            const data = await response.json();
            
            if (data.success) {
                this.conversations = data.conversations;
                this.renderConversations();
                this.updateUnreadBadge(data.total_unread);
            }
        } catch (error) {
            console.error('Erro ao carregar conversas:', error);
        }
    }
    
    renderConversations() {
        const container = document.getElementById('conversationsList');
        
        if (this.conversations.length === 0) {
            container.innerHTML = `
                <div class="conversations-empty">
                    <i class="fas fa-comments"></i>
                    <p>Nenhuma conversa ainda</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.conversations.map(conv => {
            const initials = this.getInitials(conv.other_user_nome);
            const time = this.formatTime(conv.last_message_at);
            const unreadClass = conv.unread_count > 0 ? 'unread' : '';
            
            return `
                <div class="conversation-item ${unreadClass}" data-conversation-id="${conv.id}" data-user-id="${conv.other_user_id}" data-user-name="${conv.other_user_nome}">
                    <div class="conversation-avatar">${initials}</div>
                    <div class="conversation-content">
                        <div class="conversation-header">
                            <span class="conversation-name">${conv.other_user_nome}</span>
                            <span class="conversation-time">${time}</span>
                        </div>
                        <div class="conversation-preview">${conv.last_message || 'Sem mensagens'}</div>
                    </div>
                    ${conv.unread_count > 0 ? `<div class="conversation-unread">${conv.unread_count}</div>` : ''}
                </div>
            `;
        }).join('');
        
        // Adiciona event listeners
        container.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                const conversationId = parseInt(item.dataset.conversationId);
                const userName = item.dataset.userName;
                this.openConversation(conversationId, userName);
            });
        });
    }
    
    async openConversation(conversationId, userName) {
        this.currentConversationId = conversationId;
        
        // Atualiza UI
        document.getElementById('chatHeaderTitle').textContent = userName;
        document.getElementById('chatBackBtn').classList.add('active');
        document.getElementById('conversationsList').style.display = 'none';
        document.getElementById('messagesView').classList.add('active');
        
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
        }
    }
    
    renderMessages(messages) {
        const container = document.getElementById('messagesContainer');
        
        container.innerHTML = messages.map(msg => {
            const isSent = msg.sender_tipo === this.getUserType();
            const initials = this.getInitials(msg.sender_nome);
            const time = this.formatTime(msg.created_at);
            
            return `
                <div class="message ${isSent ? 'sent' : ''}">
                    <div class="message-avatar">${initials}</div>
                    <div class="message-content">
                        <div class="message-bubble">${this.escapeHtml(msg.message)}</div>
                        <div class="message-time">${time}</div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    handleInputChange(e) {
        const input = e.target;
        const sendButton = document.getElementById('sendButton');
        
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
        
        // Habilita/desabilita botão enviar
        sendButton.disabled = !input.value.trim();
        
        // Emite evento de digitação
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
        document.getElementById('sendButton').disabled = true;
        
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
            const isSent = message.sender_tipo === this.getUserType();
            const initials = this.getInitials(message.sender_nome);
            const time = this.formatTime(message.created_at);
            
            const messageHTML = `
                <div class="message ${isSent ? 'sent' : ''}">
                    <div class="message-avatar">${initials}</div>
                    <div class="message-content">
                        <div class="message-bubble">${this.escapeHtml(message.message)}</div>
                        <div class="message-time">${time}</div>
                    </div>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', messageHTML);
            this.scrollToBottom();
        }
    }
    
    handleMessagesRead(data) {
        // Atualiza UI quando mensagens são lidas
        console.log('Mensagens lidas:', data);
    }
    
    handleConversationUpdate(data) {
        // Atualiza lista de conversas
        this.loadConversations();
    }
    
    handleUserTyping(data) {
        const indicator = document.getElementById('typingIndicator');
        if (data.is_typing) {
            indicator.classList.add('active');
            this.scrollToBottom();
        } else {
            indicator.classList.remove('active');
        }
    }
    
    showConversationsList() {
        this.currentConversationId = null;
        
        // Sai da sala do WebSocket
        if (this.currentConversationId) {
            this.socket.emit('leave_conversation', { 
                conversation_id: this.currentConversationId 
            });
        }
        
        // Atualiza UI
        document.getElementById('chatHeaderTitle').textContent = 'Mensagens';
        document.getElementById('chatBackBtn').classList.remove('active');
        document.getElementById('conversationsList').style.display = 'block';
        document.getElementById('messagesView').classList.remove('active');
        
        // Recarrega conversas
        this.loadConversations();
    }
    
    toggleChat() {
        const chatWindow = document.getElementById('chatWindow');
        chatWindow.classList.toggle('active');
        
        if (chatWindow.classList.contains('active')) {
            this.loadConversations();
        }
    }
    
    closeChat() {
        document.getElementById('chatWindow').classList.remove('active');
    }
    
    updateUnreadBadge(count) {
        const badge = document.getElementById('chatUnreadBadge');
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        const container = document.getElementById('messagesContainer');
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
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
        
        // Menos de 1 minuto
        if (diff < 60000) {
            return 'agora';
        }
        
        // Menos de 1 hora
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m`;
        }
        
        // Menos de 24 horas
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h`;
        }
        
        // Menos de 7 dias
        if (diff < 604800000) {
            const days = Math.floor(diff / 86400000);
            return `${days}d`;
        }
        
        // Formato de data
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getUserType() {
        // Obtém tipo de usuário da sessão (implementar conforme sua lógica)
        return window.userType || 'cliente';
    }
    
    // Método público para iniciar conversa com usuário específico
    async startConversation(otherUserId, otherUserName) {
        try {
            const response = await fetch(`/api/chat/conversation/${otherUserId}`);
            const data = await response.json();
            
            if (data.success) {
                this.toggleChat();
                setTimeout(() => {
                    this.openConversation(data.conversation_id, otherUserName);
                }, 300);
            }
        } catch (error) {
            console.error('Erro ao iniciar conversa:', error);
        }
    }
}

// Inicializa o chat quando o DOM estiver pronto
let chatSystem;
document.addEventListener('DOMContentLoaded', () => {
    chatSystem = new ChatSystem();
});

// Exporta para uso global
window.ChatSystem = ChatSystem;
window.chatSystem = chatSystem;
