import psycopg2
from fastapi import APIRouter, Depends, HTTPException, Request
from app.db import get_connection
from app.auth import decode_token
from pydantic import BaseModel

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class ExpenseCreate(BaseModel):
    category: str
    amount: float
    user_id: int = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    emoji: str
    description: str


def get_current_account_id(request: Request) -> int:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]
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
            "INSERT INTO expenses (account_id, user_id, category, amount) VALUES (%s, %s, %s, %s) RETURNING id",
            (account_id, expense.user_id, expense.category, expense.amount)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Expense added successfully", "id": new_id, "category": expense.category, "amount": expense.amount, "user_id": expense.user_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@router.get("/")
def get_expenses(user_id: int = None, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, category, amount, created_at, user_id FROM expenses WHERE account_id = %s"
        params = [account_id]
        
        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
            
        query += " ORDER BY created_at ASC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [{"id": r[0], "category": r[1], "amount": r[2], "created_at": r[3], "user_id": r[4]} for r in rows]
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


@router.get("/analytics/{month_year}")
def get_analytics(month_year: str, user_id: int = None, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        base_query_total = "SELECT SUM(amount) FROM expenses WHERE account_id = %s AND TO_CHAR(created_at, 'YYYY-MM') = %s"
        base_query_cats = "SELECT category, SUM(amount) FROM expenses WHERE account_id = %s AND TO_CHAR(created_at, 'YYYY-MM') = %s"
        params = [account_id, month_year]
        
        if user_id:
            base_query_total += " AND user_id = %s"
            base_query_cats += " AND user_id = %s"
            params.append(user_id)
            
        base_query_cats += " GROUP BY category"
        
        cursor.execute(base_query_total, tuple(params))
        total_expenses = cursor.fetchone()[0] or 0
        
        cursor.execute(base_query_cats, tuple(params))
        categories = [{"category": r[0], "amount": r[1]} for r in cursor.fetchall()]
        
        return {
            "total_expenses": total_expenses,
            "categories": categories
        }
    finally:
        conn.close()


@router.get("/report/summary")
def get_report_summary(account_id: int = Depends(get_current_account_id)):
    """Get total spending per user for the whole account"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Join with users table to get names. 
        # Expenses with user_id NULL are treated as 'Main Account' or excluded? 
        # Let's include them as 'Owner' if user_id is NULL.
        cursor.execute("""
            SELECT 
                COALESCE(u.name, 'Main Account') as user_name,
                SUM(e.amount) as total_amount
            FROM expenses e
            LEFT JOIN users u ON e.user_id = u.id
            WHERE e.account_id = %s
            GROUP BY u.name
        """, (account_id,))
        rows = cursor.fetchall()
        return [{"user_name": r[0], "total_amount": r[1]} for r in rows]
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