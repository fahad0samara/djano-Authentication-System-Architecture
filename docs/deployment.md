# Deployment Guide

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

## Environment Variables

Required environment variables:

```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
EMAIL_HOST=smtp.provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## Production Checklist

- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up SSL/TLS
- [ ] Configure email backend
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Set up logging
- [ ] Review security settings