# Importações necessárias do Flask e extensões
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# Importa o registro de rotas e serviços da aplicação
from routes import register_routes
from routes.chat import register_chat_routes, register_socketio_events
import services
import chat_service

# Cria a instância principal da aplicação Flask
app = Flask(__name__)

# Configurar CORS para permitir credenciais (cookies de sessão)
# Permite requisições de localhost e 127.0.0.1 na porta 5001
CORS(app, supports_credentials=True, origins=["http://localhost:5001", "http://127.0.0.1:5001"])

# Inicializa SocketIO para comunicação em tempo real
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5001", "http://127.0.0.1:5001"], 
                    manage_session=False, async_mode='eventlet')

# Chave secreta para criptografia de sessões e cookies
app.secret_key = "corte_digital_2025_secret_key"

# Configurações da aplicação
app.config["JSON_SORT_KEYS"] = False  # Mantém a ordem original das chaves JSON nas respostas
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Proteção contra CSRF, permite cookies em navegação normal
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Impede acesso aos cookies via JavaScript (segurança XSS)

# Inicializa a conexão com o banco de dados e carrega dados iniciais
services.init_app(app)

# Cria tabelas do chat
try:
    chat_service.create_chat_tables()
except Exception as e:
    print(f"Aviso ao criar tabelas de chat: {e}")

# Registra todas as rotas da aplicação (endpoints)
register_routes(app)
register_chat_routes(app)

# Registra eventos WebSocket
register_socketio_events(socketio)


@app.before_request
def auto_complete_appointments():
    """
    Middleware executado antes de cada requisição HTTP.
    Verifica e marca automaticamente como concluídos os agendamentos
    que já passaram da data/hora agendada.
    """
    try:
        services.auto_complete_past_appointments()
    except Exception as e:
        # Não bloqueia a requisição se houver erro na verificação automática
        print(f"Erro ao auto-completar agendamentos: {e}")


@app.errorhandler(404)
def handler_404(_):
    """
    Manipulador de erro 404 - Rota não encontrada.
    Retorna uma resposta JSON padronizada quando o endpoint não existe.
    """
    return jsonify({"success": False, "message": "Rota não encontrada"}), 404


@app.errorhandler(500)
def handler_500(erro):
    """
    Manipulador de erro 500 - Erro interno do servidor.
    Retorna uma resposta JSON com a mensagem do erro.
    """
    return jsonify({"success": False, "message": str(erro)}), 500


@app.errorhandler(Exception)
def handler_exception(erro):
    """
    Manipulador genérico de exceções.
    Captura todos os erros não tratados, imprime o traceback completo
    no console e retorna uma resposta JSON com a mensagem de erro.
    """
    import traceback
    traceback.print_exc()  # Imprime o stack trace completo no console para debug
    return jsonify({"success": False, "message": str(erro)}), 500


if __name__ == "__main__":
    # Inicia o servidor Flask com SocketIO em modo de desenvolvimento
    # host: 127.0.0.1 (localhost) - apenas conexões locais
    # port: 5001 - porta do servidor
    # debug: True - ativa modo debug com reload automático e mensagens detalhadas
    socketio.run(app, host="127.0.0.1", port=5001, debug=True, allow_unsafe_werkzeug=True)
