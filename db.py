from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT
import json

db = SQLAlchemy()

# Horários padrão para novos barbeiros
DEFAULT_HORARIOS = [
    "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
]


class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(300))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "name": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "endereco": self.endereco,
            "tipo": "cliente"
        }


class Barber(db.Model):
    __tablename__ = "barbers"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(400))
    especialidades = db.Column(LONGTEXT)  # store JSON list
    avaliacao = db.Column(db.Float, default=5.0)
    preco_base = db.Column(db.Float, default=0.0)
    disponibilidade = db.Column(LONGTEXT)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(300))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "name": self.nome,
            "email": self.email,
            "foto": self.foto,
            "especialidades": json.loads(self.especialidades or "[]"),
            "avaliacao": self.avaliacao,
            "preco_base": self.preco_base,
            "disponibilidade": json.loads(self.disponibilidade or "[]"),
            "telefone": self.telefone,
            "endereco": self.endereco,
            "tipo": "barbeiro"
        }


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    preco = db.Column(db.Float)
    duracao = db.Column(db.Integer)
    descricao = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "preco": self.preco, "duracao": self.duracao, "descricao": self.descricao}


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.String(50), primary_key=True)
    cliente = db.Column(db.String(150))
    cliente_email = db.Column(db.String(150))
    barbeiro = db.Column(db.String(150))
    barbeiro_id = db.Column(db.Integer)
    servico = db.Column(db.String(200))
    servico_id = db.Column(db.Integer)
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    status = db.Column(db.String(50))
    total_price = db.Column(db.Float)
    created_at = db.Column(db.String(100), default=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente,
            "cliente_email": self.cliente_email,
            "barbeiro": self.barbeiro,
            "barbeiro_id": self.barbeiro_id,
            "servico": self.servico,
            "servico_id": self.servico_id,
            "date": self.date,
            "time": self.time,
            "status": self.status,
            "total_price": self.total_price,
            "created_at": self.created_at,
        }


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(200))
    quantidade = db.Column(db.Integer)
    preco_custo = db.Column(db.Float)
    fornecedor = db.Column(db.String(150))
    categoria = db.Column(db.String(100))
    descricao = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "produto": self.produto,
            "quantidade": self.quantidade,
            "preco_custo": self.preco_custo,
            "fornecedor": self.fornecedor,
            "categoria": self.categoria,
            "descricao": self.descricao,
        }


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    dados = db.Column(LONGTEXT)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "dados": json.loads(self.dados or "{}")}


class BarberPrice(db.Model):
    """Preços personalizados de cada barbeiro para cada serviço"""
    __tablename__ = "barber_prices"
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    servico_nome = db.Column(db.String(100), nullable=False)  # 'Corte', 'Barba', 'Corte + Barba'
    preco = db.Column(db.Float, nullable=False)
    
    # Índice único para evitar duplicatas
    __table_args__ = (db.UniqueConstraint('barbeiro_id', 'servico_nome', name='_barbeiro_servico_uc'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "barbeiro_id": self.barbeiro_id,
            "servico_nome": self.servico_nome,
            "preco": self.preco
        }


class Review(db.Model):
    """Avaliações dos clientes sobre os serviços"""
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbers.id'), nullable=False)
    appointment_id = db.Column(db.String(50), db.ForeignKey('appointments.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "barbeiro_id": self.barbeiro_id,
            "appointment_id": self.appointment_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Statistic(db.Model):
    """Estatísticas do sistema"""
    __tablename__ = "statistics"
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbers.id'))
    metric_name = db.Column(db.String(100), nullable=False)  # 'total_appointments', 'revenue', etc
    metric_value = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(50))  # 'daily', 'weekly', 'monthly', 'yearly'
    date = db.Column(db.Date, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "barbeiro_id": self.barbeiro_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "period": self.period,
            "date": self.date.isoformat() if self.date else None
        } 
