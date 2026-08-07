"""
VANGUARDIAN - Database Seed
"""
from database import engine, Base, SessionLocal
from crud import seed_initial_data

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
        print("Seed concluído com sucesso.")
        print("Admin: admin@vanguardian.com / admin123")
        print("Users: ana.souza@empresa.com / 123456")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
