from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth import verify_password, get_password_hash, create_token

router = APIRouter()

@router.post("/register")
def register(form: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(
        username=form.username,
        hashed_password=get_password_hash(form.password)
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User created successfully"}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

