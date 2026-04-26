import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from app.auth import oauth2_scheme, decode_token
from pydantic import BaseModel

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class ExpenseCreate(BaseModel):
    category: str
    amount: float


class CategoryResponse(BaseModel):
    id: int
    name: str
    emoji: str
    description: str


def get_current_account_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Access token required")
    account_id = payload.get("user_id")
    if account_id is None:
        raise HTTPException(status_code=401, detail="No user_id in token")
    return account_id


@router.get("/categories/list")
def get_categories():
    """Return all categories"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, emoji, description FROM categories ORDER BY id"
        )
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1], "emoji": r[2], "description": r[3]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@router.post("/")
def add_expense(expense: ExpenseCreate, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (account_id, category, amount) VALUES (%s, %s, %s) RETURNING id",
            (account_id, expense.category, expense.amount)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Expense added successfully", "id": new_id, "category": expense.category, "amount": expense.amount}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@router.get("/")
def get_expenses(account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            # ✅ ASC - oldest first, newest last
            "SELECT id, category, amount, created_at FROM expenses WHERE account_id = %s ORDER BY created_at ASC",
            (account_id,)
        )
        rows = cursor.fetchall()
        return [{"id": r[0], "category": r[1], "amount": r[2], "created_at": r[3]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM expenses WHERE id = %s AND account_id = %s",
            (expense_id, account_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found or does not belong to you")
        return {"message": "Deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()