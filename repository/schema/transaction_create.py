from pydantic import BaseModel

class TransactionModelCreate(BaseModel):
    user_id: str
    reference_number: str
    payment_method: str
    amount: float