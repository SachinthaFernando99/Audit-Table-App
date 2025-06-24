from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from service.transaction_service import TransactionServiceInterface, get_transaction_service
from repository.schema.transaction_create import TransactionModelCreate
from repository.schema.transaction_response import TransactionResponse
from util.database import get_db
from util.logger import logger

# Create router instance
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/",
             response_model=TransactionResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create a new transaction",
             description="Creates a new transaction with the provided details. Date and time are automatically set to Sri Lankan timezone.")
async def create_transaction(
        transaction_create: TransactionModelCreate,
        db: Session = Depends(get_db),
        transaction_service: TransactionServiceInterface = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Create a new transaction.

    - **reference_number**: Unique reference number for the transaction
    - **payment_method**: Method of payment used
    - **amount**: Transaction amount (must be greater than 0)

    Note: Date and time are automatically set to current Sri Lankan time when the transaction is created.
    """
    try:
        logger.info(f"Received request to create transaction: {transaction_create.reference_number}")

        # Create transaction through injected service
        transaction_response = transaction_service.create_transaction(db, transaction_create)

        logger.info(f"Transaction created successfully with ID: {transaction_response.id}")
        return transaction_response

    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_transaction endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{transaction_id}",
            response_model=TransactionResponse,
            summary="Get transaction by ID",
            description="Retrieves a single transaction by its ID")
async def get_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        transaction_service: TransactionServiceInterface = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Get a transaction by ID.

    - **transaction_id**: The ID of the transaction to retrieve
    """
    try:
        logger.info(f"Received request to get transaction with ID: {transaction_id}")

        # Get transaction through injected service
        transaction_response = transaction_service.get_transaction_by_id(db, transaction_id)

        logger.info(f"Transaction retrieved successfully with ID: {transaction_id}")
        return transaction_response

    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_transaction endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/reference/{reference_number}",
            response_model=TransactionResponse,
            summary="Get transaction by reference number",
            description="Retrieves a single transaction by its reference number")
async def get_transaction_by_reference(
        reference_number: str,
        db: Session = Depends(get_db),
        transaction_service: TransactionServiceInterface = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Get a transaction by reference number.

    - **reference_number**: The reference number of the transaction to retrieve
    """
    try:
        logger.info(f"Received request to get transaction with reference number: {reference_number}")

        # Get transaction through injected service
        transaction_response = transaction_service.get_transaction_by_reference_number(db, reference_number)

        logger.info(f"Transaction retrieved successfully with reference number: {reference_number}")
        return transaction_response

    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_transaction_by_reference endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/reference/{reference_number}",
            response_model=TransactionResponse,
            summary="Update transaction by reference number",
            description="Updates a transaction by its reference number. Date and time are automatically updated to current Sri Lankan timezone.")
async def update_transaction_by_reference(
        reference_number: str,
        transaction_update: TransactionModelCreate,
        db: Session = Depends(get_db),
        transaction_service: TransactionServiceInterface = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Update a transaction by reference number.

    - **reference_number**: The reference number of the transaction to update
    - **reference_number** (in body): New reference number for the transaction
    - **payment_method**: Updated payment method
    - **amount**: Updated transaction amount (must be greater than 0)

    Note: Date and time are automatically updated to current Sri Lankan time when the transaction is updated.
    """
    try:
        logger.info(f"Received request to update transaction with reference number: {reference_number}")

        # Update transaction through injected service
        transaction_response = transaction_service.update_transaction_by_reference_number(db, reference_number, transaction_update)

        logger.info(f"Transaction updated successfully with reference number: {reference_number}")
        return transaction_response

    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_transaction_by_reference endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/reference/{reference_number}",
               status_code=status.HTTP_200_OK,
               summary="Delete transaction by reference number",
               description="Deletes a transaction by its reference number")
async def delete_transaction_by_reference(
        reference_number: str,
        db: Session = Depends(get_db),
        transaction_service: TransactionServiceInterface = Depends(get_transaction_service)
) -> dict:
    """
    Delete a transaction by reference number.

    - **reference_number**: The reference number of the transaction to delete
    """
    try:
        logger.info(f"Received request to delete transaction with reference number: {reference_number}")

        # Delete transaction through injected service
        result = transaction_service.delete_transaction_by_reference_number(db, reference_number)

        logger.info(f"Transaction deleted successfully with reference number: {reference_number}")
        return result

    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_transaction_by_reference endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )