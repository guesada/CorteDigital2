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
    
    body = request.get_json() or {}
    
    # Validar dados
    servicos = ["Corte", "Corte + Barba", "Barba"]
    precos = {}
    
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
    
    # Atualizar ou criar preços
    for servico, preco in precos.items():
        price_obj = BarberPrice.query.filter_by(
            barbeiro_id=barbeiro_id,
            servico_nome=servico
        ).first()
        
        if price_obj:
            price_obj.preco = preco
        else:
            price_obj = BarberPrice(
                barbeiro_id=barbeiro_id,
                servico_nome=servico,
                preco=preco
            )
            db.session.add(price_obj)
    
    db.session.commit()
    
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
