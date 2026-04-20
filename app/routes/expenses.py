from fastapi import APIRouter
from app.db import get_connection
from pydantic import BaseModel

router = APIRouter()

class ExpenseCreate(BaseModel):
    id: int  # Xarajat uchun ham ID qo'lda kiritiladi
    category: str
    amount: float

@router.post("/expenses")
def add_expense(expense: ExpenseCreate):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (id, category, amount) VALUES (?, ?, ?)",
            (expense.id, expense.category, expense.amount)
        )
        conn.commit()
        return {"message": f"Xarajat {expense.id} muvaffaqiyatli qo'shildi"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@router.get("/expenses")
def get_expenses():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, amount FROM expenses")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({"id": row["id"], "category": row["category"], "amount": row["amount"]})
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return {"message": f"Xarajat {expense_id} o'chirildi"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()