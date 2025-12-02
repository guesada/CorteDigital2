"""
Sistema de Notificações em Tempo Real
"""
from datetime import datetime
from database_config import get_database_connection


def create_notifications_table():
    """Cria a tabela de notificações"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                user_type ENUM('cliente', 'barbeiro') NOT NULL,
                type ENUM('agendamento', 'cancelamento', 'confirmacao', 'lembrete', 'chat', 'avaliacao') NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                link VARCHAR(500),
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id, user_type),
                INDEX idx_read (is_read),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        print("✅ Tabela de notificações criada!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar tabela de notificações: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def create_notification(user_id, user_type, notif_type, title, message, link=None):
    """Cria uma nova notificação"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO notifications (user_id, user_type, type, title, message, link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, user_type, notif_type, title, message, link))
        
        conn.commit()
        notification_id = cursor.lastrowid
        
        # Retorna a notificação criada
        cursor.execute("""
            SELECT * FROM notifications WHERE id = %s
        """, (notification_id,))
        
        notif = cursor.fetchone()
        if notif and notif.get('created_at'):
            notif['created_at'] = notif['created_at'].isoformat()
        
        return notif
        
    finally:
        cursor.close()
        conn.close()


def get_user_notifications(user_id, user_type, limit=50, unread_only=False):
    """Obtém notificações do usuário"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT * FROM notifications
            WHERE user_id = %s AND user_type = %s
        """
        params = [user_id, user_type]
        
        if unread_only:
            query += " AND is_read = FALSE"
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        notifications = cursor.fetchall()
        
        # Converte datetime
        for notif in notifications:
            if notif.get('created_at'):
                notif['created_at'] = notif['created_at'].isoformat()
        
        return notifications
        
    finally:
        cursor.close()
        conn.close()


def mark_as_read(notification_id, user_id):
    """Marca notificação como lida"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = %s AND user_id = %s
        """, (notification_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    finally:
        cursor.close()
        conn.close()


def mark_all_as_read(user_id, user_type):
    """Marca todas as notificações como lidas"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = %s AND user_type = %s AND is_read = FALSE
        """, (user_id, user_type))
        
        conn.commit()
        return cursor.rowcount
        
    finally:
        cursor.close()
        conn.close()


def get_unread_count(user_id, user_type):
    """Obtém contagem de não lidas"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = %s AND user_type = %s AND is_read = FALSE
        """, (user_id, user_type))
        
        result = cursor.fetchone()
        return result['count'] if result else 0
        
    finally:
        cursor.close()
        conn.close()


def delete_notification(notification_id, user_id):
    """Deleta uma notificação"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM notifications
            WHERE id = %s AND user_id = %s
        """, (notification_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    finally:
        cursor.close()
        conn.close()


# Funções auxiliares para criar notificações específicas

def notify_new_appointment(barbeiro_id, cliente_nome, servico, data_hora):
    """Notifica barbeiro sobre novo agendamento"""
    return create_notification(
        user_id=barbeiro_id,
        user_type='barbeiro',
        notif_type='agendamento',
        title='Novo Agendamento',
        message=f'{cliente_nome} agendou {servico} para {data_hora}',
        link='/barbeiro#agenda'
    )


def notify_appointment_confirmed(cliente_id, servico, data_hora):
    """Notifica cliente sobre confirmação"""
    return create_notification(
        user_id=cliente_id,
        user_type='cliente',
        notif_type='confirmacao',
        title='Agendamento Confirmado',
        message=f'Seu agendamento de {servico} para {data_hora} foi confirmado!',
        link='/cliente#agendamentos'
    )


def notify_appointment_cancelled(user_id, user_type, servico, data_hora, motivo=''):
    """Notifica sobre cancelamento"""
    msg = f'Agendamento de {servico} para {data_hora} foi cancelado'
    if motivo:
        msg += f'. Motivo: {motivo}'
    
    return create_notification(
        user_id=user_id,
        user_type=user_type,
        notif_type='cancelamento',
        title='Agendamento Cancelado',
        message=msg,
        link=f'/{user_type}#agendamentos'
    )


def notify_appointment_reminder(cliente_id, servico, data_hora):
    """Lembrete de agendamento"""
    return create_notification(
        user_id=cliente_id,
        user_type='cliente',
        notif_type='lembrete',
        title='Lembrete de Agendamento',
        message=f'Você tem um agendamento de {servico} amanhã às {data_hora}',
        link='/cliente#agendamentos'
    )


def notify_new_message(user_id, user_type, sender_name):
    """Notifica sobre nova mensagem no chat"""
    return create_notification(
        user_id=user_id,
        user_type=user_type,
        notif_type='chat',
        title='Nova Mensagem',
        message=f'{sender_name} enviou uma mensagem',
        link='/chat'
    )


def notify_new_review(barbeiro_id, cliente_nome, rating):
    """Notifica barbeiro sobre nova avaliação"""
    stars = '⭐' * rating
    return create_notification(
        user_id=barbeiro_id,
        user_type='barbeiro',
        notif_type='avaliacao',
        title='Nova Avaliação',
        message=f'{cliente_nome} avaliou seu serviço: {stars}',
        link='/barbeiro#avaliacoes'
    )
