from fastapi import APIRouter
from app.db import get_connection
from pydantic import BaseModel

router = APIRouter()

# Bu model faqat ma'lumot yuborish (POST) uchun
class ExpenseCreate(BaseModel):
    category: str
    amount: float

# 1. Xarajat qo'shish (POST)
@router.post("/expenses")
def add_expense(expense: ExpenseCreate):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # ID bu yerda avtomatik qo'yiladi (AUTOINCREMENT)
        cursor.execute(
            "INSERT INTO expenses (category, amount) VALUES (?, ?)",
            (expense.category, expense.amount)
        )
        conn.commit()
        return {"message": "Expense added"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

# 2. Xarajatlarni ko'rish (GET) - ID SHU YERDA CHIQADI
@router.get("/expenses")
def get_expenses():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Bazadan ID ni ham olamiz
        cursor.execute("SELECT id, category, amount FROM expenses")
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "id": row["id"],          # Mana bu yerda ID bor
                "category": row["category"],
                "amount": row["amount"]
            })
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

# 3. Xarajatni o'chirish (DELETE)
@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return {"message": f"Expense ID {expense_id} muvaffaqiyatli o'chirildi"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()