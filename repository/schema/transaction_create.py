from pydantic import BaseModel

class TransactionModelCreate(BaseModel):
    reference_number: str
    payment_method: str
    amount: float