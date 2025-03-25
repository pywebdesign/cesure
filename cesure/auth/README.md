# Authentication System

This module provides authentication capabilities including:

- Standard username/password authentication with JWT tokens
- OAuth integration with Google
- OAuth integration with Facebook

## Configuration

For production deployment, make sure to:

1. Change the `SECRET_KEY` in `utils.py`
2. Set proper OAuth client IDs and secrets for Google and Facebook in `oauth.py`
3. Update redirect URIs to match your production domain

## Endpoints

### Standard Authentication
- `POST /auth/token` - Get JWT token with username/password
- `GET /users/me` - Get current user info
- `PUT /users/me` - Update current user

### OAuth Authentication
- `GET /auth/google` - Get Google OAuth URL
- `POST /auth/google/callback` - Handle Google OAuth callback
- `GET /auth/facebook` - Get Facebook OAuth URL
- `POST /auth/facebook/callback` - Handle Facebook OAuth callback

### User Management (Admin Only)
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get specific user
- `PUT /users/{user_id}` - Update specific user
- `DELETE /users/{user_id}` - Delete specific user
