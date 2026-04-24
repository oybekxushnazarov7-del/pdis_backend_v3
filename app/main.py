from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Loyihangizdagi mavjud modullarni import qilish
from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

# ✅ Papka manzillarini aniqlash (Ildiz papkada bo'lsa)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def create_tables():
    """Ma'lumotlar bazasi jadvallarini yaratish"""
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
        print(f"Bazada xato: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dastur yoqilganda bazani tayyorlaydi
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

# API Routerlarni ulash
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)

# ✅ Static fayllarni ulash (CSS/JS ishlashi uchun)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ✅ Asosiy sahifa (Login/Frontend)
@app.get("/")
async def home():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Agar topilmasa, xatoni tushuntirish
    return {
        "status": "error",
        "message": "index.html topilmadi",
        "debug_path": index_path,
        "current_files": os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else "N/A"
    }