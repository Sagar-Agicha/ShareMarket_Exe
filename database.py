import logging
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("backend.database")

if getattr(sys, "frozen", False):
    DB_DIR = Path(sys.executable).resolve().parent
else:
    DB_DIR = Path(__file__).resolve().parent

DEFAULT_DB_PATH = (DB_DIR / "users.db").as_posix()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def _ensure_task_columns_exist() -> None:
    inspector = inspect(engine)
    if "tasks" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("tasks")}
    with engine.begin() as conn:
        if "output_folder" not in columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN output_folder VARCHAR"))
            logger.info("Added missing column output_folder to tasks table")
        if "output_filename" not in columns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN output_filename VARCHAR"))
            logger.info("Added missing column output_filename to tasks table")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_task_columns_exist()
    logger.info("SQLite database initialized at %s", SQLALCHEMY_DATABASE_URL)
