from fastapi import APIRouter
from app.db import get_connection
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    id: int  # Endi ID ham majburiy!
    name: str
    email: str

@router.post("/users")
def create_user(user: UserCreate):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # INSERT so'roviga 'id' ustunini qo'shamiz
        cursor.execute(
            "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
            (user.id, user.name, user.email)
        )
        conn.commit()
        return {"message": f"User {user.id} muvaffaqiyatli yaratildi"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@router.get("/users")
def get_users():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({"id": row["id"], "name": row["name"], "email": row["email"]})
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return {"message": f"Foydalanuvchi {user_id} o'chirildi"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()