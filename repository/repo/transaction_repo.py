from repository.model.transaction_model import TransactionModel
from repository.schema.transaction_create import TransactionModelCreate
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from util.logger import logger
from datetime import datetime
import pytz
from abc import ABC, abstractmethod


class TransactionRepositoryInterface(ABC):
    """Interface for transaction repository operations."""

    @abstractmethod
    def create(self, db: Session, transaction_create: TransactionModelCreate) -> TransactionModel:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, transaction_id: int) -> TransactionModel:
        pass

    @abstractmethod
    def get_by_reference_number(self, db: Session, reference_number: str) -> TransactionModel:
        pass

    @abstractmethod
    def update_by_reference_number(self, db: Session, reference_number: str,
                                   transaction_update: TransactionModelCreate) -> TransactionModel:
        pass

    @abstractmethod
    def delete_by_reference_number(self, db: Session, reference_number: str) -> bool:
        pass


class TransactionRepository(TransactionRepositoryInterface):
    """Implementation of transaction repository with database operations."""

    def create(self, db: Session, transaction_create: TransactionModelCreate) -> TransactionModel:
        """
        Creates a new transaction after checking for duplicate reference number.
        Automatically sets Sri Lankan date and time.

        :param db: SQLAlchemy session
        :param transaction_create: Pydantic model instance for validation
        :return: Created Transaction object
        :raises HTTPException: If reference number exists or database error occurs
        """
        try:
            # Check for duplicate reference number
            existing = db.query(TransactionModel).filter(
                TransactionModel.reference_number == transaction_create.reference_number
            ).first()

            if existing:
                logger.warning(f"Duplicate reference number: {transaction_create.reference_number}")
                raise HTTPException(status_code=400, detail="Reference number already exists")

            # Get current Sri Lankan time
            sri_lanka_tz = pytz.timezone('Asia/Colombo')
            current_time_sl = datetime.now(sri_lanka_tz)

            # Create new transaction instance with Sri Lankan time
            transaction = TransactionModel(
                reference_number=transaction_create.reference_number,
                payment_method=transaction_create.payment_method,
                amount=transaction_create.amount,
                date=current_time_sl.date(),
                time=current_time_sl.time()
            )

            logger.debug(f"Inserting Transaction: {transaction.__dict__}")

            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            logger.info(
                f"Transaction created successfully with ID {transaction.id} at Sri Lankan time: {current_time_sl}")
            return transaction

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during transaction creation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create transaction")

    def get_by_id(self, db: Session, transaction_id: int) -> TransactionModel:
        """
        Retrieves a transaction by its ID.

        :param db: SQLAlchemy session
        :param transaction_id: ID of the transaction
        :return: Transaction object or None
        :raises HTTPException: If database error occurs
        """
        try:
            transaction = db.query(TransactionModel).filter(
                TransactionModel.id == transaction_id
            ).first()

            if not transaction:
                logger.info(f"No transaction found with ID {transaction_id}")
                return None
            else:
                logger.info(f"Transaction retrieved with ID {transaction_id}")
                return transaction

        except SQLAlchemyError as e:
            logger.error(f"Database error during transaction retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve transaction")

    def get_by_reference_number(self, db: Session, reference_number: str) -> TransactionModel:
        """
        Retrieves a transaction by its reference number.

        :param db: SQLAlchemy session
        :param reference_number: Reference number of the transaction
        :return: Transaction object or None
        :raises HTTPException: If database error occurs
        """
        try:
            transaction = db.query(TransactionModel).filter(
                TransactionModel.reference_number == reference_number
            ).first()

            if not transaction:
                logger.info(f"No transaction found with reference number {reference_number}")
                return None
            else:
                logger.info(f"Transaction retrieved with reference number {reference_number}")
                return transaction

        except SQLAlchemyError as e:
            logger.error(f"Database error during transaction retrieval by reference number: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve transaction")

    def update_by_reference_number(self, db: Session, reference_number: str,
                                   transaction_update: TransactionModelCreate) -> TransactionModel:
        """
        Updates a transaction by its reference number.
        Automatically updates the Sri Lankan date and time.

        :param db: SQLAlchemy session
        :param reference_number: Reference number of the transaction to update
        :param transaction_update: Updated transaction data
        :return: Updated Transaction object
        :raises HTTPException: If transaction not found or database error occurs
        """
        try:
            # Find the existing transaction
            transaction = db.query(TransactionModel).filter(
                TransactionModel.reference_number == reference_number
            ).first()

            if not transaction:
                logger.warning(f"Transaction not found with reference number: {reference_number}")
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Check if new reference number conflicts with existing one (if changed)
            if transaction_update.reference_number != reference_number:
                existing = db.query(TransactionModel).filter(
                    TransactionModel.reference_number == transaction_update.reference_number
                ).first()

                if existing:
                    logger.warning(f"Duplicate reference number: {transaction_update.reference_number}")
                    raise HTTPException(status_code=400, detail="New reference number already exists")

            # Get current Sri Lankan time for update
            sri_lanka_tz = pytz.timezone('Asia/Colombo')
            current_time_sl = datetime.now(sri_lanka_tz)

            # Update transaction fields
            transaction.reference_number = transaction_update.reference_number
            transaction.payment_method = transaction_update.payment_method
            transaction.amount = transaction_update.amount
            transaction.date = current_time_sl.date()
            transaction.time = current_time_sl.time()

            logger.debug(f"Updating Transaction: {transaction.__dict__}")

            db.commit()
            db.refresh(transaction)
            logger.info(
                f"Transaction updated successfully with reference number {reference_number} at Sri Lankan time: {current_time_sl}")
            return transaction

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during transaction update: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update transaction")

    def delete_by_reference_number(self, db: Session, reference_number: str) -> bool:
        """
        Deletes a transaction by its reference number.

        :param db: SQLAlchemy session
        :param reference_number: Reference number of the transaction to delete
        :return: True if deleted successfully
        :raises HTTPException: If transaction not found or database error occurs
        """
        try:
            # Find the existing transaction
            transaction = db.query(TransactionModel).filter(
                TransactionModel.reference_number == reference_number
            ).first()

            if not transaction:
                logger.warning(f"Transaction not found with reference number: {reference_number}")
                raise HTTPException(status_code=404, detail="Transaction not found")

            logger.debug(f"Deleting Transaction: {transaction.__dict__}")

            db.delete(transaction)
            db.commit()
            logger.info(f"Transaction deleted successfully with reference number {reference_number}")
            return True

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during transaction deletion: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete transaction")


# Dependency injection function
def get_transaction_repository() -> TransactionRepositoryInterface:
    """Dependency injection function for transaction repository."""
    return TransactionRepository()