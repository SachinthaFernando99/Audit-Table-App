import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_continuum import make_versioned
from util.logger import logger

# ---------------- Database Setup ----------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(CURRENT_DIR)

db_folder = os.path.join(BASE_DIR, "db")
if not os.path.exists(db_folder):
    os.makedirs(db_folder)
    logger.info(f"Created database directory at: {db_folder}")
else:
    logger.info(f"Database directory already exists at: {db_folder}")

DATABASE_URL = f"sqlite:///{os.path.join(db_folder, 'transactions.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ---------------- Versioning Setup ----------------
# Enable versioning BEFORE model definitions
make_versioned(user_cls=None)
logger.info("Enabled SQLAlchemy-Continuum versioning")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed.")

