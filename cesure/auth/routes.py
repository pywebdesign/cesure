from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import os

from ..models.base import get_db
from ..models.user import User
from .utils import (
    get_password_hash, get_current_active_user, get_current_admin_user,
    create_verification_token, verify_email_token, get_current_verified_user,
    authenticate_user, create_access_token, Token
)
from .email import send_verification_email
from datetime import timedelta

# Set up templates
templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_path)

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    email_verified: bool


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Create the user with email_verified set to False
        db_user = User(
            email=user.email,
            password_hash=get_password_hash(user.password),
            username=user.username,
            full_name=user.full_name,
            is_active=True,
            is_admin=False,
            email_verified=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Generate verification token and send email
        token = create_verification_token(db, db_user)
        send_verification_email(db_user.id, db_user.email, token)
        
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserRead)
async def update_user_me(user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    try:
        if user.email:
            current_user.email = user.email
        if user.username:
            current_user.username = user.username
        if user.full_name:
            current_user.full_name = user.full_name
        if user.password:
            current_user.password_hash = get_password_hash(user.password)
            
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already taken",
        )


@router.get("/", response_model=list[UserRead])
async def read_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user: UserUpdate, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        if user.email:
            db_user.email = user.email
        if user.username:
            db_user.username = user.username
        if user.full_name:
            db_user.full_name = user.full_name
        if user.password:
            db_user.password_hash = get_password_hash(user.password)
            
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already taken",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(db_user)
    db.commit()
    return None


# Web UI routes
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """Render the login page"""
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@auth_router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Incorrect email or password"}
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Set cookie and redirect
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return response

@auth_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = None):
    """Render the registration page"""
    return templates.TemplateResponse("register.html", {"request": request, "error": error})

@auth_router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    full_name: str = Form(None),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration form submission"""
    # Validate passwords match
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Passwords do not match"}
        )
    
    # Create user
    try:
        db_user = User(
            email=email,
            password_hash=get_password_hash(password),
            username=username,
            full_name=full_name,
            is_active=True,
            is_admin=False,
            email_verified=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Generate verification token and send email
        token = create_verification_token(db, db_user)
        send_verification_email(db_user.id, db_user.email, token)
        
        # Redirect to login page with success message
        return RedirectResponse(
            url="/auth/login?success=Registration successful! Please check your email to verify your account.",
            status_code=status.HTTP_302_FOUND
        )
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Email or username already registered"}
        )

@auth_router.get("/logout")
async def logout():
    """Log out the user by clearing the session cookie"""
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

# API endpoints
@auth_router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify a user's email with the provided token"""
    user = verify_email_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    return {"message": "Email verified successfully"}


@auth_router.post("/resend-verification")
async def resend_verification(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Resend the verification email to the current user"""
    if current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    token = create_verification_token(db, current_user)
    success = send_verification_email(current_user.id, current_user.email, token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return {"message": "Verification email sent"}
