from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

# Determine the root project directory - more robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Debug: Log the paths being used
print(f"BASE_DIR: {BASE_DIR}")
print(f"STATIC_DIR: {STATIC_DIR}")
print(f"STATIC_DIR exists: {os.path.exists(STATIC_DIR)}")
if os.path.exists(STATIC_DIR):
    print(f"Static files: {os.listdir(STATIC_DIR)}")

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
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                emoji TEXT,
                description TEXT
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

def populate_categories():
    categories = [
        ('Food & Drinks', '🍔', 'Dining, groceries, and beverages'),
        ('Transportation', '🚗', 'Fuel, public transport, and taxis'),
        ('Shopping', '🛍️', 'Clothes, electronics, and personal items'),
        ('Housing', '🏠', 'Rent, utilities, and maintenance'),
        ('Entertainment', '🎬', 'Movies, games, and hobbies'),
        ('Health', '💊', 'Medicine, gym, and doctor visits'),
        ('Education', '📚', 'Courses, books, and tuition'),
        ('Travel', '✈️', 'Flights, hotels, and sightseeing'),
        ('Others', '📦', 'Miscellaneous expenses')
    ]
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO categories (name, emoji, description) VALUES (%s, %s, %s)",
                categories
            )
            conn.commit()
            print("Default categories populated.")
        conn.close()
    except Exception as e:
        print(f"Error populating categories: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    populate_categories()
    yield

app = FastAPI(title="PDIS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)

# Mount static files so index.html and app.js work
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def home():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found", "path": index_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)