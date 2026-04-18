from fastapi import APIRouter
from app.db import get_connection
from pydantic import BaseModel

router = APIRouter()


class ExpenseCreate(BaseModel):
    user_id: int
    amount: float
    category: str


@router.post("/expenses")
def add_expense(expense: ExpenseCreate):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
            (expense.user_id, expense.amount, expense.category)
        )

        conn.commit()
        return {"message": "Expense added"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        conn.close()


@router.get("/expenses")
def get_expenses():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row.id,
                "user_id": row.user_id,
                "amount": float(row.amount),
                "category": row.category,
                "created_at": str(row.created_at)
            })

        return result

    finally:
        conn.close() 