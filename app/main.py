from fastapi import FastAPI
from app.routes import users, expenses

app = FastAPI()

app.include_router(users.router)
app.include_router(expenses.router)

@app.get("/")
def home():
    return {"message": "Project successfully working!"}