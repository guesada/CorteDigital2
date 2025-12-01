"""
Serviço de chat em tempo real entre barbeiro e cliente
"""
from datetime import datetime
from database_config import get_database_connection


def create_chat_tables():
    """Cria as tabelas necessárias para o sistema de chat"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Tabela de conversas (threads)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT NOT NULL,
                barbeiro_id INT NOT NULL,
                last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                cliente_unread INT DEFAULT 0,
                barbeiro_unread INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (barbeiro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE KEY unique_conversation (cliente_id, barbeiro_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Tabela de mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                sender_id INT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                INDEX idx_conversation (conversation_id),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        print("✅ Tabelas de chat criadas com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar tabelas de chat: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_or_create_conversation(cliente_id, barbeiro_id):
    """Obtém ou cria uma conversa entre cliente e barbeiro"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se já existe conversa
        cursor.execute("""
            SELECT id FROM chat_conversations 
            WHERE cliente_id = %s AND barbeiro_id = %s
        """, (cliente_id, barbeiro_id))
        
        result = cursor.fetchone()
        
        if result:
            return result['id']
        
        # Cria nova conversa
        cursor.execute("""
            INSERT INTO chat_conversations (cliente_id, barbeiro_id)
            VALUES (%s, %s)
        """, (cliente_id, barbeiro_id))
        
        conn.commit()
        return cursor.lastrowid
        
    finally:
        cursor.close()
        conn.close()


def send_message(conversation_id, sender_id, message):
    """Envia uma mensagem no chat"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Insere a mensagem
        cursor.execute("""
            INSERT INTO chat_messages (conversation_id, sender_id, message)
            VALUES (%s, %s, %s)
        """, (conversation_id, sender_id, message))
        
        message_id = cursor.lastrowid
        
        # Atualiza a conversa
        cursor.execute("""
            SELECT cliente_id, barbeiro_id FROM chat_conversations
            WHERE id = %s
        """, (conversation_id,))
        
        conv = cursor.fetchone()
        
        # Incrementa contador de não lidas para o destinatário
        if sender_id == conv['cliente_id']:
            cursor.execute("""
                UPDATE chat_conversations 
                SET barbeiro_unread = barbeiro_unread + 1,
                    last_message_at = NOW()
                WHERE id = %s
            """, (conversation_id,))
        else:
            cursor.execute("""
                UPDATE chat_conversations 
                SET cliente_unread = cliente_unread + 1,
                    last_message_at = NOW()
                WHERE id = %s
            """, (conversation_id,))
        
        conn.commit()
        
        # Retorna a mensagem criada
        cursor.execute("""
            SELECT m.*, u.nome as sender_nome
            FROM chat_messages m
            JOIN usuarios u ON m.sender_id = u.id
            WHERE m.id = %s
        """, (message_id,))
        
        return cursor.fetchone()
        
    finally:
        cursor.close()
        conn.close()


def get_messages(conversation_id, limit=50):
    """Obtém mensagens de uma conversa"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT m.*, u.nome as sender_nome, u.tipo as sender_tipo
            FROM chat_messages m
            JOIN usuarios u ON m.sender_id = u.id
            WHERE m.conversation_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (conversation_id, limit))
        
        messages = cursor.fetchall()
        
        # Converte datetime para string
        for msg in messages:
            if msg['created_at']:
                msg['created_at'] = msg['created_at'].isoformat()
        
        return list(reversed(messages))
        
    finally:
        cursor.close()
        conn.close()


def mark_as_read(conversation_id, user_id):
    """Marca mensagens como lidas"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Marca mensagens como lidas
        cursor.execute("""
            UPDATE chat_messages 
            SET is_read = TRUE
            WHERE conversation_id = %s 
            AND sender_id != %s
            AND is_read = FALSE
        """, (conversation_id, user_id))
        
        # Reseta contador de não lidas
        cursor.execute("""
            SELECT cliente_id, barbeiro_id FROM chat_conversations
            WHERE id = %s
        """, (conversation_id,))
        
        conv = cursor.fetchone()
        
        if conv['cliente_id'] == user_id:
            cursor.execute("""
                UPDATE chat_conversations 
                SET cliente_unread = 0
                WHERE id = %s
            """, (conversation_id,))
        else:
            cursor.execute("""
                UPDATE chat_conversations 
                SET barbeiro_unread = 0
                WHERE id = %s
            """, (conversation_id,))
        
        conn.commit()
        
    finally:
        cursor.close()
        conn.close()


def get_user_conversations(user_id, user_tipo):
    """Obtém todas as conversas de um usuário"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        if user_tipo == 'cliente':
            cursor.execute("""
                SELECT 
                    c.id,
                    c.last_message_at,
                    c.cliente_unread as unread_count,
                    b.id as other_user_id,
                    b.nome as other_user_nome,
                    (SELECT message FROM chat_messages 
                     WHERE conversation_id = c.id 
                     ORDER BY created_at DESC LIMIT 1) as last_message
                FROM chat_conversations c
                JOIN usuarios b ON c.barbeiro_id = b.id
                WHERE c.cliente_id = %s
                ORDER BY c.last_message_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.last_message_at,
                    c.barbeiro_unread as unread_count,
                    cl.id as other_user_id,
                    cl.nome as other_user_nome,
                    (SELECT message FROM chat_messages 
                     WHERE conversation_id = c.id 
                     ORDER BY created_at DESC LIMIT 1) as last_message
                FROM chat_conversations c
                JOIN usuarios cl ON c.cliente_id = cl.id
                WHERE c.barbeiro_id = %s
                ORDER BY c.last_message_at DESC
            """, (user_id,))
        
        conversations = cursor.fetchall()
        
        # Converte datetime para string
        for conv in conversations:
            if conv['last_message_at']:
                conv['last_message_at'] = conv['last_message_at'].isoformat()
        
        return conversations
        
    finally:
        cursor.close()
        conn.close()


def get_total_unread(user_id, user_tipo):
    """Obtém total de mensagens não lidas"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        if user_tipo == 'cliente':
            cursor.execute("""
                SELECT COALESCE(SUM(cliente_unread), 0) as total
                FROM chat_conversations
                WHERE cliente_id = %s
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT COALESCE(SUM(barbeiro_unread), 0) as total
                FROM chat_conversations
                WHERE barbeiro_id = %s
            """, (user_id,))
        
        result = cursor.fetchone()
        return result['total']
        
    finally:
        cursor.close()
        conn.close()
