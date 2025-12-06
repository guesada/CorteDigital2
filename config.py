"""
Configurações da Aplicação - Groomly
Sistema profissional de agendamento para estúdios de beleza
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações base"""
    
    # Aplicação
    SECRET_KEY = os.getenv('SECRET_KEY', 'groomly_2025_secret_key_change_me')
    APP_NAME = 'Groomly'
    APP_VERSION = '2.0.0'
    
    # Servidor
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Banco de Dados
    DATABASE_URL = os.getenv('DATABASE_URL', 'root@localhost:3306@pjn%402024@CorteDigital')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Sessão
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5001', 'http://127.0.0.1:5001']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # SocketIO
    SOCKETIO_ASYNC_MODE = 'threading'  # 'gevent' em produção
    
    # Upload de arquivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Categorias de Profissionais
    PROFESSIONAL_CATEGORIES = [
        'Cabeleireiro',
        'Manicure',
        'Pedicure',
        'Esteticista',
        'Maquiador',
        'Barbeiro',
        'Depilador',
        'Massagista',
        'Designer de Sobrancelhas'
    ]
    
    # Categorias de Serviços
    SERVICE_CATEGORIES = [
        'Cabelo',
        'Unhas',
        'Estética Facial',
        'Estética Corporal',
        'Maquiagem',
        'Barba',
        'Depilação',
        'Massagem',
        'Sobrancelhas'
    ]
    
    # Status de Agendamento
    APPOINTMENT_STATUS = {
        'agendado': 'Agendado',
        'confirmado': 'Confirmado',
        'em_andamento': 'Em Andamento',
        'concluido': 'Concluído',
        'cancelado': 'Cancelado',
        'nao_compareceu': 'Não Compareceu'
    }
    
    # Configurações de Agendamento
    SLOT_DURATION = 30  # Duração padrão do slot em minutos
    MIN_ADVANCE_BOOKING = 60  # Mínimo de minutos de antecedência
    MAX_ADVANCE_BOOKING = 90  # Máximo de dias de antecedência
    CANCELLATION_DEADLINE = 120  # Prazo mínimo para cancelamento (minutos)
    
    # Notificações
    NOTIFICATION_TYPES = {
        'appointment': 'Agendamento',
        'review': 'Avaliação',
        'message': 'Mensagem',
        'reminder': 'Lembrete',
        'cancellation': 'Cancelamento',
        'confirmation': 'Confirmação'
    }
    
    # Email (opcional)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@beautystudio.com')
    
    # IA & ML
    AI_MIN_APPOINTMENTS = int(os.getenv('AI_MIN_APPOINTMENTS', 3))
    AI_CONFIDENCE_THRESHOLD = float(os.getenv('AI_CONFIDENCE_THRESHOLD', 0.7))
    
    # Validação
    EMAIL_VALIDATION_STRICT = os.getenv('EMAIL_VALIDATION_STRICT', 'true').lower() == 'true'
    PHONE_COUNTRY_CODE = os.getenv('PHONE_COUNTRY_CODE', 'BR')
    
    # Segurança
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION_MINUTES = int(os.getenv('LOCKOUT_DURATION_MINUTES', 30))
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Features
    FEATURE_AI_RECOMMENDATIONS = os.getenv('FEATURE_AI_RECOMMENDATIONS', 'true').lower() == 'true'
    FEATURE_CHAT = os.getenv('FEATURE_CHAT', 'true').lower() == 'true'
    FEATURE_NOTIFICATIONS = os.getenv('FEATURE_NOTIFICATIONS', 'true').lower() == 'true'
    FEATURE_REVIEWS = os.getenv('FEATURE_REVIEWS', 'true').lower() == 'true'
    FEATURE_ANALYTICS = os.getenv('FEATURE_ANALYTICS', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SOCKETIO_ASYNC_MODE = 'gevent'


class TestingConfig(Config):
    """Configurações de teste"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Mapeamento de configurações
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Retorna a configuração apropriada"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(config_name, DevelopmentConfig)
