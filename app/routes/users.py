import psycopg2
from datetime import datetime, timedelta
import hashlib
import os
import random
import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, Request
from app.db import get_connection
from app.auth import (
    get_hash, verify,
    create_access_token, create_refresh_token,
    decode_token
)
from pydantic import BaseModel, EmailStr

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
users_router = APIRouter(prefix="/users", tags=["Users"])


class RegisterData(BaseModel):
    name: str
    email: EmailStr
    password: str


class VerifyEmailData(BaseModel):
    email: EmailStr
    code: str


class ResendVerificationData(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class LoginData(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


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


def _hash_verification_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _generate_verification_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _send_verification_email(email: str, code: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@pdis.local")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    # Dev fallback: if SMTP is not configured, keep flow usable locally.
    if not smtp_host or not smtp_user or not smtp_password:
        print(f"[DEV] Email verification code for {email}: {code}")
        return

    msg = EmailMessage()
    msg["Subject"] = "PDIS Email Verification Code"
    msg["From"] = smtp_from
    msg["To"] = email
    msg.set_content(
        "Hello!\n\n"
        f"Your PDIS verification code is: {code}\n"
        "This code is valid for 5 minutes.\n\n"
        "If you did not request this, please ignore this email."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        if smtp_use_tls:
            server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def _send_verification_email_or_raise(email: str, code: str) -> None:
    try:
        _send_verification_email(email, code)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to send verification email. Check SMTP settings."
        )


def _is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = any(ch.isupper() for ch in password)
    has_lower = any(ch.islower() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    has_symbol = any(not ch.isalnum() for ch in password)
    return has_upper and has_lower and has_digit and has_symbol


# ==================== AUTH ====================

@auth_router.post("/register")
def register(data: RegisterData):
    if not _is_strong_password(data.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters and include upper/lower case letters, a number, and a symbol."
        )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_pwd = get_hash(data.password)
        code = _generate_verification_code()
        code_hash = _hash_verification_code(code)
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        cursor.execute(
            "SELECT id, email_verified FROM accounts WHERE email = %s",
            (data.email,)
        )
        existing = cursor.fetchone()
        if existing and existing[1]:
            raise HTTPException(status_code=400, detail="This email is already registered")

        if existing:
            cursor.execute(
                """
                UPDATE accounts
                SET name = %s,
                    password = %s,
                    verification_code_hash = %s,
                    verification_expires_at = %s,
                    verification_attempts = 0,
                    last_verification_sent_at = NOW()
                WHERE id = %s
                """,
                (data.name, hashed_pwd, code_hash, expires_at, existing[0])
            )
        else:
            cursor.execute(
                """
                INSERT INTO accounts (
                    name, email, password, email_verified,
                    verification_code_hash, verification_expires_at,
                    verification_attempts, last_verification_sent_at
                )
                VALUES (%s, %s, %s, FALSE, %s, %s, 0, NOW())
                """,
                (data.name, data.email, hashed_pwd, code_hash, expires_at)
            )

        conn.commit()
        _send_verification_email_or_raise(data.email, code)
        return {"message": "Verification code sent to your email"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@auth_router.post("/login")
def login(data: LoginData):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password FROM accounts WHERE email = %s",
            (data.email,)
        )
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=400, detail="User not found")
        if not verify(data.password, account[3]):
            raise HTTPException(status_code=400, detail="Incorrect password")
        cursor.execute(
            "SELECT email_verified FROM accounts WHERE id = %s",
            (account[0],)
        )
        email_verified = cursor.fetchone()[0]
        if not email_verified:
            raise HTTPException(
                status_code=403,
                detail="Email not verified. Please enter the verification code first."
            )
        access_token = create_access_token({"user_id": account[0]})
        refresh_token = create_refresh_token({"user_id": account[0]})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@auth_router.post("/verify-email")
def verify_email(data: VerifyEmailData):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, verification_code_hash, verification_expires_at, verification_attempts, email_verified
            FROM accounts
            WHERE email = %s
            """,
            (data.email,)
        )
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if account[4]:
            return {"message": "Email is already verified"}
        if not account[1] or not account[2]:
            raise HTTPException(status_code=400, detail="Verification code not found. Please request it again.")
        if account[3] >= 5:
            raise HTTPException(status_code=400, detail="Too many wrong attempts. Request a new code.")
        if datetime.utcnow() > account[2]:
            raise HTTPException(status_code=400, detail="Code expired. Request a new code.")
        if _hash_verification_code(data.code) != account[1]:
            cursor.execute(
                "UPDATE accounts SET verification_attempts = verification_attempts + 1 WHERE id = %s",
                (account[0],)
            )
            conn.commit()
            raise HTTPException(status_code=400, detail="Incorrect code")

        cursor.execute(
            """
            UPDATE accounts
            SET email_verified = TRUE,
                verification_code_hash = NULL,
                verification_expires_at = NULL,
                verification_attempts = 0
            WHERE id = %s
            """,
            (account[0],)
        )
        conn.commit()
        return {"message": "Email muvaffaqiyatli tasdiqlandi"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@auth_router.post("/resend-verification")
def resend_verification(data: ResendVerificationData):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, email_verified, last_verification_sent_at
            FROM accounts
            WHERE email = %s
            """,
            (data.email,)
        )
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if account[1]:
            raise HTTPException(status_code=400, detail="This email is already verified")

        if account[2] and (datetime.utcnow() - account[2]).total_seconds() < 60:
            raise HTTPException(status_code=429, detail="Please request a new code after 60 seconds")

        code = _generate_verification_code()
        code_hash = _hash_verification_code(code)
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        cursor.execute(
            """
            UPDATE accounts
            SET verification_code_hash = %s,
                verification_expires_at = %s,
                verification_attempts = 0,
                last_verification_sent_at = NOW()
            WHERE id = %s
            """,
            (code_hash, expires_at, account[0])
        )
        conn.commit()
        _send_verification_email_or_raise(data.email, code)
        return {"message": "New verification code sent"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@auth_router.post("/refresh")
def refresh_token(data: RefreshRequest):
    payload = decode_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token required")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="user_id is missing in token")
    new_access_token = create_access_token({"user_id": user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}


# ==================== USERS ====================

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
        return {"message": "User added!", "id": new_id, "name": user.name, "email": user.email}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="This email already exists")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()


@users_router.get("/")
def get_users(account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            # ✅ ASC — oldest first, newest last
            "SELECT id, name, email FROM users WHERE account_id = %s ORDER BY id ASC",
            (account_id,)
        )
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
    finally:
        conn.close()


@users_router.delete("/{user_id}")
def delete_user(user_id: int, account_id: int = Depends(get_current_account_id)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE id = %s AND account_id = %s",
            (user_id, account_id)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Not found or does not belong to you")
        cursor.execute(
            "DELETE FROM users WHERE id = %s AND account_id = %s",
            (user_id, account_id)
        )
        conn.commit()
        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        conn.close()