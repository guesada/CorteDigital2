"""Rotas para gerenciamento de preços dos barbeiros."""
from flask import Blueprint, jsonify, request, session
from db import db, BarberPrice
from services import exigir_login, usuario_atual

barber_prices_bp = Blueprint("barber_prices", __name__, url_prefix="/api/barber-prices")


@barber_prices_bp.get("")
def get_barber_prices():
    """Obter preços do barbeiro logado ou de um barbeiro específico."""
    if not exigir_login():
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    # Verificar se é para buscar preços de um barbeiro específico
    barbeiro_id = request.args.get('barbeiro_id', type=int)
    
    if not barbeiro_id:
        # Buscar preços do barbeiro logado
        user = usuario_atual()
        if user['tipo'] != 'barbeiro':
            return jsonify({"success": False, "message": "Apenas barbeiros"}), 403
        barbeiro_id = user['id']
    
    # Buscar preços
    prices = BarberPrice.query.filter_by(barbeiro_id=barbeiro_id).all()
    
    # Converter para dict
    prices_dict = {}
    for price in prices:
        prices_dict[price.servico_nome] = price.preco
    
    # Se não houver preços, retornar preços padrão
    if not prices_dict:
        prices_dict = {
            "Corte": 35.00,
            "Corte + Barba": 55.00,
            "Barba": 25.00
        }
    
    return jsonify({"success": True, "data": prices_dict})


@barber_prices_bp.post("")
def update_barber_prices():
    """Atualizar preços do barbeiro logado."""
    if not exigir_login("barbeiro"):
        return jsonify({"success": False, "message": "Apenas barbeiros"}), 403
    
    user = usuario_atual()
    barbeiro_id = user['id']
    barbeiro_nome = user['name']
    
    body = request.get_json() or {}
    
    # Validar dados
    servicos = ["Corte", "Corte + Barba", "Barba"]
    precos = {}
    precos_alterados = []
    
    for servico in servicos:
        preco = body.get(servico)
        if preco is None:
            return jsonify({"success": False, "message": f"Preço de '{servico}' obrigatório"}), 400
        
        try:
            preco = float(preco)
            if preco < 0:
                return jsonify({"success": False, "message": f"Preço de '{servico}' deve ser positivo"}), 400
            precos[servico] = preco
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": f"Preço de '{servico}' inválido"}), 400
    
    # Atualizar ou criar preços e detectar mudanças
    from db import Notification, Cliente, Appointment
    from datetime import datetime
    
    for servico, preco_novo in precos.items():
        price_obj = BarberPrice.query.filter_by(
            barbeiro_id=barbeiro_id,
            servico_nome=servico
        ).first()
        
        preco_antigo = None
        if price_obj:
            preco_antigo = price_obj.preco
            if preco_antigo != preco_novo:
                precos_alterados.append({
                    'servico': servico,
                    'preco_antigo': preco_antigo,
                    'preco_novo': preco_novo
                })
            price_obj.preco = preco_novo
        else:
            price_obj = BarberPrice(
                barbeiro_id=barbeiro_id,
                servico_nome=servico,
                preco=preco_novo
            )
            db.session.add(price_obj)
            # Primeira vez definindo preço, não notificar
    
    db.session.commit()
    
    # Criar notificações para clientes que já agendaram com este barbeiro
    if precos_alterados:
        # Buscar clientes únicos que têm agendamentos com este barbeiro
        agendamentos = Appointment.query.filter_by(barbeiro_id=barbeiro_id).all()
        clientes_emails = set(apt.cliente_email for apt in agendamentos if apt.cliente_email)
        
        # Criar mensagem de notificação
        if len(precos_alterados) == 1:
            mudanca = precos_alterados[0]
            if mudanca['preco_novo'] < mudanca['preco_antigo']:
                mensagem = f"🎉 Boa notícia! O barbeiro {barbeiro_nome} reduziu o preço de {mudanca['servico']} de R$ {mudanca['preco_antigo']:.2f} para R$ {mudanca['preco_novo']:.2f}!"
            else:
                mensagem = f"📢 O barbeiro {barbeiro_nome} atualizou o preço de {mudanca['servico']} de R$ {mudanca['preco_antigo']:.2f} para R$ {mudanca['preco_novo']:.2f}"
        else:
            mensagem = f"📢 O barbeiro {barbeiro_nome} atualizou os preços de {len(precos_alterados)} serviços. Confira os novos valores!"
        
        # Criar notificação para cada cliente
        for cliente_email in clientes_emails:
            notificacao = Notification(
                usuario_email=cliente_email,
                tipo="preco_alterado",
                mensagem=mensagem,
                lida=False,
                data=datetime.utcnow().isoformat()
            )
            db.session.add(notificacao)
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Preços atualizados! {len(clientes_emails)} clientes foram notificados.",
            "clientes_notificados": len(clientes_emails)
        })
    
    return jsonify({"success": True, "message": "Preços atualizados com sucesso"})


@barber_prices_bp.get("/all-barbers")
def get_all_barbers_prices():
    """Obter preços de todos os barbeiros (para clientes escolherem)."""
    if not exigir_login():
        return jsonify({"success": False, "message": "Não autenticado"}), 401
    
    from db import Barber
    
    # Buscar todos os barbeiros
    barbeiros = Barber.query.all()
    
    result = []
    for barbeiro in barbeiros:
        # Buscar preços do barbeiro
        prices = BarberPrice.query.filter_by(barbeiro_id=barbeiro.id).all()
        
        prices_dict = {}
        for price in prices:
            prices_dict[price.servico_nome] = price.preco
        
        # Se não houver preços, usar padrão
        if not prices_dict:
            prices_dict = {
                "Corte": 35.00,
                "Corte + Barba": 55.00,
                "Barba": 25.00
            }
        
        result.append({
            "id": barbeiro.id,
            "nome": barbeiro.nome,
            "foto": barbeiro.foto,
            "avaliacao": barbeiro.avaliacao,
            "precos": prices_dict
        })
    
    return jsonify({"success": True, "data": result})
