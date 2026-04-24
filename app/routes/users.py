import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_connection
# ✅ create_tokens (ko'plikda) import qilinganiga ishonch hosil qiling
from app.auth import get_hash, verify, create_tokens, oauth2_scheme, decode_token
from pydantic import BaseModel, EmailStr

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
users_router = APIRouter(prefix="/users", tags=["Users"])

class RegisterData(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr

def get_current_account_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati o'tgan")
    # ✅ Token ichidan user_id ni olamiz
    account_id = payload.get("user_id")
    if account_id is None:
        raise HTTPException(status_code=401, detail="Token ichida user_id yo'q")
    return account_id

# ==================== AUTH ====================

@auth_router.post("/register")
def register(data: RegisterData):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pwd = get_hash(data.password)
        cursor.execute(
            "INSERT INTO accounts (name, email, password) VALUES (%s, %s, %s)",
            (data.name, data.email, hashed_pwd)
        )
        conn.commit()
        return {"message": "Muvaffaqiyatli ro'yxatdan o'tdingiz!"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Bu email allaqachon ro'yxatdan o'tgan")
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
            "SELECT id, name, email, password FROM accounts WHERE email = %s",
            (form_data.username,)
        )
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=400, detail="Foydalanuvchi topilmadi")
        
        if not verify(form_data.password, account[3]):
            raise HTTPException(status_code=400, detail="Parol noto'g'ri")
        
        # ✅ O'ZGARTIRILDI: Ikkala tokenni ham yaratamiz
        access_token, refresh_token = create_tokens({"user_id": account[0], "sub": account[2]})
        
        # ✅ O'ZGARTIRILDI: Frontendga ikkala tokenni qaytaramiz
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login xatosi: {str(e)}")
    finally:
        conn.close()

# ==================== USERS ====================
# Qolgan funksiyalar (create_user, get_users, delete_user) o'z holicha qoladi, 
# chunki ular get_current_account_id orqali to'g'ri ishlaydi.

@users_router.post("/")
def create_user(user: UserCreate, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, account_id) VALUES (%s, %s, %s) RETURNING id",
            (user.name, user.email, account_id)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "User qo'shildi!", "id": new_id, "name": user.name, "email": user.email}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@users_router.get("/")
def get_users(account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE account_id = %s", (account_id,))
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
    finally:
        conn.close()

@users_router.delete("/{user_id}")
def delete_user(user_id: int, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s AND account_id = %s", (user_id, account_id))
        conn.commit()
        return {"message": "O'chirildi"}
    finally:
        conn.close()