from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from app.models.base import Base
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = "sqlite:///academic_management.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create database tables from models."""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    logging.info("Sessão do banco de dados aberta.")
    try:
        yield db
    except Exception as e:
        logging.error(f"Erro na sessão do banco de dados. Realizando rollback. Erro: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        logging.info("Sessão do banco de dados fechada.")
        db.close()
