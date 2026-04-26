from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Import modules
from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses
# ✅ New: auth.py router with refresh endpoint
from app.auth import router as auth_methods_router 

# Determine folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def create_tables():
    """Create database tables (with SERIAL ids)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Accounts table
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
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        
        # Expenses table
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
        print("Tables verified/created successfully.")
    except Exception as e:
        print(f"Database error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(title="PDIS API", lifespan=lifespan)

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API Routerlarni ulash
app.include_router(auth_router)  # Login/Register (/auth/login)
app.include_router(auth_methods_router) # ✅ YANGI: Refresh endpointi (/auth/refresh)
app.include_router(users_router) # Userlar bilan ishlash
app.include_router(expenses.router) # Xarajatlar

# Static fayllarni ulash
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Asosiy sahifa
@app.get("/")
async def home():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {
        "status": "error",
        "message": "index.html topilmadi",
        "debug_path": index_path
    }