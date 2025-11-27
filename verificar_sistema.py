"""
Script de Verificação do Sistema - Corte Digital
Verifica se tudo está configurado corretamente para a apresentação do TCC.

Uso:
    python verificar_sistema.py
"""

import sys
import os
import sqlite3

def verificar_python():
    """Verifica versão do Python."""
    print("🐍 Verificando Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Versão muito antiga!")
        print("   💡 Recomendado: Python 3.8 ou superior")
        return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas."""
    print("\n📦 Verificando dependências...")
    
    dependencias = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'werkzeug': 'Werkzeug'
    }
    
    todas_ok = True
    
    for modulo, nome in dependencias.items():
        try:
            __import__(modulo)
            print(f"   ✅ {nome} - Instalado")
        except ImportError:
            print(f"   ❌ {nome} - NÃO instalado")
            todas_ok = False
    
    if not todas_ok:
        print("\n   💡 Para instalar as dependências, execute:")
        print("      pip install -r requirements.txt")
    
    return todas_ok

def verificar_banco_dados():
    """Verifica se o banco de dados existe e está populado."""
    print("\n💾 Verificando banco de dados...")
    
    db_file = "corte_digital.db"
    
    if not os.path.exists(db_file):
        print(f"   ❌ Banco de dados '{db_file}' não encontrado!")
        print("\n   💡 Para criar o banco de dados, execute:")
        print("      python setup_database.py")
        return False
    
    print(f"   ✅ Arquivo '{db_file}' encontrado")
    
    # Verificar conteúdo
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        tabelas_esperadas = ['users', 'services', 'appointments', 'inventory', 'notifications']
        
        print("\n   📋 Tabelas encontradas:")
        for tabela in tabelas_esperadas:
            if tabela in tabelas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"      ✅ {tabela}: {count} registros")
            else:
                print(f"      ❌ {tabela}: NÃO encontrada")
        
        # Verificar se há dados
        cursor.execute("SELECT COUNT(*) FROM users WHERE tipo = 'barbeiro'")
        barbeiros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE tipo = 'cliente'")
        clientes = cursor.fetchone()[0]
        
        if barbeiros == 0 or clientes == 0:
            print("\n   ⚠️  Banco de dados vazio ou incompleto!")
            print("   💡 Execute o setup novamente:")
            print("      python setup_database.py")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco: {e}")
        return False

def verificar_arquivos():
    """Verifica se os arquivos principais existem."""
    print("\n📁 Verificando arquivos do projeto...")
    
    arquivos_criticos = [
        'app.py',
        'db.py',
        'services.py',
        'requirements.txt',
        'templates/index.html',
        'templates/cliente_dashboard.html',
        'templates/barbeiro_dashboard.html',
    ]
    
    todos_ok = True
    
    for arquivo in arquivos_criticos:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - NÃO encontrado")
            todos_ok = False
    
    return todos_ok

def verificar_portas():
    """Verifica se a porta 5001 está disponível."""
    print("\n🔌 Verificando porta 5001...")
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        
        if result == 0:
            print("   ⚠️  Porta 5001 já está em uso!")
            print("   💡 Feche a aplicação que está usando a porta ou mude a porta no app.py")
            return False
        else:
            print("   ✅ Porta 5001 disponível")
            return True
    except Exception as e:
        print(f"   ⚠️  Não foi possível verificar a porta: {e}")
        return True

def exibir_credenciais():
    """Exibe as credenciais de acesso."""
    print("\n" + "=" * 60)
    print("🔐 CREDENCIAIS PARA TESTE")
    print("=" * 60)
    
    print("\n👨‍💼 BARBEIRO:")
    print("   Email: miguel@cortedigital.com")
    print("   Senha: senha123")
    
    print("\n👤 CLIENTE:")
    print("   Email: carlos@email.com")
    print("   Senha: senha123")
    
    print("\n" + "=" * 60)

def main():
    """Função principal."""
    print("\n" + "=" * 60)
    print("🔍 VERIFICAÇÃO DO SISTEMA - CORTE DIGITAL")
    print("=" * 60)
    
    resultados = []
    
    # Executar verificações
    resultados.append(("Python", verificar_python()))
    resultados.append(("Dependências", verificar_dependencias()))
    resultados.append(("Banco de Dados", verificar_banco_dados()))
    resultados.append(("Arquivos", verificar_arquivos()))
    resultados.append(("Porta", verificar_portas()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    tudo_ok = True
    for nome, resultado in resultados:
        status = "✅ OK" if resultado else "❌ ERRO"
        print(f"   {nome}: {status}")
        if not resultado:
            tudo_ok = False
    
    print("\n" + "=" * 60)
    
    if tudo_ok:
        print("✅ SISTEMA PRONTO PARA USO!")
        print("\n💡 Para iniciar a aplicação, execute:")
        print("   python app.py")
        print("\n🌐 Acesse: http://127.0.0.1:5001")
        exibir_credenciais()
    else:
        print("❌ SISTEMA COM PROBLEMAS!")
        print("\n💡 Corrija os erros acima antes de iniciar a aplicação.")
    
    print()

if __name__ == "__main__":
    main()
