"""FastAPI application entrypoint """

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.db.session import Base, engine
import app.db.models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fullstack Agent Challenge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
