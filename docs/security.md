# Security Features

## Password Security

- Minimum length: 10 characters
- Required complexity:
  - Uppercase letters
  - Lowercase letters
  - Numbers
  - Special characters
- Password history enforcement
- Bcrypt hashing with per-user salt

## Two-Factor Authentication

- TOTP-based 2FA
- Backup codes
- Device trust system
- QR code setup

## Session Security

- Session timeout after 30 minutes of inactivity
- Concurrent session limiting
- Device fingerprinting
- Secure session storage

## Brute Force Protection

- Account lockout after 5 failed attempts
- IP-based rate limiting
- Suspicious activity monitoring
- Security notifications

## Audit Logging

- Login attempts
- Security-related actions
- IP address tracking
- Device information
- Geographic location (when available)

## API Security

- JWT authentication
- Rate limiting
- CORS configuration
- Input validation
- Request size limiting