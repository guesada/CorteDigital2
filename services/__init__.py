"""
Services Package - Serviços da Aplicação
Re-exporta funções do services_legacy.py para compatibilidade
"""

# Re-exporta todas as funções do services_legacy
from services_legacy import *

# Importa novos serviços
from . import chat_service
from . import notification_service
from . import analytics_service
from . import review_service
