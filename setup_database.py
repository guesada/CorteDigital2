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
    
    # Tabela de Estoque/Inventário
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0.0,
            barbeiro_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (barbeiro_id) REFERENCES users(id)
        )
    """)
    print("  ✓ Tabela 'inventory' criada")
    
    # Tabela de Notificações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            data TEXT,
            read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("  ✓ Tabela 'notifications' criada")
    
    conn.commit()
    print("✅ Todas as tabelas criadas com sucesso!\n")

def inserir_dados_demonstracao(conn):
    """Insere dados de demonstração no banco."""
    cursor = conn.cursor()
    
    print("📦 Inserindo dados de demonstração...\n")
    
    # 1. Usuários (Barbeiros e Clientes)
    print("👥 Inserindo usuários...")
    usuarios = [
        # Barbeiros
        ("Miguel Silva", "miguel@cortedigital.com", "senha123", "barbeiro", "(11) 98765-4321"),
        ("João Santos", "joao@cortedigital.com", "senha123", "barbeiro", "(11) 98765-4322"),
        ("Pedro Costa", "pedro@cortedigital.com", "senha123", "barbeiro", "(11) 98765-4323"),
        
        # Clientes
        ("Carlos Oliveira", "carlos@email.com", "senha123", "cliente", "(11) 91234-5678"),
        ("Ana Paula", "ana@email.com", "senha123", "cliente", "(11) 91234-5679"),
        ("Roberto Lima", "roberto@email.com", "senha123", "cliente", "(11) 91234-5680"),
        ("Fernanda Costa", "fernanda@email.com", "senha123", "cliente", "(11) 91234-5681"),
        ("Lucas Martins", "lucas@email.com", "senha123", "cliente", "(11) 91234-5682"),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO users (name, email, password, tipo, telefone)
        VALUES (?, ?, ?, ?, ?)
    """, usuarios)
    print(f"  ✓ {len(usuarios)} usuários inseridos")
    
    # 2. Serviços
    print("✂️  Inserindo serviços...")
    servicos = [
        ("Corte Simples", "Corte de cabelo tradicional", 35.00, 30),
        ("Corte + Barba", "Corte de cabelo + barba completa", 55.00, 45),
        ("Barba", "Aparar e modelar barba", 25.00, 20),
        ("Corte Degradê", "Corte degradê moderno", 45.00, 40),
        ("Sobrancelha", "Design de sobrancelha", 15.00, 15),
        ("Hidratação Capilar", "Tratamento de hidratação", 40.00, 30),
        ("Platinado", "Descoloração completa", 120.00, 120),
        ("Luzes", "Mechas e luzes", 80.00, 90),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO services (name, description, price, duration)
        VALUES (?, ?, ?, ?)
    """, servicos)
    print(f"  ✓ {len(servicos)} serviços inseridos")
    
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
    
    # 4. Itens de Estoque
    print("📦 Inserindo itens de estoque...")
    estoque = [
        ("Shampoo Profissional", 15, 25.00, barbeiros[0][0]),
        ("Condicionador", 12, 22.00, barbeiros[0][0]),
        ("Pomada Modeladora", 8, 35.00, barbeiros[0][0]),
        ("Cera para Cabelo", 10, 30.00, barbeiros[0][0]),
        ("Gel Fixador", 20, 18.00, barbeiros[0][0]),
        ("Óleo para Barba", 6, 45.00, barbeiros[0][0]),
        ("Navalha Descartável", 50, 2.50, barbeiros[0][0]),
        ("Toalha", 30, 15.00, barbeiros[0][0]),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO inventory (name, quantity, price, barbeiro_id)
        VALUES (?, ?, ?, ?)
    """, estoque)
    print(f"  ✓ {len(estoque)} itens de estoque inseridos")
    
    conn.commit()
    print("\n✅ Dados de demonstração inseridos com sucesso!\n")

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
    
    cursor.execute("SELECT COUNT(*) FROM inventory")
    estoque = cursor.fetchone()[0]
    
    print(f"\n👥 Usuários:")
    print(f"   • Barbeiros: {barbeiros}")
    print(f"   • Clientes: {clientes}")
    print(f"\n✂️  Serviços: {servicos}")
    print(f"📅 Agendamentos: {agendamentos}")
    print(f"📦 Itens de Estoque: {estoque}")
    
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
