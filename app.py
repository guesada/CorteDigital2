from flask import Flask, jsonify
from flask_cors import CORS
import os

from routes import register_routes
from db import db

app = Flask(__name__)

# Configurar CORS para permitir credenciais (cookies de sessão)
CORS(app, supports_credentials=True, origins=["http://localhost:5001", "http://127.0.0.1:5001"])

app.secret_key = "corte_digital_2025_secret_key"
app.config["JSON_SORT_KEYS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# ===== CONFIGURAÇÃO DO BANCO DE DADOS =====
def configure_database():
    """Configura o banco de dados baseado no ambiente"""
    
    try:
        from config.config_database import MYSQL_CONFIG, DATABASE_MODE
    except ImportError:
        # Se não existir config, usar modo auto
        MYSQL_CONFIG = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': 3306,
            'database': 'corte_digital'
        }
        DATABASE_MODE = 'auto'
    
    # Verificar variável de ambiente primeiro
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        # Usar URL fornecida por variável de ambiente
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        print(f"📊 Usando banco de dados da variável de ambiente")
        
    elif DATABASE_MODE == 'sqlite':
        # Forçar SQLite
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'corte_digital.db')
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        print(f"📊 Modo SQLite: {db_path}")
        
    elif DATABASE_MODE == 'mysql':
        # Forçar MySQL
        try:
            import pymysql
            
            # Testar conexão e criar banco
            connection = pymysql.connect(
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password'],
                host=MYSQL_CONFIG['host'],
                port=MYSQL_CONFIG['port']
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Banco '{MYSQL_CONFIG['database']}' criado/verificado no MySQL")
            cursor.close()
            connection.close()
            
            # Configurar SQLAlchemy
            mysql_url = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
            app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
            print(f"📊 Modo MySQL: {MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
            
        except Exception as e:
            print(f"❌ Erro ao conectar MySQL: {e}")
            print(f"💡 Verifique as credenciais em config_database.py")
            raise
            
    else:  # auto
        # Tentar MySQL primeiro, fallback para SQLite
        try:
            import pymysql
            
            # Testar conexão MySQL
            connection = pymysql.connect(
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password'],
                host=MYSQL_CONFIG['host'],
                port=MYSQL_CONFIG['port']
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Banco '{MYSQL_CONFIG['database']}' criado/verificado no MySQL")
            cursor.close()
            connection.close()
            
            # Configurar SQLAlchemy para MySQL
            mysql_url = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
            app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
            print(f"📊 Modo Auto: Usando MySQL - {MYSQL_CONFIG['user']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
            
        except Exception as e:
            # Fallback para SQLite
            print(f"⚠️  MySQL não disponível, usando SQLite local")
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'corte_digital.db')
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
            print(f"📊 Modo Auto: Usando SQLite - {db_path}")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configurar banco de dados
configure_database()

# Inicializar banco de dados
db.init_app(app)

# Criar tabelas e popular com dados de exemplo se necessário
with app.app_context():
    from database.init_database import init_database_with_sample_data
    init_database_with_sample_data(app, db)

register_routes(app)


@app.errorhandler(404)
def handler_404(_):
    return jsonify({"success": False, "message": "Rota não encontrada"}), 404


@app.errorhandler(500)
def handler_500(erro):
    return jsonify({"success": False, "message": str(erro)}), 500


@app.errorhandler(Exception)
def handler_exception(erro):
    """Captura todos os erros não tratados."""
    import traceback
    traceback.print_exc()
    return jsonify({"success": False, "message": str(erro)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
