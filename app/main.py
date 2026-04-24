from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

# ✅ Render va mahalliy kompyuter uchun universal yo'lni aniqlash
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static papkasini qidirish algoritmi
possible_static_paths = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "app", "static"),
    "/opt/render/project/src/static" # Render'dagi absolyut yo'l
]

STATIC_DIR = None
for path in possible_static_paths:
    if os.path.exists(path):
        STATIC_DIR = path
        break

def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Accounts jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        # Users jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE
            )
        """)
        # Expenses jadvali
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
        print("✅ Ma'lumotlar bazasi jadvallari tayyor.")
    except Exception as e:
        print(f"❌ Ma'lumotlar bazasida xato: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(title="PDIS API", lifespan=lifespan)

# CORS sozlamalari (Frontend ulanishi uchun)
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

# ✅ Static fayllarni (CSS, JS, Images) ulash
if STATIC_DIR:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print(f"✅ Static papka topildi: {STATIC_DIR}")
else:
    print("⚠️ Diqqat: Static papka topilmadi!")

# ✅ Asosiy sahifa (Frontend)
@app.get("/")
async def home():
    if STATIC_DIR:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # Agar index.html baribir topilmasa, debug ma'lumotlarini qaytaradi
    return {
        "error": "index.html topilmadi",
        "debug_info": {
            "base_dir": BASE_DIR,
            "checked_paths": possible_static_paths,
            "current_static_dir": STATIC_DIR,
            "files_in_root": os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else "N/A"
        }
    }