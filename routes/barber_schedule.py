"""
Rotas para gerenciamento de horários de trabalho dos barbeiros
"""
from flask import Blueprint, request, jsonify, session
from db import db, Barber, DEFAULT_HORARIOS
import json

barber_schedule_bp = Blueprint('barber_schedule', __name__)


@barber_schedule_bp.route('/api/barber-schedule', methods=['GET'])
def get_barber_schedule():
    """Retorna os horários de trabalho do barbeiro logado"""
    try:
        if 'user_id' not in session or session.get('user_type') != 'barbeiro':
            return jsonify({"success": False, "message": "Não autorizado"}), 401
        
        barbeiro_id = session['user_id']
        barbeiro = Barber.query.get(barbeiro_id)
        
        if not barbeiro:
            return jsonify({"success": False, "message": "Barbeiro não encontrado"}), 404
        
        # Parse disponibilidade
        disponibilidade = json.loads(barbeiro.disponibilidade or "[]")
        
        # Se não tiver horários configurados, retornar padrão
        if not disponibilidade:
            disponibilidade = [
                {
                    "dia": "Segunda",
                    "ativo": True,
                    "horarios": DEFAULT_HORARIOS.copy()
                },
                {
                    "dia": "Terça",
                    "ativo": True,
                    "horarios": DEFAULT_HORARIOS.copy()
                },
                {
                    "dia": "Quarta",
                    "ativo": True,
                    "horarios": DEFAULT_HORARIOS.copy()
                },
                {
                    "dia": "Quinta",
                    "ativo": True,
                    "horarios": DEFAULT_HORARIOS.copy()
                },
                {
                    "dia": "Sexta",
                    "ativo": True,
                    "horarios": DEFAULT_HORARIOS.copy()
                },
                {
                    "dia": "Sábado",
                    "ativo": False,
                    "horarios": []
                },
                {
                    "dia": "Domingo",
                    "ativo": False,
                    "horarios": []
                }
            ]
        
        return jsonify({
            "success": True,
            "data": disponibilidade
        })
        
    except Exception as e:
        print(f"Erro ao buscar horários: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@barber_schedule_bp.route('/api/barber-schedule', methods=['POST'])
def update_barber_schedule():
    """Atualiza os horários de trabalho do barbeiro"""
    try:
        if 'user_id' not in session or session.get('user_type') != 'barbeiro':
            return jsonify({"success": False, "message": "Não autorizado"}), 401
        
        barbeiro_id = session['user_id']
        barbeiro = Barber.query.get(barbeiro_id)
        
        if not barbeiro:
            return jsonify({"success": False, "message": "Barbeiro não encontrado"}), 404
        
        data = request.get_json()
        disponibilidade = data.get('disponibilidade', [])
        
        # Validar estrutura
        dias_validos = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        
        for item in disponibilidade:
            if 'dia' not in item or item['dia'] not in dias_validos:
                return jsonify({"success": False, "message": "Dia inválido"}), 400
            
            if 'ativo' not in item or not isinstance(item['ativo'], bool):
                return jsonify({"success": False, "message": "Campo 'ativo' inválido"}), 400
            
            if 'horarios' not in item or not isinstance(item['horarios'], list):
                return jsonify({"success": False, "message": "Campo 'horarios' inválido"}), 400
        
        # Salvar
        barbeiro.disponibilidade = json.dumps(disponibilidade, ensure_ascii=False)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Horários atualizados com sucesso!"
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar horários: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@barber_schedule_bp.route('/api/barber-schedule/<int:barbeiro_id>', methods=['GET'])
def get_barber_schedule_public(barbeiro_id):
    """Retorna os horários de trabalho de um barbeiro específico (público para clientes)"""
    try:
        barbeiro = Barber.query.get(barbeiro_id)
        
        if not barbeiro:
            return jsonify({"success": False, "message": "Barbeiro não encontrado"}), 404
        
        disponibilidade = json.loads(barbeiro.disponibilidade or "[]")
        
        # Se não tiver horários, retornar padrão
        if not disponibilidade:
            disponibilidade = [
                {"dia": "Segunda", "ativo": True, "horarios": DEFAULT_HORARIOS.copy()},
                {"dia": "Terça", "ativo": True, "horarios": DEFAULT_HORARIOS.copy()},
                {"dia": "Quarta", "ativo": True, "horarios": DEFAULT_HORARIOS.copy()},
                {"dia": "Quinta", "ativo": True, "horarios": DEFAULT_HORARIOS.copy()},
                {"dia": "Sexta", "ativo": True, "horarios": DEFAULT_HORARIOS.copy()},
                {"dia": "Sábado", "ativo": False, "horarios": []},
                {"dia": "Domingo", "ativo": False, "horarios": []}
            ]
        
        return jsonify({
            "success": True,
            "data": disponibilidade
        })
        
    except Exception as e:
        print(f"Erro ao buscar horários públicos: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
