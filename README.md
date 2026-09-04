# LangGraph Blog Generator API

AI-powered blog generation REST API using LangGraph, LangChain, and Groq.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
echo "GROQ_API_KEY=your_key_here" > .env

# Run
uvicorn api:app --host 0.0.0.0 --port 8077
```

Server: `http://localhost:8077`  
Docs: `http://localhost:8077/docs`

## API

### Generate Blog

```bash
POST /api/generate-blog
Content-Type: application/json

{
  "topic": "How to Test Electrical Outlets",
  "category": "troubleshooting",
  "keywords": ["outlet", "testing", "safety"],
  "target_audience": "homeowners"
}
```

**Response:**
```json
{
  "success": true,
  "title": "SEO-Optimized Title",
  "content": "# Full markdown content (1200-1800 words)",
  "meta_description": "SEO description",
  "category": "troubleshooting",
  "keywords": ["outlet", "testing", "safety"],
  "outline": "## Outline",
  "word_count": 1485,
  "revisions": 0,
  "review_status": "APPROVED",
  "review_feedback": "Reviewer notes",
  "generated_at": "2026-09-04T11:02:28.265207",
  "target_audience": "homeowners"
}
```

### Health Check

```bash
GET /health

Response: {"status": "healthy", ...}
```

## Frontend Integration

**The `content` field is markdown.** Parse it in your frontend:

### React Example

```jsx
import ReactMarkdown from 'react-markdown';

function BlogDisplay({ blog }) {
  return (
    <div>
      <h1>{blog.title}</h1>
      <p>{blog.meta_description}</p>
      <ReactMarkdown>{blog.content}</ReactMarkdown>
    </div>
  );
}
```

```bash
npm install react-markdown
```

### Vanilla JS Example

```javascript
import { marked } from 'marked';

const html = marked(blog.content);
document.getElementById('blog').innerHTML = html;
```

```bash
npm install marked
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Generation succeeded |
| `title` | string | SEO title (≤60 chars) |
| `content` | **string (markdown)** | Full blog content |
| `meta_description` | string | SEO meta (≤160 chars) |
| `category` | string | Category |
| `keywords` | array | Keywords |
| `outline` | string | Outline used |
| `word_count` | integer | Total words |
| `revisions` | integer | Revisions made (0-3) |
| `review_status` | string | APPROVED / ACCEPTED |
| `review_feedback` | string | Reviewer notes |
| `generated_at` | string | ISO timestamp |
| `target_audience` | string | Audience |

## Architecture

```
┌─────────────────┐
│  Outline Node   │ Creates structure
└────────┬────────┘
         ↓
┌─────────────────┐
│  Writer Node    │ Generates content (JSON format)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Reviewer Node  │ Quality check (JSON format)
└────────┬────────┘
         ↓
    [Approved?]
    Yes ↓   No → (revise, max 3x)
         ↓
┌─────────────────┐
│ Finalizer Node  │ Package output
└─────────────────┘
```

## Configuration

### Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key  # Required
```

### CORS (Production)

Update `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your domain
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

## Security Notes

⚠️ **Development setup** - For production:

1. **CORS**: Set specific origins (not `["*"]`)
2. **Authentication**: Add API keys/JWT
3. **Rate Limiting**: Prevent abuse
4. **HTTPS**: Use SSL certificates
5. **Error Messages**: Don't expose internals

See `SECURITY.md` for details.

## Performance

- **Generation**: 30-60 seconds
- **Word Count**: 1200-1800 words
- **Max Revisions**: 3
- **Rate Limit**: 8000 tokens/min (Groq free tier)

## Testing

```bash
# Health
curl http://localhost:8077/health

# Generate
curl -X POST http://localhost:8077/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{"topic":"Test","keywords":["test"]}'
```

## Project Structure

```
.
├── api.py              # FastAPI application
├── src/
│   ├── state.py        # BlogState TypedDict
│   ├── graph.py        # LangGraph workflow
│   └── nodes/          # Individual nodes
├── tests/              # Test suite
├── .env                # API keys (gitignored)
└── README.md           # This file
```

## Dependencies

- **LangGraph** - Workflow orchestration
- **LangChain** - LLM integration  
- **Groq** - Content generation
- **FastAPI** - REST API
- **Pydantic** - Validation

## CLI (Legacy)

Original CLI still works:

```bash
python main.py "Topic" --category troubleshooting --keywords "key1,key2"
```

Saves markdown file to `output/` directory.

## License

MIT
