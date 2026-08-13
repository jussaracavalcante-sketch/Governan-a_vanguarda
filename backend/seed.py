"""Script de seed manual: cria tabelas, o admin inicial e os dados do HEAD de IA."""
from database import engine, Base, SessionLocal
from crud import seed_admin
from head.seed import seed_head_data
import head.models  # noqa: F401  (registra as tabelas do HEAD no metadata)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_head_data(db)
        print("Seed concluído: admin + dados do HEAD de IA.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
