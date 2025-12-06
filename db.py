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


class Professional(db.Model):
    """Profissionais de beleza (cabeleireiros, manicures, esteticistas, etc)"""
    __tablename__ = "professionals"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(400))
    especialidades = db.Column(LONGTEXT)  # store JSON list: ['Corte', 'Coloração', 'Manicure', etc]
    categoria = db.Column(db.String(100))  # 'Cabeleireiro', 'Manicure', 'Esteticista', 'Maquiador', etc
    avaliacao = db.Column(db.Float, default=5.0)
    total_avaliacoes = db.Column(db.Integer, default=0)
    preco_base = db.Column(db.Float, default=0.0)
    disponibilidade = db.Column(LONGTEXT)  # store JSON
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(300))
    bio = db.Column(db.Text)  # Biografia/descrição do profissional
    instagram = db.Column(db.String(100))
    portfolio = db.Column(LONGTEXT)  # JSON array de URLs de fotos
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "name": self.nome,
            "email": self.email,
            "foto": self.foto,
            "especialidades": json.loads(self.especialidades or "[]"),
            "categoria": self.categoria,
            "avaliacao": self.avaliacao,
            "total_avaliacoes": self.total_avaliacoes,
            "preco_base": self.preco_base,
            "disponibilidade": json.loads(self.disponibilidade or "[]"),
            "telefone": self.telefone,
            "endereco": self.endereco,
            "bio": self.bio,
            "instagram": self.instagram,
            "portfolio": json.loads(self.portfolio or "[]"),
            "ativo": self.ativo,
            "tipo": "profissional"
        }


# Manter compatibilidade com código antigo
class Barber(Professional):
    """Alias para compatibilidade - usar Professional no novo código"""
    __tablename__ = None
    __mapper_args__ = {
        'concrete': True
    }


class Service(db.Model):
    """Serviços oferecidos (Corte, Coloração, Manicure, Pedicure, Maquiagem, etc)"""
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100))  # 'Cabelo', 'Unhas', 'Estética', 'Maquiagem'
    preco = db.Column(db.Float)
    preco_min = db.Column(db.Float)  # Preço mínimo (para serviços com variação)
    preco_max = db.Column(db.Float)  # Preço máximo
    duracao = db.Column(db.Integer)  # Duração em minutos
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(400))  # URL da imagem do serviço
    popular = db.Column(db.Boolean, default=False)  # Serviço popular/destaque
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "preco_min": self.preco_min,
            "preco_max": self.preco_max,
            "duracao": self.duracao,
            "descricao": self.descricao,
            "imagem": self.imagem,
            "popular": self.popular,
            "ativo": self.ativo
        }


class Appointment(db.Model):
    """Agendamentos de serviços"""
    __tablename__ = "appointments"
    id = db.Column(db.String(50), primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    cliente = db.Column(db.String(150))
    cliente_email = db.Column(db.String(150))
    profissional_id = db.Column(db.Integer)  # ID do profissional
    profissional = db.Column(db.String(150))  # Nome do profissional
    servico = db.Column(db.String(200))
    servico_id = db.Column(db.Integer)
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    status = db.Column(db.String(50))  # 'agendado', 'confirmado', 'em_andamento', 'concluido', 'cancelado', 'nao_compareceu'
    total_price = db.Column(db.Float)
    observacoes = db.Column(db.Text)  # Observações do cliente
    cancelamento_motivo = db.Column(db.Text)  # Motivo do cancelamento
    created_at = db.Column(db.String(100), default=lambda: datetime.utcnow().isoformat())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos legados para compatibilidade
    barbeiro = db.Column(db.String(150))
    barbeiro_id = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente": self.cliente,
            "cliente_email": self.cliente_email,
            "profissional_id": self.profissional_id or self.barbeiro_id,
            "profissional": self.profissional or self.barbeiro,
            "servico": self.servico,
            "servico_id": self.servico_id,
            "date": self.date,
            "time": self.time,
            "status": self.status,
            "total_price": self.total_price,
            "observacoes": self.observacoes,
            "cancelamento_motivo": self.cancelamento_motivo,
            "created_at": self.created_at,
            # Campos legados para compatibilidade
            "barbeiro": self.profissional or self.barbeiro,
            "barbeiro_id": self.profissional_id or self.barbeiro_id,
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


class ProfessionalPrice(db.Model):
    """Preços personalizados de cada profissional para cada serviço"""
    __tablename__ = "professional_prices"
    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    servico_nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    duracao_customizada = db.Column(db.Integer)  # Duração customizada em minutos
    ativo = db.Column(db.Boolean, default=True)
    
    # Índice único para evitar duplicatas
    __table_args__ = (db.UniqueConstraint('profissional_id', 'servico_id', name='_profissional_servico_uc'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "profissional_id": self.profissional_id,
            "servico_id": self.servico_id,
            "servico_nome": self.servico_nome,
            "preco": self.preco,
            "duracao_customizada": self.duracao_customizada,
            "ativo": self.ativo
        }


# Alias para compatibilidade
class BarberPrice(ProfessionalPrice):
    """Alias para compatibilidade - usar ProfessionalPrice no novo código"""
    __tablename__ = None
    __mapper_args__ = {
        'concrete': True
    }


class ChatConversation(db.Model):
    """Conversas de chat entre cliente e profissional"""
    __tablename__ = "chat_conversations"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False)
    profissional_id = db.Column(db.Integer, nullable=False)  # ID do profissional
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_unread = db.Column(db.Integer, default=0)
    profissional_unread = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos legados para compatibilidade
    barbeiro_id = db.Column(db.Integer)
    barbeiro_unread = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('cliente_id', 'profissional_id', name='unique_conversation'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "profissional_id": self.profissional_id or self.barbeiro_id,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "cliente_unread": self.cliente_unread,
            "profissional_unread": self.profissional_unread or self.barbeiro_unread,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Compatibilidade
            "barbeiro_id": self.profissional_id or self.barbeiro_id,
            "barbeiro_unread": self.profissional_unread or self.barbeiro_unread,
        }


class ChatMessage(db.Model):
    """Mensagens de chat"""
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id', ondelete='CASCADE'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # 'cliente' ou 'profissional' (ou 'barbeiro' para compatibilidade)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # Normaliza sender_type para 'profissional'
        sender_type_normalized = 'profissional' if self.sender_type == 'barbeiro' else self.sender_type
        
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_type": sender_type_normalized,
            "sender_tipo": sender_type_normalized,  # Alias para compatibilidade
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 



class Review(db.Model):
    """Avaliações de serviços"""
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    profissional_id = db.Column(db.Integer, nullable=False)
    appointment_id = db.Column(db.String(50), db.ForeignKey('appointments.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comentario = db.Column(db.Text)
    resposta = db.Column(db.Text)  # Resposta do profissional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "profissional_id": self.profissional_id,
            "appointment_id": self.appointment_id,
            "rating": self.rating,
            "comentario": self.comentario,
            "resposta": self.resposta,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Notification(db.Model):
    """Notificações do sistema"""
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'cliente' ou 'profissional'
    tipo = db.Column(db.String(50), nullable=False)  # 'appointment', 'review', 'message', 'reminder'
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(300))  # Link relacionado à notificação
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_type": self.user_type,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "mensagem": self.mensagem,
            "link": self.link,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class WorkingHours(db.Model):
    """Horários de trabalho dos profissionais"""
    __tablename__ = "working_hours"
    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Domingo, 1=Segunda, ..., 6=Sábado
    hora_inicio = db.Column(db.String(5), nullable=False)  # Formato: "09:00"
    hora_fim = db.Column(db.String(5), nullable=False)  # Formato: "18:00"
    intervalo_inicio = db.Column(db.String(5))  # Horário de início do intervalo
    intervalo_fim = db.Column(db.String(5))  # Horário de fim do intervalo
    ativo = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('profissional_id', 'dia_semana', name='_profissional_dia_uc'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "profissional_id": self.profissional_id,
            "dia_semana": self.dia_semana,
            "hora_inicio": self.hora_inicio,
            "hora_fim": self.hora_fim,
            "intervalo_inicio": self.intervalo_inicio,
            "intervalo_fim": self.intervalo_fim,
            "ativo": self.ativo
        }


class BlockedTime(db.Model):
    """Horários bloqueados (folgas, compromissos, etc)"""
    __tablename__ = "blocked_times"
    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(10), nullable=False)  # Formato: "2025-12-06"
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fim = db.Column(db.String(5), nullable=False)
    motivo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "profissional_id": self.profissional_id,
            "data": self.data,
            "hora_inicio": self.hora_inicio,
            "hora_fim": self.hora_fim,
            "motivo": self.motivo,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
