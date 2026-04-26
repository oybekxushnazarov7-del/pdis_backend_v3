import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from app.auth import oauth2_scheme, decode_token
from pydantic import BaseModel

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class ExpenseCreate(BaseModel):
    category: str
    amount: float


class BudgetCreate(BaseModel):
    month_year: str  # YYYY-MM
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


@router.post("/budget")
def set_budget(budget: BudgetCreate, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO budgets (account_id, month_year, amount) VALUES (%s, %s, %s) ON CONFLICT (account_id, month_year) DO UPDATE SET amount = EXCLUDED.amount",
            (account_id, budget.month_year, budget.amount)
        )
        conn.commit()
        return {"message": "Budget set successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@router.get("/budget/{month_year}")
def get_budget(month_year: str, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT amount FROM budgets WHERE account_id = %s AND month_year = %s",
            (account_id, month_year)
        )
        row = cursor.fetchone()
        if row:
            return {"amount": row[0]}
        return {"amount": 0}
    finally:
        conn.close()


@router.get("/analytics/{month_year}")
def get_analytics(month_year: str, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Total expenses for the month
        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE account_id = %s AND strftime('%%Y-%%m', created_at) = %s",
            (account_id, month_year)
        )
        total_expenses = cursor.fetchone()[0] or 0
        
        # Category breakdown
        cursor.execute(
            "SELECT category, SUM(amount) FROM expenses WHERE account_id = %s AND strftime('%%Y-%%m', created_at) = %s GROUP BY category",
            (account_id, month_year)
        )
        categories = [{"category": r[0], "amount": r[1]} for r in cursor.fetchall()]
        
        # Budget
        cursor.execute(
            "SELECT amount FROM budgets WHERE account_id = %s AND month_year = %s",
            (account_id, month_year)
        )
        budget_row = cursor.fetchone()
        budget = budget_row[0] if budget_row else 0
        
        return {
            "total_expenses": total_expenses,
            "budget": budget,
            "remaining": budget - total_expenses,
            "categories": categories
        }
    finally:
        conn.close()


@router.get("/export/csv")
def export_expenses_csv(account_id: int = Depends(get_current_account_id)):
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category, amount, created_at FROM expenses WHERE account_id = %s ORDER BY created_at DESC",
            (account_id,)
        )
        rows = cursor.fetchall()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Category", "Amount", "Date"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3]])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=expenses.csv"}
        )
    finally:
        conn.close()