from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

# ✅ To'g'ri absolyut yo'lni aniqlash
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rasmdagi strukturaga ko'ra, static papkasi ildizda (root) joylashgan:
STATIC_DIR = os.path.join(BASE_DIR, "static")

def create_tables():
    try:
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
        cursor.execute("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE")
        cursor.execute("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS verification_code_hash TEXT")
        cursor.execute("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS verification_expires_at TIMESTAMP")
        cursor.execute("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS verification_attempts INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_verification_sent_at TIMESTAMP")
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
    except Exception as e:
        print(f"Database error: {e}")

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

# Routerlar
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)

# ✅ Static fayllarni ulash (index.html ichidagi js/css lar ishlashi uchun)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def home():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found", "path": index_path}