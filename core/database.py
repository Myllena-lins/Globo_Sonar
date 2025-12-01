from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import ProgrammingError
import os

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "globo_sonar")
DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "apppass")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL_FALLBACK = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres"
engine_fallback = create_engine(DATABASE_URL_FALLBACK, isolation_level="AUTOCOMMIT")
conn = engine_fallback.connect()

try:
    conn.execute(text(f'CREATE DATABASE {DB_NAME}'))
except ProgrammingError:
    pass
finally:
    conn.close()
    engine_fallback.dispose()

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Session:
    """
    Cria uma sessão de banco de dados para ser usada como dependência no FastAPI.
    Exemplo:
        @app.get("/itens")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()