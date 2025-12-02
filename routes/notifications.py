"""
Rotas de Notificações
"""
from flask import Blueprint, jsonify, session
from flask_socketio import emit
from services import notification_service

notifications_bp = Blueprint('notifications', __name__)


def register_notifications_routes(app):
    """Registra as rotas de notificações"""
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')


def register_notification_events(socketio):
    """Registra eventos WebSocket de notificações"""
    
    @socketio.on('join_notifications')
    def handle_join_notifications():
        """Usuário entra na sala de notificações"""
        if 'user_id' not in session:
            return
        
        from flask_socketio import join_room
        user_id = session['user_id']
        user_type = session['tipo']
        join_room(f'notifications_{user_type}_{user_id}')
        
        # Envia contagem de não lidas
        count = notification_service.get_unread_count(user_id, user_type)
        emit('unread_count', {'count': count})


@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    """Obtém notificações do usuário"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        user_type = session['tipo']
        
        notifications = notification_service.get_user_notifications(user_id, user_type)
        unread_count = notification_service.get_unread_count(user_id, user_type)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/unread', methods=['GET'])
def get_unread():
    """Obtém apenas notificações não lidas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        user_type = session['tipo']
        
        notifications = notification_service.get_user_notifications(
            user_id, user_type, unread_only=True
        )
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
def mark_read(notification_id):
    """Marca notificação como lida"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        success = notification_service.mark_as_read(notification_id, user_id)
        
        if success:
            # Atualiza contagem
            user_type = session['tipo']
            count = notification_service.get_unread_count(user_id, user_type)
            
            return jsonify({
                'success': True,
                'unread_count': count
            })
        else:
            return jsonify({'success': False, 'message': 'Notificação não encontrada'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/read-all', methods=['POST'])
def mark_all_read():
    """Marca todas as notificações como lidas"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        user_type = session['tipo']
        
        count = notification_service.mark_all_as_read(user_id, user_type)
        
        return jsonify({
            'success': True,
            'marked': count,
            'unread_count': 0
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Deleta uma notificação"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        success = notification_service.delete_notification(notification_id, user_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Notificação não encontrada'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Função auxiliar para enviar notificação em tempo real
def send_realtime_notification(socketio, user_id, user_type, notification):
    """Envia notificação em tempo real via WebSocket"""
    socketio.emit('new_notification', notification, 
                  room=f'notifications_{user_type}_{user_id}')
