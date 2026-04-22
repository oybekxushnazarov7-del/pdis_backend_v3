import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from app.auth import oauth2_scheme, decode_token
from pydantic import BaseModel

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class ExpenseCreate(BaseModel):
    id: int
    category: str
    amount: float


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati o'tgan")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token ichida user_id yo'q")
    return user_id


# 1️⃣ POST
@router.post("/")
def add_expense(expense: ExpenseCreate, user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM expenses WHERE id = %s", (expense.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"ID {expense.id} allaqachon band")
        cursor.execute(
            "INSERT INTO expenses (id, user_id, category, amount) VALUES (%s, %s, %s, %s)",
            (expense.id, user_id, expense.category, expense.amount)
        )
        conn.commit()
        return {"message": "Xarajat qo'shildi", "id": expense.id, "category": expense.category, "amount": expense.amount}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")
    finally:
        conn.close()


# 2️⃣ GET
@router.get("/")
def get_expenses(user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category, amount, created_at FROM expenses WHERE user_id = %s",
            (user_id,)
        )
        rows = cursor.fetchall()
        return [{"id": r[0], "category": r[1], "amount": r[2], "created_at": r[3]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")
    finally:
        conn.close()


# 3️⃣ DELETE
@router.delete("/{expense_id}")
def delete_expense(expense_id: int, user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM expenses WHERE id = %s AND user_id = %s",
            (expense_id, user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"ID {expense_id} topilmadi yoki sizga tegishli emas")
        return {"message": f"ID {expense_id} xarajat o'chirildi"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")
    finally:
        conn.close()