from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Frontend uchun kerak
from fastapi.responses import FileResponse  # Frontend uchun kerak
from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

tags_metadata = [
    {"name": "Auth", "description": "Ro'yxatdan o'tish va login"},
    {"name": "Users", "description": "Foydalanuvchilarni boshqarish"},
    {"name": "Expenses", "description": "Xarajatlar bilan ishlash"},
]

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Accounts jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # 2. Users jadvali (SERIAL va ON DELETE CASCADE qo'shildi)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, 
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)

    # 3. Expenses jadvali (SERIAL va ON DELETE CASCADE qo'shildi)
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

app = FastAPI(
    title="PDIS API with Auth",
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

# ✅ CORS sozlamalari - Front-end ulanishi uchun shart
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlarni ulash
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)

# ✅ Frontend fayllari uchun (static papkasi yaratganingizdan keyin)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    # Agar frontend tayyor bo'lsa, FileResponse("static/index.html") qaytarish mumkin
    return {
        "message": "PDIS API ishlamoqda 🚀",
        "docs": "/docs",
        "version": "3.0"
    }