from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import httpx
from pydantic import BaseModel
from typing import Optional
import json

from ..models.base import get_db
from ..models.user import User
from .utils import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, Token

# OAuth configuration
GOOGLE_CLIENT_ID = "GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "GOOGLE_CLIENT_SECRET"
GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google/callback"

FACEBOOK_CLIENT_ID = "FACEBOOK_CLIENT_ID"
FACEBOOK_CLIENT_SECRET = "FACEBOOK_CLIENT_SECRET"
FACEBOOK_REDIRECT_URI = "http://localhost:8000/auth/facebook/callback"


class OAuthRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified for password login
    # For security reasons, we still create a token but return a clear message
    if not user.email_verified:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        # We return a token, but also include a warning
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "email_verified": False,
            "message": "Email not verified. Please verify your email to access all features."
        }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "email_verified": True}


@router.get("/google")
async def google_login():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20email%20profile&access_type=offline"
    }


@router.post("/google/callback", response_model=Token)
async def google_callback(request: OAuthRequest, db: Session = Depends(get_db)):
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": request.code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": request.redirect_uri or GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_data = token_response.json()
        
        if "error" in token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get Google token: {token_data['error']}",
            )
            
        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_info = user_response.json()
        
    # Check if user exists
    user = db.query(User).filter(User.email == user_info["email"]).first()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            username=user_info["email"].split("@")[0],  # Using email username as username
            full_name=user_info.get("name", ""),
            # Generate a random password hash that can't be used to login directly
            password_hash="OAUTH_USER",  
            is_active=True,
            email_verified=True,  # OAuth-verified emails are considered verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/facebook")
async def facebook_login():
    return {
        "url": f"https://www.facebook.com/v17.0/dialog/oauth?client_id={FACEBOOK_CLIENT_ID}&redirect_uri={FACEBOOK_REDIRECT_URI}&scope=email,public_profile"
    }


@router.post("/facebook/callback", response_model=Token)
async def facebook_callback(request: OAuthRequest, db: Session = Depends(get_db)):
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.get(
            "https://graph.facebook.com/v17.0/oauth/access_token",
            params={
                "client_id": FACEBOOK_CLIENT_ID,
                "client_secret": FACEBOOK_CLIENT_SECRET,
                "redirect_uri": request.redirect_uri or FACEBOOK_REDIRECT_URI,
                "code": request.code,
            },
        )
        token_data = token_response.json()
        
        if "error" in token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get Facebook token: {token_data['error']['message']}",
            )
            
        # Get user info
        user_response = await client.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,name,email",
                "access_token": token_data["access_token"],
            },
        )
        user_info = user_response.json()
        
    if "email" not in user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Facebook",
        )
        
    # Check if user exists
    user = db.query(User).filter(User.email == user_info["email"]).first()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            username=f"fb_{user_info['id']}",  # Using Facebook ID as username
            full_name=user_info.get("name", ""),
            # Generate a random password hash that can't be used to login directly
            password_hash="OAUTH_USER",  
            is_active=True,
            email_verified=True,  # OAuth-verified emails are considered verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
