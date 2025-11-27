"""Serviços de acesso a dados usando SQLAlchemy (MySQL).

Este módulo substitui a persistência por JSON. Ele expõe funções usadas
pelas rotas para autenticação, consultas e mutações (agendamentos, estoque, etc.).
"""

from __future__ import annotations

from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional

from flask import session, current_app

from db import db, Cliente, Barber, Service, Appointment, Product, Notification, Report, DEFAULT_HORARIOS


def init_app(app):
    # Configura o SQLALCHEMY_DATABASE_URI
    # Formato: mysql+pymysql://usuario:senha@host:porta/database
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        # Se DATABASE_URL estiver no formato: root@localhost:3306@senha
        # Converter para: mysql+pymysql://root:senha@localhost:3306/cortedigital
        parts = database_url.split('@')
        if len(parts) == 3:
            user = parts[0]
            host_port = parts[1]
            password = parts[2]
            database_url = f"mysql+pymysql://{user}:{password}@{host_port}/cortedigital"
    else:
        # Fallback para banco local
        database_url = "mysql+pymysql://root:pjn%402024@localhost:3306/cortedigital"
    
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", database_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_if_needed()


def _seed_if_needed():
    # Cria apenas estrutura mínima necessária para o sistema funcionar
    # Todos os dados reais devem ser cadastrados via interface
    
    # Cria apenas o relatório inicial (necessário para o sistema)
    if Report.query.count() == 0:
        r = Report(nome="ultima_semana", dados=json.dumps({"total_servicos": 0, "ticket_medio": 0, "clientes_novos": 0, "faturamento": 0}))
        db.session.add(r)
        db.session.commit()
    
    # Não criar mais dados de seed:
    # - Usuários devem ser cadastrados via registro
    # - Barbeiros devem ser cadastrados via interface administrativa
    # - Serviços devem ser cadastrados via interface administrativa
    # - Produtos devem ser cadastrados via interface do barbeiro
    # - Notificações são criadas automaticamente pelo sistema


def usuario_atual() -> Optional[Dict[str, Any]]:
    email = session.get("usuario_email")
    tipo = session.get("usuario_tipo")
    if not email:
        return None
    
    # Buscar em clientes ou barbeiros dependendo do tipo
    if tipo == "barbeiro":
        u = Barber.query.filter_by(email=email).first()
    else:
        u = Cliente.query.filter_by(email=email).first()
    
    return u.to_dict() if u else None


def exigir_login(tipo: Optional[str] = None) -> bool:
    user = usuario_atual()
    if not user:
        return False
    if tipo and user.get("tipo") != tipo:
        return False
    return True


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    # Tentar buscar como cliente
    u = Cliente.query.filter_by(email=email).first()
    if u and u.senha == password:
        return u.to_dict()
    
    # Tentar buscar como barbeiro
    b = Barber.query.filter_by(email=email).first()
    if b and b.senha == password:
        return b.to_dict()
    
    return None


def register_user(nome: str, email: str, senha: str, tipo: str = "cliente") -> bool:
    # Verificar se email já existe em clientes ou barbeiros
    if Cliente.query.filter_by(email=email).first() or Barber.query.filter_by(email=email).first():
        return False
    
    if tipo == "barbeiro":
        # Criar barbeiro com horários padrão
        b = Barber(
            nome=nome,
            email=email,
            senha=senha,
            foto="https://via.placeholder.com/150",
            especialidades=json.dumps(["Corte", "Barba"]),
            avaliacao=5.0,
            preco_base=50.0,
            disponibilidade=json.dumps(DEFAULT_HORARIOS)
        )
        db.session.add(b)
    else:
        # Criar cliente
        c = Cliente(nome=nome, email=email, senha=senha)
        db.session.add(c)
    
    db.session.commit()
    return True


def list_barbers() -> List[Dict[str, Any]]:
    return [b.to_dict() for b in Barber.query.all()]


def list_services() -> List[Dict[str, Any]]:
    return [s.to_dict() for s in Service.query.all()]


def list_notifications() -> List[Dict[str, Any]]:
    return [n.to_dict() for n in Notification.query.all()]


def report_week() -> Dict[str, Any]:
    r = Report.query.filter_by(nome="ultima_semana").first()
    return r.to_dict()["dados"] if r else {}


def list_products() -> List[Dict[str, Any]]:
    return [p.to_dict() for p in Product.query.all()]


def create_product(data: Dict[str, Any]) -> Dict[str, Any]:
    prod = Product(
        produto=data.get("name"),
        quantidade=int(data.get("quantity", 0)),
        preco_custo=float(data.get("price", 0)),
        fornecedor=data.get("supplier"),
        categoria=data.get("category"),
        descricao=data.get("description"),
    )
    db.session.add(prod)
    db.session.commit()
    return prod.to_dict()


def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    p = Product.query.get(product_id)
    return p.to_dict() if p else None


def update_product(product_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    p = Product.query.get(product_id)
    if not p:
        return None
    p.produto = data.get("name", p.produto)
    p.quantidade = int(data.get("quantity", p.quantidade))
    p.preco_custo = float(data.get("price", p.preco_custo))
    p.fornecedor = data.get("supplier", p.fornecedor)
    p.categoria = data.get("category", p.categoria)
    p.descricao = data.get("description", p.descricao)
    db.session.commit()
    return p.to_dict()


def delete_product(product_id: int) -> bool:
    p = Product.query.get(product_id)
    if not p:
        return False
    db.session.delete(p)
    db.session.commit()
    return True


def list_appointments_for_user() -> List[Dict[str, Any]]:
    """Lista agendamentos do usuário logado."""
    usuario = usuario_atual()
    if not usuario:
        return []
    
    if usuario["tipo"] == "barbeiro":
        # Barbeiro vê apenas seus próprios agendamentos
        return [a.to_dict() for a in Appointment.query.filter_by(barbeiro=usuario["name"]).order_by(Appointment.date.desc(), Appointment.time.desc()).all()]
    
    # Cliente vê apenas seus próprios agendamentos
    return [a.to_dict() for a in Appointment.query.filter_by(cliente_email=usuario["email"]).all()]


def list_appointments_for_barber(barber_id: int, date: Optional[str] = None) -> List[Dict[str, Any]]:
    # retorna agendamentos para um barbeiro específico, opcionalmente filtrando por data (YYYY-MM-DD)
    q = Appointment.query.filter_by(barbeiro_id=barber_id)
    if date:
        q = q.filter_by(date=date)
    return [a.to_dict() for a in q.all()]


def create_appointment(body: Dict[str, Any]) -> Dict[str, Any]:
    """Cria um novo agendamento."""
    usuario = usuario_atual()
    if not usuario:
        raise ValueError("Usuário não autenticado")
    
    # Gerar ID único
    last = Appointment.query.order_by(Appointment.id.desc()).first()
    if last and last.id.startswith('APT'):
        apt_id = f"APT{int(last.id[3:]) + 1:05d}"
    else:
        apt_id = "APT00001"
    
    ap = Appointment(
        id=apt_id,
        cliente=usuario.get("name", "Cliente"),
        cliente_email=usuario.get("email", ""),
        barbeiro=body["barberName"],
        barbeiro_id=int(body["barberId"]),
        servico=body["serviceName"],
        servico_id=int(body["serviceId"]),
        date=body["date"],
        time=body["time"],
        status="agendado",
        total_price=float(body.get("total", 0)),
        created_at=datetime.utcnow().isoformat(),
    )
    
    db.session.add(ap)
    db.session.commit()
    return ap.to_dict()


def cancel_appointment_by_id(appointment_id: str) -> bool:
    ap = Appointment.query.get(appointment_id)
    if not ap:
        return False
    db.session.delete(ap)
    db.session.commit()
    return True


def update_appointment_status(appointment_id: str, status: str) -> bool:
    ap = Appointment.query.get(appointment_id)
    if not ap:
        return False
    ap.status = status
    db.session.commit()
    return True


def dados_iniciais() -> Dict[str, Any]:
    # Para compatibilidade: devolve um resumo dos dados iniciais; prefer usar funções específicas.
    return {
        "barbeiros": list_barbers(),
        "servicos": list_services(),
        "estoque": list_products(),
        "notificacoes": list_notifications(),
        "relatorios": {"ultima_semana": report_week()},
    }
