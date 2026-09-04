# LangGraph Blog Generator

Multi-node AI workflow for generating SEO-optimized electrical blog posts using LangGraph and Groq (Llama 3.1 405B).

## Architecture

```
┌─────────────────┐
│  Outline Node   │ - Creates structured outline
└────────┬────────┘
         ↓
┌─────────────────┐
│  Writer Node    │ - Generates 1200-1800 word content
└────────┬────────┘
         ↓
┌─────────────────┐
│  Reviewer Node  │ - Checks quality & SEO
└────────┬────────┘
         ↓
    [Approved?]
    Yes ↓   No → (revise, max 2x)
         ↓
┌─────────────────┐
│ Finalizer Node  │ - Packages output
└─────────────────┘
```

## Features

- **Multi-node workflow** - Outline → Write → Review → Finalize
- **Quality control** - Automated reviewer with 8 criteria
- **Iterative revision** - Up to 2 automatic revisions based on feedback
- **SEO optimized** - Title, meta, keywords validated
- **LangGraph orchestration** - Conditional edges and state management

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env: GROQ_API_KEY=your-groq-api-key
```

## Usage

```bash
python main.py "Topic Title" \
  --category CATEGORY \
  --keywords "keyword1,keyword2,keyword3"
```

**Example:**

```bash
python main.py "Why Does My Circuit Breaker Keep Tripping?" \
  --category troubleshooting \
  --keywords "circuit breaker,tripping,electrical overload"
```

**Output:**

```
🤖 LangGraph Blog Generator
======================================================================

📝 Topic: Why Does My Circuit Breaker Keep Tripping?
   Category: troubleshooting
   Keywords: circuit breaker, tripping, electrical overload
   Audience: homeowners

🔄 Starting multi-node workflow...

   [1/4] 📋 Generating outline...
   [2/4] ✍️  Writing content...
   [3/4] 🔍 Reviewing quality...
   [4/4] ✅ Finalizing...

======================================================================

✅ Blog post generated successfully!

📊 Workflow Stats:
   Revisions: 0
   Review: APPROVED

📄 Final Output:
   Title: Why Does My Circuit Breaker Keep Tripping? 7 Common Causes
   Meta: Learn the 7 most common reasons your circuit breaker trips.
   Keywords: circuit breaker, tripping, electrical overload
   Length: 1523 words

💾 Saved to: output/why-does-my-circuit-breaker-keep-tripping.md

📝 Review Feedback:
   ✓ SEO optimized title and meta ✓ Keywords naturally integrated...

======================================================================
✅ Complete!
```

## Review Criteria

The reviewer node checks:

1. **SEO** - Title < 60 chars, meta < 160 chars, keyword integration
2. **Length** - 1200-1800 words
3. **Structure** - Clear headers, numbered lists
4. **Safety** - Warnings where appropriate
5. **Audience** - Accessible language
6. **Call-to-Action** - Clear service invitation
7. **Accuracy** - Technically sound
8. **Completeness** - All sections covered

## Workflow Details

### Node 1: Outline Generator
- Creates structured outline
- 5-7 main sections
- Safety and CTA sections

### Node 2: Content Writer
- Generates 1200-1800 words
- Follows outline structure
- Incorporates keywords naturally
- Can revise based on feedback

### Node 3: Content Reviewer
- Reviews against 8 criteria
- Returns APPROVED: YES/NO
- Provides specific feedback
- Scores quality 0-10

### Node 4: Finalizer
- Packages approved content
- Adds final metadata
- Prepares for publication

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
.
├── src/
│   ├── state.py                    # BlogState TypedDict
│   ├── graph.py                    # LangGraph workflow
│   └── nodes/
│       ├── outline_generator.py
│       ├── content_writer.py
│       ├── content_reviewer.py
│       └── finalizer.py
├── tests/
├── output/                         # Generated blogs
├── main.py                         # CLI
└── README.md
```

## Dependencies

- **LangGraph** - Workflow orchestration
- **LangChain** - LLM integration
- **Groq API** - Content generation (Llama 3.1 405B Reasoning)

## License

MIT
