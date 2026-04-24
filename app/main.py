from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

# ✅ Papka manzillarini tekshirish
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Render va mahalliy kompyuter uchun barcha variantlarni tekshiramiz
possible_paths = [
    os.path.join(BASE_DIR, "static"),           # Ildizda bo'lsa
    os.path.join(BASE_DIR, "app", "static"),    # app ichida bo'lsa
    "/opt/render/project/src/static"            # Render-ning absolyut manzili
]

STATIC_DIR = None
for path in possible_paths:
    if os.path.exists(path):
        STATIC_DIR = path
        break

def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS accounts (id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id SERIAL PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE, amount REAL NOT NULL, category TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(title="PDIS API", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)

# ✅ Static fayllarni ulash
if STATIC_DIR:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def home():
    if STATIC_DIR:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # Agar topilmasa, tizimda nima borligini ko'rish uchun (faqat debug)
    return {
        "error": "index.html hali ham topilmadi",
        "current_dir": BASE_DIR,
        "searched_in": possible_paths,
        "found_static_dir": STATIC_DIR,
        "existing_files": os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else "dir not found"
    }