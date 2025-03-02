# API Documentation

## Authentication

### Login
`POST /api/auth/login/`

Login with username/email and password.

**Request:**
```json
{
    "email": "user@example.com",
    "password": "secure-password"
}
```

**Response:**
```json
{
    "token": "jwt-token",
    "user": {
        "id": 1,
        "username": "user",
        "email": "user@example.com"
    }
}
```

### Two-Factor Authentication
`POST /api/auth/2fa/verify/`

Verify 2FA code.

**Request:**
```json
{
    "code": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "session_token": "session-token"
}
```

## User Management

### Get User Profile
`GET /api/users/me/`

Get current user's profile.

**Response:**
```json
{
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "two_factor_enabled": true,
    "last_login": "2024-01-20T12:00:00Z"
}
```

### Update Profile
`PATCH /api/users/me/`

Update user profile.

**Request:**
```json
{
    "username": "newusername"
}
```

For complete API documentation, see our [Swagger UI](/api/docs/).