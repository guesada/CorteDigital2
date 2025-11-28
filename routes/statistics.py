"""Rotas de estatísticas avançadas."""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from db import db, Appointment, Review
from services import exigir_login, usuario_atual
from collections import Counter

statistics_bp = Blueprint("statistics", __name__, url_prefix="/api/statistics")


@statistics_bp.route("/dashboard", methods=["GET"])
def dashboard_stats():
    """Estatísticas completas do dashboard do barbeiro."""
    if not exigir_login("barbeiro"):
        return jsonify({"success": False, "message": "Apenas barbeiros"}), 401
    
    user = usuario_atual()
    barbeiro_id = user['id']
    
    # Período (últimos 30 dias por padrão)
    days = int(request.args.get('days', 30))
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Buscar agendamentos do período
    appointments = Appointment.query.filter(
        Appointment.barbeiro_id == barbeiro_id,
        Appointment.date >= start_date
    ).all()
    
    # Métricas básicas
    total_appointments = len(appointments)
    completed = len([a for a in appointments if a.status == 'concluido'])
    cancelled = len([a for a in appointments if a.status == 'cancelado'])
    pending = len([a for a in appointments if a.status in ['agendado', 'pendente']])
    
    # Receita
    revenue = sum(float(a.total_price or 0) for a in appointments if a.status == 'concluido')
    
    # Serviços mais populares
    services = Counter(a.servico for a in appointments if a.status == 'concluido')
    top_services = [{"name": name, "count": count} for name, count in services.most_common(5)]
    
    # Clientes únicos
    unique_clients = len(set(a.cliente_email for a in appointments if a.cliente_email))
    
    # Taxa de conclusão
    completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
    
    # Taxa de cancelamento
    cancellation_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
    
    # Ticket médio
    avg_ticket = revenue / completed if completed > 0 else 0
    
    # Avaliações
    reviews = Review.query.filter_by(barbeiro_id=barbeiro_id).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 5.0
    total_reviews = len(reviews)
    
    # Horários mais populares
    time_slots = Counter(a.time for a in appointments if a.status == 'concluido')
    popular_times = [{"time": time, "count": count} for time, count in time_slots.most_common(5)]
    
    # Dias da semana mais populares
    weekday_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    weekdays = []
    for a in appointments:
        if a.status == 'concluido' and a.date:
            try:
                date_obj = datetime.strptime(a.date, '%Y-%m-%d')
                weekdays.append(date_obj.weekday())
            except:
                pass
    
    weekday_counts = Counter(weekdays)
    popular_weekdays = [
        {"day": weekday_names[day], "count": count} 
        for day, count in sorted(weekday_counts.items())
    ]
    
    return jsonify({
        "success": True,
        "data": {
            "period_days": days,
            "total_appointments": total_appointments,
            "completed": completed,
            "cancelled": cancelled,
            "pending": pending,
            "revenue": round(revenue, 2),
            "unique_clients": unique_clients,
            "completion_rate": round(completion_rate, 1),
            "cancellation_rate": round(cancellation_rate, 1),
            "avg_ticket": round(avg_ticket, 2),
            "avg_rating": round(avg_rating, 1),
            "total_reviews": total_reviews,
            "top_services": top_services,
            "popular_times": popular_times,
            "popular_weekdays": popular_weekdays
        }
    })


@statistics_bp.route("/revenue-chart", methods=["GET"])
def revenue_chart():
    """Dados para gráfico de receita."""
    if not exigir_login("barbeiro"):
        return jsonify({"success": False, "message": "Apenas barbeiros"}), 401
    
    user = usuario_atual()
    barbeiro_id = user['id']
    
    # Últimos 7 dias
    days_data = []
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        appointments = Appointment.query.filter(
            Appointment.barbeiro_id == barbeiro_id,
            Appointment.date == date,
            Appointment.status == 'concluido'
        ).all()
        
        revenue = sum(float(a.total_price or 0) for a in appointments)
        count = len(appointments)
        
        days_data.append({
            "date": date,
            "revenue": round(revenue, 2),
            "count": count
        })
    
    return jsonify({"success": True, "data": days_data})


@statistics_bp.route("/client-retention", methods=["GET"])
def client_retention():
    """Análise de retenção de clientes."""
    if not exigir_login("barbeiro"):
        return jsonify({"success": False, "message": "Apenas barbeiros"}), 401
    
    user = usuario_atual()
    barbeiro_id = user['id']
    
    # Buscar todos os agendamentos concluídos
    appointments = Appointment.query.filter(
        Appointment.barbeiro_id == barbeiro_id,
        Appointment.status == 'concluido'
    ).all()
    
    # Contar agendamentos por cliente
    client_counts = Counter(a.cliente_email for a in appointments if a.cliente_email)
    
    # Categorizar clientes
    new_clients = sum(1 for count in client_counts.values() if count == 1)
    returning_clients = sum(1 for count in client_counts.values() if 2 <= count <= 5)
    loyal_clients = sum(1 for count in client_counts.values() if count > 5)
    
    total_clients = len(client_counts)
    
    return jsonify({
        "success": True,
        "data": {
            "total_clients": total_clients,
            "new_clients": new_clients,
            "returning_clients": returning_clients,
            "loyal_clients": loyal_clients,
            "retention_rate": round((returning_clients + loyal_clients) / total_clients * 100, 1) if total_clients > 0 else 0
        }
    })
