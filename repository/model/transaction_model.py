from sqlalchemy import Column, Integer, String, Float, Date, Time
from sqlalchemy.orm import configure_mappers
from util.logger import logger
from util.database import Base, engine  # Import Base and engine from database.py

class TransactionModel(Base):
    """
    Represents a transaction record.
    Versioned with SQLAlchemy-Continuum for audit history.
    """
    __tablename__ = 'transactions'
    __versioned__ = {}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    reference_number = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)

# Finalize mappings and create tables
configure_mappers()
logger.info("Configured ORM mappers.")

Base.metadata.create_all(engine)
logger.info("Created database tables (if they did not exist).")
