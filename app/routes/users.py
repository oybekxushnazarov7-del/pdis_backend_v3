import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_connection
from app.auth import get_hash, verify, create_token, oauth2_scheme, decode_token
from pydantic import BaseModel, EmailStr

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
users_router = APIRouter(prefix="/users", tags=["Users"])


class LoginData(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    id: int
    name: str
    email: EmailStr


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati o'tgan")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token ichida user_id yo'q")
    return user_id


# ==================== AUTH ====================

@auth_router.post("/register")
def register(user: LoginData):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pwd = get_hash(user.password)
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (user.name, user.email, hashed_pwd)
        )
        conn.commit()
        return {"message": "Muvaffaqiyatli ro'yxatdan o'tdingiz!"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Bu email allaqachon ro'yxatdan o'tgan")
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Register xatosi: {str(e)}")
    finally:
        conn.close()


@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s",
            (form_data.username,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=400, detail="Foydalanuvchi topilmadi")

        if not verify(form_data.password, user[3]):
            raise HTTPException(status_code=400, detail="Parol noto'g'ri")

        token = create_token({"user_id": user[0]})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login xatosi: {str(e)}")
    finally:
        conn.close()


# ==================== USERS ====================

# 1️⃣ POST
@users_router.post("/")
def create_user(user: UserCreate, current_user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE id = %s", (user.id,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"ID {user.id} allaqachon band")
        cursor.execute(
            "INSERT INTO users (id, name, email, password) VALUES (%s, %s, %s, %s)",
            (user.id, user.name, user.email, "")
        )
        conn.commit()
        return {"message": "User qo'shildi!", "id": user.id, "name": user.name, "email": user.email}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Bu email allaqachon mavjud")
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")
    finally:
        conn.close()


# 2️⃣ GET
@users_router.get("/")
def get_users(current_user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
    finally:
        conn.close()


# 3️⃣ DELETE
@users_router.delete("/{user_id}")
def delete_user(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"ID {user_id} topilmadi")
        cursor.execute("DELETE FROM expenses WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return {"message": f"ID {user_id} user va uning barcha xarajatlari o'chirildi"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")
    finally:
        conn.close()