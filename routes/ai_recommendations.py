"""
Rotas para Recomendações com IA
"""
from flask import Blueprint, jsonify, request, session
from services.ai_recommendation_service import AIRecommendationService
from datetime import datetime
import db

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/patterns', methods=['GET'])
def get_user_patterns():
    """Retorna análise de padrões do usuário"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        # Busca agendamentos do usuário
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date, time, service_name, barber_name, status
            FROM appointments
            WHERE user_id = ? AND status != 'cancelado'
            ORDER BY date DESC, time DESC
        ''', (user_id,))
        
        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                'date': row[0],
                'time': row[1],
                'service_name': row[2],
                'barber_name': row[3],
                'status': row[4]
            })
        
        conn.close()
        
        # Analisa padrões
        patterns = AIRecommendationService.analyze_user_patterns(appointments)
        
        return jsonify({
            'success': True,
            'data': patterns
        })
        
    except Exception as e:
        print(f"Erro ao analisar padrões: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@ai_bp.route('/suggest-appointment', methods=['GET'])
def suggest_appointment():
    """Sugere próximos horários de agendamento"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        # Busca agendamentos do usuário
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date, time, service_name, barber_name
            FROM appointments
            WHERE user_id = ? AND status != 'cancelado'
            ORDER BY date DESC, time DESC
        ''', (user_id,))
        
        appointments = []
        last_date = None
        
        for row in cursor.fetchall():
            appointments.append({
                'date': row[0],
                'time': row[1],
                'service_name': row[2],
                'barber_name': row[3]
            })
            
            if not last_date:
                try:
                    last_date = datetime.strptime(row[0], '%Y-%m-%d')
                except:
                    pass
        
        conn.close()
        
        # Analisa padrões
        patterns = AIRecommendationService.analyze_user_patterns(appointments)
        
        # Gera sugestões
        suggestions = AIRecommendationService.suggest_next_appointment(
            patterns,
            last_date
        )
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'patterns': patterns
            }
        })
        
    except Exception as e:
        print(f"Erro ao sugerir agendamento: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@ai_bp.route('/recommend-service', methods=['GET'])
def recommend_service():
    """Recomenda serviços baseado em padrões"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        # Busca agendamentos do usuário
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date, time, service_name, barber_name
            FROM appointments
            WHERE user_id = ? AND status != 'cancelado'
        ''', (user_id,))
        
        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                'date': row[0],
                'time': row[1],
                'service_name': row[2],
                'barber_name': row[3]
            })
        
        # Busca todos os serviços
        cursor.execute('SELECT id, nome, descricao, preco, duracao FROM services')
        services = []
        for row in cursor.fetchall():
            services.append({
                'id': row[0],
                'nome': row[1],
                'descricao': row[2],
                'preco': row[3],
                'duracao': row[4]
            })
        
        conn.close()
        
        # Analisa padrões
        patterns = AIRecommendationService.analyze_user_patterns(appointments)
        
        # Gera recomendações
        recommendations = AIRecommendationService.recommend_service(patterns, services)
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
        
    except Exception as e:
        print(f"Erro ao recomendar serviço: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@ai_bp.route('/recommend-barber', methods=['GET'])
def recommend_barber():
    """Recomenda barbeiros baseado em padrões"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        # Busca agendamentos do usuário
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date, time, service_name, barber_name
            FROM appointments
            WHERE user_id = ? AND status != 'cancelado'
        ''', (user_id,))
        
        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                'date': row[0],
                'time': row[1],
                'service_name': row[2],
                'barber_name': row[3]
            })
        
        # Busca todos os barbeiros
        cursor.execute('SELECT id, nome FROM barbers')
        barbers = []
        for row in cursor.fetchall():
            barbers.append({
                'id': row[0],
                'nome': row[1]
            })
        
        conn.close()
        
        # Analisa padrões
        patterns = AIRecommendationService.analyze_user_patterns(appointments)
        
        # Gera recomendações
        recommendations = AIRecommendationService.recommend_barber(patterns, barbers)
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
        
    except Exception as e:
        print(f"Erro ao recomendar barbeiro: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@ai_bp.route('/insights', methods=['GET'])
def get_insights():
    """Retorna insights sobre padrões do usuário"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        # Busca agendamentos do usuário
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date, time, service_name, barber_name
            FROM appointments
            WHERE user_id = ? AND status != 'cancelado'
        ''', (user_id,))
        
        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                'date': row[0],
                'time': row[1],
                'service_name': row[2],
                'barber_name': row[3]
            })
        
        conn.close()
        
        # Analisa padrões
        patterns = AIRecommendationService.analyze_user_patterns(appointments)
        
        # Gera insights
        insights = AIRecommendationService.get_insights(patterns)
        
        return jsonify({
            'success': True,
            'data': insights
        })
        
    except Exception as e:
        print(f"Erro ao gerar insights: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
