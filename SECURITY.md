# Security Considerations

## ⚠️ Important: This is a Development Setup

The current implementation is designed for **development and testing**. Before deploying to production, implement the following security measures:

## 1. CORS Configuration

**Current (Development):**
```python
allow_origins=["*"]  # Allows any domain
```

**Production Fix:**
```python
# api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],  # Specific domains only
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

## 2. Authentication & Authorization

**Current:** No authentication (anyone can call the API)

**Production Options:**

### Option A: API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Apply to endpoint
@app.post("/api/generate-blog")
def generate_blog(
    request: BlogGenerationRequest,
    api_key: str = Security(verify_api_key)
):
    # ... existing code
```

**Usage:**
```bash
curl -X POST http://localhost:8077/api/generate-blog \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"topic": "...", ...}'
```

### Option B: JWT Authentication

```python
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/generate-blog")
def generate_blog(
    request: BlogGenerationRequest,
    user = Depends(verify_token)
):
    # ... existing code
```

### Option C: OAuth2 / Auth0

For production apps with user management, integrate OAuth2:

```python
from fastapi_auth0 import Auth0, Auth0User

auth = Auth0(domain='your-domain.auth0.com', api_audience='your-api-audience')

@app.post("/api/generate-blog")
def generate_blog(
    request: BlogGenerationRequest,
    user: Auth0User = Depends(auth.get_user)
):
    # ... existing code
```

## 3. Rate Limiting

**Current:** No rate limiting (abuse risk)

**Production Fix:**

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/generate-blog")
@limiter.limit("5/hour")  # 5 requests per hour per IP
def generate_blog(request: Request, blog_request: BlogGenerationRequest):
    # ... existing code
```

## 4. Error Information Disclosure

**Current:** Detailed error messages expose internal details

**Production Fix:**

```python
@app.post("/api/generate-blog")
def generate_blog(request: BlogGenerationRequest):
    try:
        # ... existing code
    except Exception as e:
        # Log detailed error internally
        import logging
        logging.error(f"Blog generation failed: {str(e)}", exc_info=True)
        
        # Return generic error to client
        raise HTTPException(
            status_code=500,
            detail="Blog generation failed. Please try again later."
        )
```

## 5. Input Validation

**Current:** Basic Pydantic validation

**Additional Production Checks:**

```python
from fastapi import HTTPException
import re

@app.post("/api/generate-blog")
def generate_blog(request: BlogGenerationRequest):
    # Sanitize topic (prevent injection)
    if not re.match(r'^[a-zA-Z0-9\s\-\?\!,\.]+$', request.topic):
        raise HTTPException(
            status_code=400,
            detail="Topic contains invalid characters"
        )
    
    # Limit keywords
    if len(request.keywords) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 keywords allowed"
        )
    
    # ... existing code
```

## 6. HTTPS Only

**Production:** Always use HTTPS

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

## 7. API Key Storage

**Never hardcode API keys in code!**

```bash
# Use environment variables
export GROQ_API_KEY="your-key"
export API_KEY="your-api-key"
export JWT_SECRET="your-jwt-secret"

# Or use .env file (never commit to git!)
echo "GROQ_API_KEY=..." >> .env
echo "API_KEY=..." >> .env
```

Ensure `.env` is in `.gitignore`:
```bash
echo ".env" >> .gitignore
```

## 8. Request Logging & Monitoring

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/generate-blog")
def generate_blog(request: BlogGenerationRequest):
    # Log request (sanitize sensitive data)
    logger.info(f"Blog generation request: topic={request.topic[:50]}")
    
    try:
        # ... existing code
        logger.info(f"Blog generated successfully: {result['word_count']} words")
        return result
    except Exception as e:
        logger.error(f"Blog generation failed: {str(e)}")
        raise
```

## 9. Production Deployment Checklist

- [ ] Configure specific CORS origins
- [ ] Add authentication (API key, JWT, or OAuth)
- [ ] Implement rate limiting
- [ ] Use HTTPS only
- [ ] Sanitize error messages
- [ ] Add request logging
- [ ] Use environment variables for secrets
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Add request timeout limits
- [ ] Implement caching (Redis)
- [ ] Use production WSGI server (Gunicorn)
- [ ] Set up firewall rules
- [ ] Enable CSRF protection (if using cookies)

## 10. Production Server Setup

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8077 \
  --timeout 180 \
  --access-logfile /var/log/api/access.log \
  --error-logfile /var/log/api/error.log
```

## Docker Production Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Switch to non-root user
USER appuser

# Production server
CMD ["gunicorn", "api:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8077"]
```

## Environment-Specific Config

```python
# config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    groq_api_key: str
    api_key: str = ""
    jwt_secret: str = ""
    allowed_origins: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()

# api.py
from config import settings

if settings.environment == "production":
    if not settings.api_key:
        raise ValueError("API_KEY required in production")
```

## Summary

**Development (Current):**
- ✅ Fast iteration
- ✅ Easy testing
- ⚠️ No security

**Production (Required):**
- ✅ CORS restrictions
- ✅ Authentication
- ✅ Rate limiting
- ✅ HTTPS only
- ✅ Error sanitization
- ✅ Monitoring
- ✅ Non-root user
- ✅ Secret management

**Remember:** Security is not optional for production deployments!
