from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import re

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication and protected routes.
    Redirects to login page for protected routes if user is not authenticated.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Define paths that don't require authentication
        public_paths = [
            r"^/auth/login",
            r"^/auth/register",
            r"^/auth/verify-email",
            r"^/auth/token",
            r"^/auth/google",
            r"^/auth/facebook",
            r"^/docs",
            r"^/redoc",
            r"^/openapi.json",
            r"^/$",
            r"^/health",
            r"^/static/",
        ]
        
        # Check if path is public
        path = request.url.path
        is_public = any(re.match(pattern, path) for pattern in public_paths)
        
        # Check if API request (not HTML)
        is_api = path.startswith("/api") or "application/json" in request.headers.get("accept", "")
        
        # If path is protected and no auth token, redirect to login
        if not is_public and not is_api:
            # Check for auth token in cookie
            has_token = "access_token" in request.cookies
            
            if not has_token:
                # Redirect to login if no token and route requires auth
                return RedirectResponse(url="/auth/login", status_code=302)
        
        # Process the request normally
        response = await call_next(request)
        return response