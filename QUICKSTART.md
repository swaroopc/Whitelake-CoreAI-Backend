# 🚀 Quick Start Guide - Blog Generator API

## ✅ **What You Have**

A **FastAPI REST API** that generates SEO-optimized blog posts using:
- **LangGraph** (multi-node workflow)
- **Groq API** (openai/gpt-oss-120b model)
- **JSON response** (ready for frontend integration)

## 📋 **Prerequisites**

```bash
# 1. Python 3.11+
python --version

# 2. Groq API Key
# Get from: https://console.groq.com
```

## 🔧 **Setup (First Time)**

```bash
# 1. Clone/navigate to project
cd /home/swarocha/dev/Core-AI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

## 🚀 **Start API Server**

```bash
# Method 1: Direct run (development)
uvicorn api:app --reload --host 0.0.0.0 --port 8077

# Method 2: Python script
python api.py

# Method 3: Custom port
uvicorn api:app --port 8001
```

**Server runs at:** `http://localhost:8077`

## 📡 **API Endpoints**

### 1. Health Check

```bash
GET http://localhost:8077/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "blog-generator-api",
  "timestamp": "2026-09-04T10:55:02.223151"
}
```

### 2. Generate Blog

```bash
POST http://localhost:8000/api/generate-blog
Content-Type: application/json
```

**Request:**
```json
{
  "topic": "How to Test Electrical Outlets Safely",
  "category": "troubleshooting",
  "keywords": ["outlet", "testing", "safety"],
  "target_audience": "homeowners"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "title": "How to Safely Test Your Home Electrical Outlets",
  "content": "# How to Safely Test...\n\n[1200-1800 words]",
  "meta_description": "Learn how to safely test...",
  "category": "troubleshooting",
  "keywords": ["outlet", "testing", "safety"],
  "outline": "## Introduction\n## Steps...",
  "word_count": 1485,
  "revisions": 0,
  "review_status": "APPROVED",
  "review_feedback": "Excellent quality...",
  "generated_at": "2026-09-04T10:55:02.223151",
  "target_audience": "homeowners"
}
```

## 🧪 **Testing**

### Using Python Test Script

```bash
python test_api.py
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Generate blog
curl -X POST http://localhost:8077/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Why Circuit Breakers Trip",
    "category": "troubleshooting",
    "keywords": ["circuit breaker", "electrical"],
    "target_audience": "homeowners"
  }' | jq
```

### Using JavaScript/Frontend

```javascript
const response = await fetch('http://localhost:8077/api/generate-blog', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: "How to Test Electrical Outlets",
    category: "troubleshooting",
    keywords: ["outlet", "testing", "safety"],
    target_audience: "homeowners"
  })
});

const blog = await response.json();
console.log(blog.title);        // "How to Safely Test..."
console.log(blog.word_count);   // 1485
console.log(blog.content);      // Full markdown content
```

## 📊 **Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether generation succeeded |
| `title` | string | SEO title (≤60 chars) |
| `content` | string | Full markdown blog (1200-1800 words) |
| `meta_description` | string | Meta description (≤160 chars) |
| `category` | string | Blog category |
| `keywords` | array | Target keywords |
| `outline` | string | Blog outline (markdown) |
| `word_count` | integer | Total words |
| `revisions` | integer | Revisions made (0-3) |
| `review_status` | string | "APPROVED" or "ACCEPTED (max revisions)" |
| `review_feedback` | string | Reviewer comments |
| `generated_at` | string | ISO timestamp |
| `target_audience` | string | Target audience |

## 🎯 **Frontend Integration**

### React Example

```jsx
import { useState } from 'react';

function BlogGenerator() {
  const [loading, setLoading] = useState(false);
  const [blog, setBlog] = useState(null);

  const generateBlog = async (topic, keywords) => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8077/api/generate-blog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          category: 'troubleshooting',
          keywords,
          target_audience: 'homeowners'
        })
      });
      
      const data = await res.json();
      setBlog(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>Generating blog (30-60s)...</p>}
      {blog && (
        <div>
          <h1>{blog.title}</h1>
          <p>Word Count: {blog.word_count} | Revisions: {blog.revisions}</p>
          <div dangerouslySetInnerHTML={{ __html: marked(blog.content) }} />
        </div>
      )}
    </div>
  );
}
```

## 📖 **Interactive Docs**

Open in browser:

- **Swagger UI**: `http://localhost:8077/docs`
- **ReDoc**: `http://localhost:8077/redoc`

Try the API directly from the browser!

## ⚡ **Performance**

- **Generation Time**: 30-60 seconds
- **Word Count**: 1200-1800 words
- **Max Revisions**: 3 (configurable)
- **Rate Limit**: 8000 tokens/min (Groq free tier)

## 🛑 **Stop Server**

```bash
# Find process
ps aux | grep uvicorn

# Kill by PID
kill <PID>

# Or use Ctrl+C in terminal
```

## 🔒 **Production Tips**

1. **CORS**: Update `allow_origins` in `api.py`
2. **Rate Limiting**: Add rate limiting middleware
3. **Authentication**: Add API keys/JWT
4. **Caching**: Cache responses to reduce costs
5. **Queue**: Use Celery/Redis for long-running tasks
6. **Monitoring**: Add logging, Sentry, DataDog

## 📚 **Documentation**

- **API Docs**: See `API_README.md`
- **Full Plan**: See `docs/superpowers/plans/2026-09-03-langgraph-blog-generator.md`
- **Code**: Browse `src/` directory

## ❓ **Troubleshooting**

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8077 | xargs kill -9

# Or use different port
uvicorn api:app --port 8078
```

**Rate limit errors:**
```bash
# Wait 60 seconds between requests
# Or upgrade Groq API tier
```

**Empty response:**
```bash
# Check API key
cat .env

# Verify server is running
curl http://localhost:8000/health
```

## 🎉 **Success!**

You now have a **production-ready REST API** for AI blog generation!

**Next steps:**
1. Integrate with your frontend
2. Customize prompts in `src/nodes/`
3. Add more categories/templates
4. Deploy to cloud (AWS, GCP, Heroku)
