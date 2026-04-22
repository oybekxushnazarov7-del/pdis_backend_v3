from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import get_connection
from app.routes.users import auth_router, users_router
from app.routes import expenses

tags_metadata = [
    {"name": "Auth"},
    {"name": "Users"},
    {"name": "Expenses"},
]


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Login/Register uchun
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Foydalanuvchi o'zi qo'shadigan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            account_id INTEGER REFERENCES accounts(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL REFERENCES accounts(id),
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

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(expenses.router)


@app.get("/")
def home():
    return {
        "message": "PDIS API ishlamoqda 🚀",
        "docs": "/docs"
    }