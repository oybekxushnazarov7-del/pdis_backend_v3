from fastapi import APIRouter
from app.db import get_connection
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

@router.post("/users")
def create_user(user: UserCreate):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email)
        )
        conn.commit()
        return {"message": "User created"}
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
            # Diqqat! Bu qatorlar 'for' dan 4 ta probel ichkarida bo'lishi shart
            result.append({
                "id": row["id"],
                "name": row["name"],
                "email": row["email"]
            })

        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()