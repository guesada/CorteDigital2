"""
Constantes da Aplicação - Groomly
"""

# Tipos de Usuário
USER_TYPE_CLIENT = 'cliente'
USER_TYPE_PROFESSIONAL = 'profissional'
USER_TYPE_ADMIN = 'admin'

# Status de Agendamento
STATUS_SCHEDULED = 'agendado'
STATUS_CONFIRMED = 'confirmado'
STATUS_IN_PROGRESS = 'em_andamento'
STATUS_COMPLETED = 'concluido'
STATUS_CANCELLED = 'cancelado'
STATUS_NO_SHOW = 'nao_compareceu'

APPOINTMENT_STATUSES = [
    STATUS_SCHEDULED,
    STATUS_CONFIRMED,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
    STATUS_NO_SHOW
]

# Categorias de Profissionais
CATEGORY_HAIRDRESSER = 'Cabeleireiro'
CATEGORY_MANICURE = 'Manicure'
CATEGORY_PEDICURE = 'Pedicure'
CATEGORY_ESTHETICIAN = 'Esteticista'
CATEGORY_MAKEUP_ARTIST = 'Maquiador'
CATEGORY_BARBER = 'Barbeiro'
CATEGORY_WAXING = 'Depilador'
CATEGORY_MASSAGE = 'Massagista'
CATEGORY_EYEBROW = 'Designer de Sobrancelhas'

PROFESSIONAL_CATEGORIES = [
    CATEGORY_HAIRDRESSER,
    CATEGORY_MANICURE,
    CATEGORY_PEDICURE,
    CATEGORY_ESTHETICIAN,
    CATEGORY_MAKEUP_ARTIST,
    CATEGORY_BARBER,
    CATEGORY_WAXING,
    CATEGORY_MASSAGE,
    CATEGORY_EYEBROW
]

# Categorias de Serviços
SERVICE_HAIR = 'Cabelo'
SERVICE_NAILS = 'Unhas'
SERVICE_FACIAL = 'Estética Facial'
SERVICE_BODY = 'Estética Corporal'
SERVICE_MAKEUP = 'Maquiagem'
SERVICE_BEARD = 'Barba'
SERVICE_WAXING = 'Depilação'
SERVICE_MASSAGE = 'Massagem'
SERVICE_EYEBROWS = 'Sobrancelhas'

SERVICE_CATEGORIES = [
    SERVICE_HAIR,
    SERVICE_NAILS,
    SERVICE_FACIAL,
    SERVICE_BODY,
    SERVICE_MAKEUP,
    SERVICE_BEARD,
    SERVICE_WAXING,
    SERVICE_MASSAGE,
    SERVICE_EYEBROWS
]

# Tipos de Notificação
NOTIFICATION_APPOINTMENT = 'appointment'
NOTIFICATION_REVIEW = 'review'
NOTIFICATION_MESSAGE = 'message'
NOTIFICATION_REMINDER = 'reminder'
NOTIFICATION_CANCELLATION = 'cancellation'
NOTIFICATION_CONFIRMATION = 'confirmation'

NOTIFICATION_TYPES = [
    NOTIFICATION_APPOINTMENT,
    NOTIFICATION_REVIEW,
    NOTIFICATION_MESSAGE,
    NOTIFICATION_REMINDER,
    NOTIFICATION_CANCELLATION,
    NOTIFICATION_CONFIRMATION
]

# Dias da Semana
WEEKDAYS = {
    0: 'Domingo',
    1: 'Segunda-feira',
    2: 'Terça-feira',
    3: 'Quarta-feira',
    4: 'Quinta-feira',
    5: 'Sexta-feira',
    6: 'Sábado'
}

# Mensagens de Erro
ERROR_UNAUTHORIZED = 'Não autorizado'
ERROR_NOT_FOUND = 'Não encontrado'
ERROR_INVALID_DATA = 'Dados inválidos'
ERROR_ALREADY_EXISTS = 'Já existe'
ERROR_INTERNAL_ERROR = 'Erro interno do servidor'

# Mensagens de Sucesso
SUCCESS_CREATED = 'Criado com sucesso'
SUCCESS_UPDATED = 'Atualizado com sucesso'
SUCCESS_DELETED = 'Deletado com sucesso'
SUCCESS_OPERATION = 'Operação realizada com sucesso'
