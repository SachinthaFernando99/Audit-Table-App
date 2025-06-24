from abc import ABC, abstractmethod
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from repository.repo.transaction_repo import TransactionRepositoryInterface, get_transaction_repository
from repository.schema.transaction_create import TransactionModelCreate
from repository.schema.transaction_response import TransactionResponse
from util.logger import logger


class TransactionServiceInterface(ABC):
    """Interface for transaction service operations."""

    @abstractmethod
    def create_transaction(self, db: Session, transaction_create: TransactionModelCreate) -> TransactionResponse:
        pass

    @abstractmethod
    def get_transaction_by_id(self, db: Session, transaction_id: int) -> TransactionResponse:
        pass

    @abstractmethod
    def get_transaction_by_reference_number(self, db: Session, reference_number: str) -> TransactionResponse:
        pass

    @abstractmethod
    def update_transaction_by_reference_number(self, db: Session, reference_number: str, transaction_update: TransactionModelCreate) -> TransactionResponse:
        pass

    @abstractmethod
    def delete_transaction_by_reference_number(self, db: Session, reference_number: str) -> dict:
        pass


class TransactionService(TransactionServiceInterface):
    """Service layer for transaction operations with business logic and validation."""

    def __init__(self, transaction_repo: TransactionRepositoryInterface):
        self.transaction_repo = transaction_repo

    def create_transaction(self, db: Session, transaction_create: TransactionModelCreate) -> TransactionResponse:
        """
        Creates a new transaction with validation.
        Date and time are automatically set to Sri Lankan timezone.

        :param db: SQLAlchemy session
        :param transaction_create: Pydantic model with transaction data
        :return: TransactionResponse instance
        :raises HTTPException: If validation fails or creation error occurs
        """
        try:
            # Validate transaction data
            self._validate_transaction_create(transaction_create)

            logger.info(f"Creating transaction with reference: {transaction_create.reference_number}")

            # Create transaction through repository (time/date set automatically in Sri Lankan timezone)
            transaction = self.transaction_repo.create(db, transaction_create)

            # Convert to response model
            transaction_response = TransactionResponse.model_validate(transaction)

            logger.info(f"Transaction created successfully with ID: {transaction.id}")
            return transaction_response

        except HTTPException:
            # Re-raise HTTP exceptions from repository
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_transaction_by_id(self, db: Session, transaction_id: int) -> TransactionResponse:
        """
        Retrieves a transaction by ID with validation.

        :param db: SQLAlchemy session
        :param transaction_id: ID of the transaction to retrieve
        :return: TransactionResponse instance
        :raises HTTPException: If transaction not found or validation fails
        """
        try:
            # Validate transaction ID
            self._validate_transaction_id(transaction_id)

            logger.info(f"Retrieving transaction with ID: {transaction_id}")

            # Get transaction through repository
            transaction = self.transaction_repo.get_by_id(db, transaction_id)

            if not transaction:
                logger.warning(f"Transaction not found with ID: {transaction_id}")
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Convert to response model
            transaction_response = TransactionResponse.model_validate(transaction)

            logger.info(f"Transaction retrieved successfully with ID: {transaction_id}")
            return transaction_response

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_transaction_by_reference_number(self, db: Session, reference_number: str) -> TransactionResponse:
        """
        Retrieves a transaction by reference number with validation.

        :param db: SQLAlchemy session
        :param reference_number: Reference number of the transaction to retrieve
        :return: TransactionResponse instance
        :raises HTTPException: If transaction not found or validation fails
        """
        try:
            # Validate reference number
            self._validate_reference_number(reference_number)

            logger.info(f"Retrieving transaction with reference number: {reference_number}")

            # Get transaction through repository
            transaction = self.transaction_repo.get_by_reference_number(db, reference_number)

            if not transaction:
                logger.warning(f"Transaction not found with reference number: {reference_number}")
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Convert to response model
            transaction_response = TransactionResponse.model_validate(transaction)

            logger.info(f"Transaction retrieved successfully with reference number: {reference_number}")
            return transaction_response

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_transaction_by_reference_number(self, db: Session, reference_number: str, transaction_update: TransactionModelCreate) -> TransactionResponse:
        """
        Updates a transaction by reference number with validation.
        Date and time are automatically updated to current Sri Lankan timezone.

        :param db: SQLAlchemy session
        :param reference_number: Reference number of the transaction to update
        :param transaction_update: Updated transaction data
        :return: TransactionResponse instance
        :raises HTTPException: If validation fails or update error occurs
        """
        try:
            # Validate reference number and transaction data
            self._validate_reference_number(reference_number)
            self._validate_transaction_create(transaction_update)

            logger.info(f"Updating transaction with reference number: {reference_number}")

            # Update transaction through repository (time/date updated automatically in Sri Lankan timezone)
            transaction = self.transaction_repo.update_by_reference_number(db, reference_number, transaction_update)

            # Convert to response model
            transaction_response = TransactionResponse.model_validate(transaction)

            logger.info(f"Transaction updated successfully with reference number: {reference_number}")
            return transaction_response

        except HTTPException:
            # Re-raise HTTP exceptions from repository
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete_transaction_by_reference_number(self, db: Session, reference_number: str) -> dict:
        """
        Deletes a transaction by reference number with validation.

        :param db: SQLAlchemy session
        :param reference_number: Reference number of the transaction to delete
        :return: Success message dictionary
        :raises HTTPException: If validation fails or deletion error occurs
        """
        try:
            # Validate reference number
            self._validate_reference_number(reference_number)

            logger.info(f"Deleting transaction with reference number: {reference_number}")

            # Delete transaction through repository
            success = self.transaction_repo.delete_by_reference_number(db, reference_number)

            if success:
                logger.info(f"Transaction deleted successfully with reference number: {reference_number}")
                return {"message": f"Transaction with reference number {reference_number} deleted successfully"}
            else:
                logger.error(f"Failed to delete transaction with reference number: {reference_number}")
                raise HTTPException(status_code=500, detail="Failed to delete transaction")

        except HTTPException:
            # Re-raise HTTP exceptions from repository
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def _validate_transaction_create(self, transaction_create: TransactionModelCreate) -> None:
        """
        Validates transaction creation data.

        :param transaction_create: Transaction data to validate
        :raises HTTPException: If validation fails
        """
        # Validate reference number
        if not transaction_create.reference_number or not transaction_create.reference_number.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")

        # Validate payment method
        if not transaction_create.payment_method or not transaction_create.payment_method.strip():
            raise HTTPException(status_code=400, detail="Payment method is required")

        # Validate amount
        if transaction_create.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than zero")

        logger.debug("Transaction validation passed")

    def _validate_transaction_id(self, transaction_id: int) -> None:
        """
        Validates transaction ID.

        :param transaction_id: ID to validate
        :raises HTTPException: If validation fails
        """
        if not isinstance(transaction_id, int) or transaction_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid transaction ID")

        logger.debug(f"Transaction ID validation passed: {transaction_id}")

    def _validate_reference_number(self, reference_number: str) -> None:
        """
        Validates reference number.

        :param reference_number: Reference number to validate
        :raises HTTPException: If validation fails
        """
        if not reference_number or not reference_number.strip():
            raise HTTPException(status_code=400, detail="Reference number is required")

        logger.debug(f"Reference number validation passed: {reference_number}")


# Dependency injection function
def get_transaction_service(
        transaction_repo: TransactionRepositoryInterface = Depends(get_transaction_repository)
) -> TransactionServiceInterface:
    """Dependency injection function for transaction service."""
    return TransactionService(transaction_repo)