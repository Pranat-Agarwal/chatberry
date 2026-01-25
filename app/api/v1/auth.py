from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.models.user import User

router = APIRouter()

MAX_PASSWORD_BYTES = 72  # bcrypt limit


# -------------------------------------------------
# SIGNUP
# -------------------------------------------------

@router.post("/signup")
def signup(data: dict, db: Session = Depends(get_db)):
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="All fields required")

    # 🔒 Password length check (bcrypt safe)
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Password too long. Maximum {MAX_PASSWORD_BYTES} characters allowed."
        )

    # Check duplicate username
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=400,
            detail=f"Username '{username}' already exists"
        )

    # Check duplicate email
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "username": user.username
    }


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "username": user.username
    }
