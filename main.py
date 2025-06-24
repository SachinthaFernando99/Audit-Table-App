import uvicorn
from fastapi import FastAPI
from api.transaction_router import router as transaction_router

app = FastAPI()

app.include_router(transaction_router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)