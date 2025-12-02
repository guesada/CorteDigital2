"""
Rotas de Analytics e Estatísticas
"""
from flask import Blueprint, jsonify, session
from services import analytics_service

analytics_bp = Blueprint('analytics', __name__)


def register_analytics_routes(app):
    """Registra as rotas de analytics"""
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')


@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Obtém estatísticas do dashboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        user_type = session['tipo']
        
        stats = analytics_service.get_dashboard_stats(user_id, user_type)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/appointments-chart', methods=['GET'])
def get_appointments_chart():
    """Dados para gráfico de agendamentos"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        from flask import request
        user_id = session['user_id']
        user_type = session['tipo']
        period = request.args.get('period', 'month')
        
        data = analytics_service.get_appointments_chart_data(user_id, user_type, period)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/revenue-chart', methods=['GET'])
def get_revenue_chart():
    """Dados para gráfico de faturamento (apenas barbeiro)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if session.get('tipo') != 'barbeiro':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        from flask import request
        user_id = session['user_id']
        period = request.args.get('period', 'month')
        
        data = analytics_service.get_revenue_chart_data(user_id, period)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/services-distribution', methods=['GET'])
def get_services_distribution():
    """Distribuição de serviços"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        user_type = session['tipo']
        
        data = analytics_service.get_services_distribution(user_id, user_type)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/peak-hours', methods=['GET'])
def get_peak_hours():
    """Horários de pico (apenas barbeiro)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if session.get('tipo') != 'barbeiro':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        user_id = session['user_id']
        data = analytics_service.get_peak_hours(user_id)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/top-clients', methods=['GET'])
def get_top_clients():
    """Clientes mais frequentes (apenas barbeiro)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if session.get('tipo') != 'barbeiro':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        from flask import request
        user_id = session['user_id']
        limit = int(request.args.get('limit', 10))
        
        clients = analytics_service.get_top_clients(user_id, limit)
        
        return jsonify({
            'success': True,
            'clients': clients
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/monthly-comparison', methods=['GET'])
def get_monthly_comparison():
    """Comparação mensal"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        user_id = session['user_id']
        user_type = session['tipo']
        
        data = analytics_service.get_monthly_comparison(user_id, user_type)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
