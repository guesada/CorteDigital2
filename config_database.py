"""
Configuração do Banco de Dados
Configure aqui as credenciais do MySQL da escola
"""

# ===== CONFIGURAÇÃO MYSQL =====
# Edite estas variáveis com as credenciais da escola

MYSQL_CONFIG = {
    'user': 'root',           # Usuário MySQL
    'password': '',           # Senha MySQL (deixe vazio se não tiver)
    'host': 'localhost',      # Host MySQL
    'port': 3306,             # Porta MySQL
    'database': 'corte_digital'  # Nome do banco
}

# ===== MODO DE OPERAÇÃO =====
# 'mysql' - Usar MySQL (escola)
# 'sqlite' - Usar SQLite (desenvolvimento local)
# 'auto' - Detectar automaticamente (tenta MySQL, fallback para SQLite)

DATABASE_MODE = 'auto'

# ===== INSTRUÇÕES =====
"""
PARA USAR NA ESCOLA (MySQL):
1. Configure MYSQL_CONFIG com as credenciais da escola
2. Defina DATABASE_MODE = 'mysql'
3. Execute: python app.py

PARA USAR EM CASA (SQLite):
1. Defina DATABASE_MODE = 'sqlite'
2. Execute: python app.py

MODO AUTOMÁTICO (Recomendado):
1. Deixe DATABASE_MODE = 'auto'
2. O sistema tentará MySQL primeiro
3. Se falhar, usará SQLite automaticamente
"""
