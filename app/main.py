from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

# ✅ Fayl joylashgan papkani aniq topamiz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="PDIS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)

# ✅ Mutlaq yo'l bilan static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))