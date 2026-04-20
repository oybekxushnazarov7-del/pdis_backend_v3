from fastapi import FastAPI
from app.db import get_connection
from app.routes import users, expenses

app = FastAPI()


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
def on_startup():
    create_tables()

# Routerlarni ulash
app.include_router(users.router)
app.include_router(expenses.router)

@app.get("/")
def home():
    return {"message": "Project successfully working!"}