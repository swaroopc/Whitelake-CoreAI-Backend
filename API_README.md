# Blog Generator REST API

FastAPI-based REST API for AI-powered blog generation using LangGraph and Groq.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` file has your Groq API key:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Start API Server

```bash
# Development mode (auto-reload)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at: `http://localhost:8077`

## 📡 API Endpoints

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "blog-generator-api",
  "timestamp": "2026-09-04T10:35:11.480100"
}
```

### Generate Blog

```bash
POST /api/generate-blog
```

**Request Body:**
```json
{
  "topic": "How to Test Electrical Outlets Safely",
  "category": "troubleshooting",
  "keywords": ["outlet", "testing", "safety", "electrical"],
  "target_audience": "homeowners"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "title": "How to Safely Test Your Home Electrical Outlets",
  "content": "# How to Safely Test Your Home Electrical Outlets\n\n...",
  "meta_description": "Learn how to safely test electrical outlets...",
  "category": "troubleshooting",
  "keywords": ["outlet", "testing", "safety", "electrical"],
  "outline": "## Introduction\n## Testing Steps\n## Conclusion",
  "word_count": 1485,
  "revisions": 0,
  "review_status": "APPROVED",
  "review_feedback": "Excellent quality, ready to publish",
  "generated_at": "2026-09-04T10:35:11.480100",
  "target_audience": "homeowners"
}
```

## 🧪 Testing

### Using Python Script

```bash
python test_api.py
```

### Using cURL

```bash
# Health check
curl http://localhost:8077/health

# Generate blog
curl -X POST http://localhost:8077/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Why Circuit Breakers Trip",
    "category": "troubleshooting",
    "keywords": ["circuit breaker", "electrical", "safety"],
    "target_audience": "homeowners"
  }'
```

### Using Frontend (JavaScript/React)

```javascript
// Example fetch call
const generateBlog = async (topic, keywords) => {
  const response = await fetch('http://localhost:8077/api/generate-blog', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      topic: topic,
      category: 'troubleshooting',
      keywords: keywords,
      target_audience: 'homeowners'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Title:', data.title);
    console.log('Content:', data.content);
    console.log('Word Count:', data.word_count);
    // Use data in your frontend...
  }
};

// Usage
generateBlog(
  "How to Test Electrical Outlets", 
  ["outlet", "testing", "safety"]
);
```

## 📊 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether generation succeeded |
| `title` | string | SEO-optimized blog title (≤60 chars) |
| `content` | string | Full markdown blog content (1200-1800 words) |
| `meta_description` | string | Meta description for SEO (≤160 chars) |
| `category` | string | Blog category |
| `keywords` | array | Target keywords used |
| `outline` | string | Blog outline (markdown) |
| `word_count` | integer | Total word count |
| `revisions` | integer | Number of revisions made (0-3) |
| `review_status` | string | "APPROVED" or "ACCEPTED (max revisions)" |
| `review_feedback` | string | Reviewer feedback/comments |
| `generated_at` | string | ISO 8601 timestamp |
| `target_audience` | string | Target audience |

## ⚙️ API Documentation

Interactive API docs available at:

- **Swagger UI**: `http://localhost:8077/docs`
- **ReDoc**: `http://localhost:8077/redoc`

## 🔒 Production Considerations

### CORS Configuration

Update `allow_origins` in `api.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### Rate Limiting

Groq free tier has rate limits (8000 tokens/min). Consider:

- Implementing request queue
- Adding rate limiting middleware
- Caching responses
- Upgrading to Groq paid tier

### Error Handling

API returns 500 with error details:

```json
{
  "detail": "Blog generation failed: Rate limit exceeded"
}
```

### Deployment

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    restart: unless-stopped
```

## 📈 Performance

- **Average Generation Time**: 30-60 seconds
- **Timeout**: 180 seconds (configurable)
- **Max Word Count**: ~1800 words
- **Max Revisions**: 3 (configurable in `src/graph.py`)

## 🛠️ Troubleshooting

**API won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn api:app --port 8001
```

**Rate limit errors:**
- Wait 60 seconds between requests
- Upgrade Groq API tier
- Use different model with higher limits

**Empty response:**
- Check `GROQ_API_KEY` is set
- Verify API key is valid
- Check Groq API status

## 📝 License

MIT
