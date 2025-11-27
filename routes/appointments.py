"""Rotas de agendamentos."""
from flask import Blueprint, jsonify, request
from datetime import datetime
from services import (exigir_login, list_appointments_for_user, create_appointment,
                      cancel_appointment_by_id, update_appointment_status, usuario_atual,
                      list_appointments_for_barber)

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


def validate_datetime(date_str, time_str):
    """Valida data e horário."""
    try:
        apt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        if apt_date < today:
            return "Não é possível agendar em datas passadas"
        
        if apt_date == today:
            apt_time = datetime.strptime(time_str, "%H:%M").time()
            if apt_time <= datetime.now().time():
                return "Não é possível agendar em horários que já passaram"
        
        return None
    except ValueError:
        return "Data ou horário inválido"


def notify_barber(barber_id, client_name, service_name, date_str, time_str, apt_id):
    """Cria notificação para o barbeiro."""
    try:
        from routes.notifications import create_notification
        date_formatted = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        message = f"{client_name} agendou {service_name} para {date_formatted} às {time_str}"
        create_notification(barber_id, 'Novo Agendamento', message, 'new-appointment', str(apt_id))
    except Exception as e:
        print(f"Erro ao criar notificação: {e}")


@appointments_bp.route("", methods=["GET", "POST"])
def appointments_root():
    if not exigir_login():
        return jsonify({"success": False, "message": "Não autenticado"}), 401

    if request.method == "GET":
        return jsonify({"success": True, "data": list_appointments_for_user()})

    # POST - Criar agendamento
    body = request.get_json() or {}
    required = ["barberId", "barberName", "serviceId", "serviceName", "date", "time"]
    if not all(body.get(f) for f in required):
        return jsonify({"success": False, "message": "Dados incompletos"}), 400

    barber_id, date, time = int(body["barberId"]), body["date"], body["time"]
    
    # Validar data/hora
    error = validate_datetime(date, time)
    if error:
        return jsonify({"success": False, "message": error}), 400

    # Verificar conflito
    existing = [a for a in list_appointments_for_barber(barber_id, date)
                if a.get("time") == time and a.get("status") != "cancelado"]
    if existing:
        return jsonify({"success": False, "message": "Horário já agendado"}), 409

    # Criar agendamento
    novo = create_appointment(body)
    
    # Notificar barbeiro
    user = usuario_atual()
    notify_barber(barber_id, user.get('name', 'Cliente'), body['serviceName'], date, time, novo.get('id'))
    
    return jsonify({"success": True, "data": novo}), 201


@appointments_bp.delete("/<appointment_id>")
def cancel_appointment(appointment_id: str):
    if not exigir_login():
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    # Remover notificações relacionadas ao agendamento cancelado
    try:
        from routes.notifications import delete_notification_by_data
        delete_notification_by_data(appointment_id)
    except Exception as e:
        print(f"Erro ao remover notificação: {e}")
    
    if not cancel_appointment_by_id(appointment_id):
        return jsonify({"success": False, "message": "Agendamento não encontrado"}), 404
    return jsonify({"success": True})


@appointments_bp.patch("/<appointment_id>/status")
def update_status(appointment_id: str):
    if not exigir_login("barbeiro"):
        return jsonify({"success": False, "message": "Apenas barbeiros"}), 401

    status = (request.get_json() or {}).get("status")
    if not status:
        return jsonify({"success": False, "message": "Status obrigatório"}), 400

    if not update_appointment_status(appointment_id, status):
        return jsonify({"success": False, "message": "Agendamento não encontrado"}), 404
    
    # Remover notificações quando concluído ou cancelado
    if status in ['concluido', 'cancelado']:
        try:
            from routes.notifications import delete_notification_by_data
            delete_notification_by_data(appointment_id)
        except Exception as e:
            print(f"Erro ao remover notificação: {e}")
    
    return jsonify({"success": True})


@appointments_bp.get('/for_barber/<int:barber_id>')
def appointments_for_barber(barber_id: int):
    if not exigir_login():
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    data = list_appointments_for_barber(barber_id, request.args.get('date'))
    return jsonify({"success": True, "data": data})
