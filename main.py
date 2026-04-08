from fastapi import FastAPI
from database import engine, Base
import models
from app.documents import router as documents_router

app = FastAPI()
app.include_router(documents_router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Travel Assistant Backend Running"}