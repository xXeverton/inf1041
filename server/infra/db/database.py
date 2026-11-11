from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from infra.db.models import Base


DATABASE_DIR = Path(__file__).resolve().parents[2] / "database"
DATABASE_PATH = DATABASE_DIR / "db.sqlite3"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
Session = sessionmaker(bind=engine)


def criar_banco() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
