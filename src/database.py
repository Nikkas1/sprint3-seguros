import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define o caminho do banco de dados (na pasta data)
DATABASE_DIR = "data"
DATABASE_URL = os.path.join(DATABASE_DIR, "seguro.db")

# Garante que o diretório exista
os.makedirs(DATABASE_DIR, exist_ok=True)

# Configuração do SQLAlchemy
engine = create_engine(
    f"sqlite:///{DATABASE_URL}", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_schema():
    """Cria todas as tabelas definidas nos modelos, se não existirem."""
    from .models import Base as SchemaBase

    SchemaBase.metadata.create_all(bind=engine)


def get_db():
    """Gera uma sessão de banco de dados e garante que ela seja fechada."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
