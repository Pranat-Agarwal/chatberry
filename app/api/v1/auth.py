from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User

router = APIRouter()

# ---------- Schemas ----------
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


# ---------- SIGNUP ----------
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):

    # ✅ check username
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # ✅ check email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "username": user.username
    }


# ---------- LOGIN ----------
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "username": user.username
    }
