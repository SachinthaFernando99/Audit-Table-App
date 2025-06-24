from pydantic import BaseModel
from datetime import date, time

class TransactionResponse(BaseModel):
    id: int
    reference_number: str
    date: date
    time: time
    payment_method: str
    amount: float

    class Config:
        from_attributes = True