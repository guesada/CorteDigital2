"""
Script de Inicialização do Banco de Dados - Corte Digital
TCC - Sistema de Agendamento para Barbearias

Este script cria o banco de dados SQLite e popula com dados de demonstração.
Execute este script antes de iniciar a aplicação pela primeira vez.

Uso:
    python setup_database.py
"""

import sqlite3
from datetime import datetime, timedelta
import os

# Configurações
DB_FILE = "corte_digital.db"
BACKUP_DIR = "backups"

def criar_backup():
    """Cria backup do banco de dados existente."""
    if os.path.exists(DB_FILE):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"corte_digital_backup_{timestamp}.db")
        
        import shutil
        shutil.copy2(DB_FILE, backup_file)
        print(f"✅ Backup criado: {backup_file}")
        return True
    return False

def criar_tabelas(conn):
    """Cria todas as tabelas do banco de dados."""
    cursor = conn.cursor()
    
    print("📋 Criando tabelas...")
    
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('cliente', 'barbeiro')),
            telefone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Tabela 'users' criada")
    
    # Tabela de Serviços
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            duration INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ Tabela 'services' criada")
    
    # Tabela de Agendamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            cliente TEXT NOT NULL,
            cliente_email TEXT NOT NULL,
            barbeiro TEXT NOT NULL,
            barbeiro_id INTEGER NOT NULL,
            servico TEXT NOT NULL,
            servico_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'agendado' CHECK(status IN ('agendado', 'confirmado', 'concluido', 'cancelado', 'pendente')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_email) REFERENCES users(email),
            FOREIGN KEY (barbeiro_id) REFERENCES users(id),
            FOREIGN KEY (servico_id) REFERENCES services(id)
        )
    """)
    print("  ✓ Tabela 'appointments' criada")
    
    # Tabela de Preços Personalizados por Barbeiro
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barber_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barbeiro_id INTEGER NOT NULL,
            servico_nome TEXT NOT NULL,
            preco REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (barbeiro_id) REFERENCES users(id),
            UNIQUE(barbeiro_id, servico_nome)
        )
    """)
    print("  ✓ Tabela 'barber_prices' criada")
    
    conn.commit()
    print("✅ Todas as tabelas criadas com sucesso!\n")



    
    # 2.1. Preços Personalizados dos Barbeiros
    print("💰 Inserindo preços dos barbeiros...")
    
    # Obter IDs dos barbeiros
    cursor.execute("SELECT id, name FROM users WHERE tipo = 'barbeiro'")
    barbeiros_ids = cursor.fetchall()
    
    # Preços padrão para cada barbeiro (podem ser diferentes)
    precos_barbeiros = []
    for barbeiro_id, barbeiro_nome in barbeiros_ids:
        if "Miguel" in barbeiro_nome:
            # Miguel - preços padrão
            precos_barbeiros.extend([
                (barbeiro_id, "Corte", 35.00),
                (barbeiro_id, "Corte + Barba", 55.00),
                (barbeiro_id, "Barba", 25.00),
            ])
        elif "João" in barbeiro_nome:
            # João - preços um pouco mais altos
            precos_barbeiros.extend([
                (barbeiro_id, "Corte", 40.00),
                (barbeiro_id, "Corte + Barba", 60.00),
                (barbeiro_id, "Barba", 28.00),
            ])
        else:
            # Pedro - preços mais baixos
            precos_barbeiros.extend([
                (barbeiro_id, "Corte", 30.00),
                (barbeiro_id, "Corte + Barba", 50.00),
                (barbeiro_id, "Barba", 22.00),
            ])
    
    cursor.executemany("""
        INSERT OR IGNORE INTO barber_prices (barbeiro_id, servico_nome, preco)
        VALUES (?, ?, ?)
    """, precos_barbeiros)
    print(f"  ✓ {len(precos_barbeiros)} preços de barbeiros inseridos")
    
    # 3. Agendamentos de Demonstração
    print("📅 Inserindo agendamentos...")
    
    # Obter IDs dos barbeiros
    cursor.execute("SELECT id, name FROM users WHERE tipo = 'barbeiro'")
    barbeiros = cursor.fetchall()
    
    # Obter IDs dos serviços
    cursor.execute("SELECT id, name, price FROM services")
    servicos_db = cursor.fetchall()
    
    # Criar agendamentos para os próximos dias
    hoje = datetime.now().date()
    agendamentos = []
    apt_counter = 1
    
    # Agendamentos passados (últimos 3 dias)
    for dias_atras in range(3, 0, -1):
        data = (hoje - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        
        # 2 agendamentos por dia
        agendamentos.append((
            f"APT{apt_counter:05d}",
            "Carlos Oliveira",
            "carlos@email.com",
            barbeiros[0][1],  # Miguel
            barbeiros[0][0],
            servicos_db[0][1],  # Corte Simples
            servicos_db[0][0],
            data,
            "09:00",
            servicos_db[0][2],
            "concluido"
        ))
        apt_counter += 1
        
        agendamentos.append((
            f"APT{apt_counter:05d}",
            "Ana Paula",
            "ana@email.com",
            barbeiros[0][1],  # Miguel
            barbeiros[0][0],
            servicos_db[1][1],  # Corte + Barba
            servicos_db[1][0],
            data,
            "14:00",
            servicos_db[1][2],
            "concluido"
        ))
        apt_counter += 1
    
    # Agendamentos futuros (próximos 7 dias)
    for dias_frente in range(1, 8):
        data = (hoje + timedelta(days=dias_frente)).strftime("%Y-%m-%d")
        
        # Distribuir entre barbeiros
        barbeiro_idx = (dias_frente - 1) % len(barbeiros)
        servico_idx = (dias_frente - 1) % len(servicos_db)
        
        # 3 agendamentos por dia
        horarios = ["10:00", "14:00", "16:30"]
        clientes = [
            ("Roberto Lima", "roberto@email.com"),
            ("Fernanda Costa", "fernanda@email.com"),
            ("Lucas Martins", "lucas@email.com")
        ]
        
        for i, horario in enumerate(horarios):
            cliente_idx = i % len(clientes)
            status = "confirmado" if i == 0 else "agendado"
            
            agendamentos.append((
                f"APT{apt_counter:05d}",
                clientes[cliente_idx][0],
                clientes[cliente_idx][1],
                barbeiros[barbeiro_idx][1],
                barbeiros[barbeiro_idx][0],
                servicos_db[servico_idx][1],
                servicos_db[servico_idx][0],
                data,
                horario,
                servicos_db[servico_idx][2],
                status
            ))
            apt_counter += 1
    
    cursor.executemany("""
        INSERT OR IGNORE INTO appointments 
        (id, cliente, cliente_email, barbeiro, barbeiro_id, servico, servico_id, date, time, total_price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, agendamentos)
    print(f"  ✓ {len(agendamentos)} agendamentos inseridos")


def exibir_resumo(conn):
    """Exibe resumo dos dados no banco."""
    cursor = conn.cursor()
    
    print("=" * 60)
    print("📊 RESUMO DO BANCO DE DADOS")
    print("=" * 60)
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM users WHERE tipo = 'barbeiro'")
    barbeiros = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE tipo = 'cliente'")
    clientes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM services")
    servicos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM appointments")
    agendamentos = cursor.fetchone()[0]
    
    
    print(f"\n👥 Usuários:")
    print(f"   • Barbeiros: {barbeiros}")
    print(f"   • Clientes: {clientes}")
    print(f"\n✂️  Serviços: {servicos}")
    print(f"📅 Agendamentos: {agendamentos}")
    
    print("\n" + "=" * 60)
    print("🔐 CREDENCIAIS DE ACESSO")
    print("=" * 60)
    
    print("\n👨‍💼 BARBEIROS:")
    cursor.execute("SELECT name, email FROM users WHERE tipo = 'barbeiro'")
    for nome, email in cursor.fetchall():
        print(f"   • {nome}")
        print(f"     Email: {email}")
        print(f"     Senha: senha123")
        print()
    
    print("👤 CLIENTES:")
    cursor.execute("SELECT name, email FROM users WHERE tipo = 'cliente' LIMIT 3")
    for nome, email in cursor.fetchall():
        print(f"   • {nome}")
        print(f"     Email: {email}")
        print(f"     Senha: senha123")
        print()
    
    print("=" * 60)
    print()

def main():
    """Função principal."""
    print("\n" + "=" * 60)
    print("🚀 SETUP DO BANCO DE DADOS - CORTE DIGITAL")
    print("=" * 60)
    print()
    
    # Verificar se já existe banco
    if os.path.exists(DB_FILE):
        print(f"⚠️  Banco de dados '{DB_FILE}' já existe!")
        resposta = input("Deseja recriar o banco? (s/N): ").strip().lower()
        
        if resposta != 's':
            print("❌ Operação cancelada.")
            return
        
        # Criar backup
        criar_backup()
        
        # Remover banco antigo
        os.remove(DB_FILE)
        print(f"🗑️  Banco antigo removido\n")
    
    # Criar conexão
    print(f"📁 Criando banco de dados: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    
    try:
        # Criar estrutura
        criar_tabelas(conn)
        
        # Inserir dados
        inserir_dados_demonstracao(conn)
        
        # Exibir resumo
        exibir_resumo(conn)
        
        print("✅ Setup concluído com sucesso!")
        print("\n💡 Para iniciar a aplicação, execute:")
        print("   python app.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Erro durante o setup: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
