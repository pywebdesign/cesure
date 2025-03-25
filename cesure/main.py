from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import os

from .models.base import engine, SessionLocal, get_db
from .models import artist, artwork, competition, event, user
from .auth import routes as user_routes
from .auth import oauth as oauth_routes
from .auth.utils import get_current_user
from .middleware import AuthMiddleware

# Create database tables (comment out if using Alembic migrations)
# artist.Base.metadata.create_all(bind=engine)
# artwork.Base.metadata.create_all(bind=engine)
# competition.Base.metadata.create_all(bind=engine)
# event.Base.metadata.create_all(bind=engine)
# user.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cesure Art Gallery API")

# Set up template directory
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_path, exist_ok=True)  # Create static directory if it doesn't exist
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(user_routes.router)
app.include_router(user_routes.auth_router)  # Auth and Email verification routes
app.include_router(oauth_routes.router)

# Define exception handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "status_code": 404,
            "title": "Page Not Found",
            "message": "The page you're looking for doesn't exist."
        },
        status_code=404
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "status_code": 500,
            "title": "Server Error",
            "message": "Something went wrong on our end. Please try again later."
        },
        status_code=500
    )

@app.get("/")
async def root(request: Request):
    try:
        # Try to get the current user from the token
        token = request.cookies.get("access_token", "")
        if token:
            token = token.replace("Bearer ", "")
            user = await get_current_user(token, next(get_db()))
            # If successful, user is logged in, show the welcome page
            return templates.TemplateResponse("welcome.html", {"request": request, "user": user})
        else:
            # No token found, show public home page
            return templates.TemplateResponse("home.html", {"request": request})
    except:
        # If token is invalid or expired, show public home page
        return templates.TemplateResponse("home.html", {"request": request})

@app.get("/health")
async def health_check():
    db_url = os.environ.get("DATABASE_URL", "Not set")
    return {
        "status": "healthy",
        "db_connection": db_url.replace(db_url.split("@")[0], "***")
    }

# Include any additional routes here