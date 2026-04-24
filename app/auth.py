from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status

# Yangi router (bu /auth/refresh ishlashi uchun kerak)
router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "super_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token 30 daqiqa (qisqa)
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh token 7 kun (uzun)

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

# ✅ Yangilangan create_tokens (ikkala tokenni generatsiya qiladi)
def create_tokens(data: dict):
    # Access Token yaratish
    access_to_encode = data.copy()
    access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_to_encode.update({"exp": access_expire, "type": "access"})
    access_token = jwt.encode(access_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh Token yaratish
    refresh_to_encode = data.copy()
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_to_encode.update({"exp": refresh_expire, "type": "refresh"})
    refresh_token = jwt.encode(refresh_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token

# ✅ YANGI ENDPOINT: Tokenni yangilash uchun
@router.post("/refresh")
async def refresh_access_token(payload: dict):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token topilmadi")
    
    try:
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Token turi Refresh ekanligini tekshiramiz
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token turi noto'g'ri")
            
        user_email = decoded.get("sub")
        
        # Yangi faqat Access Token yaratamiz
        new_access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = jwt.encode(
            {"sub": user_email, "exp": new_access_expire, "type": "access"}, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        
        return {"access_token": new_access_token}
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token muddati tugagan")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None