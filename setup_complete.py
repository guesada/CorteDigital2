"""
Script completo de setup do banco de dados.
Cria todas as tabelas e popula com dados de exemplo.
Execute este script em qualquer máquina para configurar o sistema.
"""

from app import app
from db import db, Cliente, Barber, Service, Appointment, BarberPrice, Statistic
from datetime import datetime, timedelta
import random

def create_tables():
    """Criar todas as tabelas do banco de dados."""
    print("📋 Criando tabelas do banco de dados...")
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")

def create_services():
    """Criar serviços padrão."""
    print("\n🔧 Criando serviços...")
    
    services_data = [
        {"nome": "Corte", "preco": 35.00, "duracao": 30, "descricao": "Corte de cabelo masculino"},
        {"nome": "Barba", "preco": 25.00, "duracao": 20, "descricao": "Aparar e modelar barba"},
        {"nome": "Corte + Barba", "preco": 55.00, "duracao": 50, "descricao": "Combo completo"}
    ]
    
    for service_data in services_data:
        existing = Service.query.filter_by(nome=service_data["nome"]).first()
        if not existing:
            service = Service(**service_data)
            db.session.add(service)
            print(f"  ✓ Serviço criado: {service_data['nome']}")
    
    db.session.commit()

def create_barbers():
    """Criar barbeiros de exemplo."""
    print("\n💈 Criando barbeiros...")
    
    barbers_data = [
        {
            "nome": "João Silva",
            "email": "joao@barbershop.com",
            "senha": "senha123",
            "telefone": "(11) 98765-4321",
            "especialidades": '["Corte Clássico", "Degradê", "Barba"]',
            "avaliacao": 4.8,
            "preco_base": 35.00,
            "disponibilidade": '["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]'
        },
        {
            "nome": "Pedro Santos",
            "email": "pedro@barbershop.com",
            "senha": "senha123",
            "telefone": "(11) 98765-4322",
            "especialidades": '["Corte Moderno", "Fade", "Desenhos"]',
            "avaliacao": 4.9,
            "preco_base": 40.00,
            "disponibilidade": '["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]'
        },
        {
            "nome": "Carlos Oliveira",
            "email": "carlos@barbershop.com",
            "senha": "senha123",
            "telefone": "(11) 98765-4323",
            "especialidades": '["Corte Social", "Barba", "Tratamentos"]',
            "avaliacao": 4.7,
            "preco_base": 35.00,
            "disponibilidade": '["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00", "18:00"]'
        }
    ]
    
    created_barbers = []
    for barber_data in barbers_data:
        existing = Barber.query.filter_by(email=barber_data["email"]).first()
        if not existing:
            barber = Barber(**barber_data)
            db.session.add(barber)
            created_barbers.append(barber)
            print(f"  ✓ Barbeiro criado: {barber_data['nome']}")
        else:
            created_barbers.append(existing)
    
    db.session.commit()
    return created_barbers

def create_barber_prices(barbers):
    """Criar preços personalizados para cada barbeiro."""
    print("\n💰 Criando preços personalizados...")
    
    prices_config = [
        {"Corte": 35.00, "Barba": 25.00, "Corte + Barba": 55.00},  # João
        {"Corte": 40.00, "Barba": 30.00, "Corte + Barba": 65.00},  # Pedro (mais caro)
        {"Corte": 35.00, "Barba": 25.00, "Corte + Barba": 55.00}   # Carlos
    ]
    
    for i, barber in enumerate(barbers):
        if i < len(prices_config):
            for servico_nome, preco in prices_config[i].items():
                existing = BarberPrice.query.filter_by(
                    barbeiro_id=barber.id,
                    servico_nome=servico_nome
                ).first()
                
                if not existing:
                    price = BarberPrice(
                        barbeiro_id=barber.id,
                        servico_nome=servico_nome,
                        preco=preco
                    )
                    db.session.add(price)
            print(f"  ✓ Preços definidos para: {barber.nome}")
    
    db.session.commit()

def create_clients():
    """Criar clientes de exemplo."""
    print("\n👥 Criando clientes...")
    
    clients_data = [
        {
            "nome": "Maria Santos",
            "email": "maria@email.com",
            "senha": "senha123",
            "telefone": "(11) 91234-5678"
        },
        {
            "nome": "José Silva",
            "email": "jose@email.com",
            "senha": "senha123",
            "telefone": "(11) 91234-5679"
        },
        {
            "nome": "Ana Costa",
            "email": "ana@email.com",
            "senha": "senha123",
            "telefone": "(11) 91234-5680"
        },
        {
            "nome": "Paulo Souza",
            "email": "paulo@email.com",
            "senha": "senha123",
            "telefone": "(11) 91234-5681"
        }
    ]
    
    created_clients = []
    for client_data in clients_data:
        existing = Cliente.query.filter_by(email=client_data["email"]).first()
        if not existing:
            client = Cliente(**client_data)
            db.session.add(client)
            created_clients.append(client)
            print(f"  ✓ Cliente criado: {client_data['nome']}")
        else:
            created_clients.append(existing)
    
    db.session.commit()
    return created_clients

def create_sample_appointments(barbers, clients):
    """Criar agendamentos de exemplo."""
    print("\n📅 Criando agendamentos de exemplo...")
    
    services = Service.query.all()
    if not services:
        print("  ⚠️ Nenhum serviço encontrado. Pulando agendamentos.")
        return []
    
    statuses = ['concluido', 'agendado', 'confirmado']
    created_appointments = []
    
    # Criar agendamentos dos últimos 30 dias
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 2-4 agendamentos por dia
        num_appointments = random.randint(2, 4)
        
        for _ in range(num_appointments):
            barber = random.choice(barbers)
            client = random.choice(clients)
            service = random.choice(services)
            
            # Horários disponíveis
            times = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
            time = random.choice(times)
            
            # Status (mais concluídos no passado, mais agendados no futuro)
            if i > 7:  # Passado
                status = 'concluido'
            elif i > 0:  # Passado recente
                status = random.choice(['concluido', 'concluido', 'cancelado'])
            else:  # Hoje
                status = random.choice(['agendado', 'confirmado'])
            
            # Buscar preço personalizado do barbeiro
            barber_price = BarberPrice.query.filter_by(
                barbeiro_id=barber.id,
                servico_nome=service.nome
            ).first()
            
            price = barber_price.preco if barber_price else service.preco
            
            appointment_id = f"APT{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            # Verificar se já existe
            existing = Appointment.query.get(appointment_id)
            if existing:
                continue
            
            appointment = Appointment(
                id=appointment_id,
                cliente=client.nome,
                cliente_email=client.email,
                barbeiro=barber.nome,
                barbeiro_id=barber.id,
                servico=service.nome,
                servico_id=service.id,
                date=date,
                time=time,
                status=status,
                total_price=price,
                created_at=datetime.now().isoformat()
            )
            
            db.session.add(appointment)
            created_appointments.append(appointment)
    
    db.session.commit()
    print(f"  ✓ {len(created_appointments)} agendamentos criados")
    return created_appointments

def main():
    """Executar setup completo."""
    print("=" * 60)
    print("🚀 SETUP COMPLETO DO BANCO DE DADOS - CORTE DIGITAL")
    print("=" * 60)
    
    with app.app_context():
        try:
            # 1. Criar tabelas
            create_tables()
            
            # 2. Criar serviços
            create_services()
            
            # 3. Criar barbeiros
            barbers = create_barbers()
            
            # 4. Criar preços personalizados
            create_barber_prices(barbers)
            
            # 5. Criar clientes
            clients = create_clients()
            
            # 6. Criar agendamentos
            appointments = create_sample_appointments(barbers, clients)
            
            print("\n" + "=" * 60)
            print("✅ SETUP CONCLUÍDO COM SUCESSO!")
            print("=" * 60)
            print("\n📊 Resumo:")
            print(f"  • Barbeiros: {len(barbers)}")
            print(f"  • Clientes: {len(clients)}")
            print(f"  • Serviços: {Service.query.count()}")
            print(f"  • Agendamentos: {len(appointments)}")
            print("\n🔐 Credenciais de acesso:")
            print("\n  BARBEIROS:")
            print("    Email: joao@barbershop.com | Senha: senha123")
            print("    Email: pedro@barbershop.com | Senha: senha123")
            print("    Email: carlos@barbershop.com | Senha: senha123")
            print("\n  CLIENTES:")
            print("    Email: maria@email.com | Senha: senha123")
            print("    Email: jose@email.com | Senha: senha123")
            print("    Email: ana@email.com | Senha: senha123")
            print("    Email: paulo@email.com | Senha: senha123")
            print("\n🎯 Execute 'python app.py' para iniciar o servidor!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Erro durante o setup: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
