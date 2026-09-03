# LangGraph Blog Generator - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build blog generator using LangGraph framework with multiple nodes: outline → draft → review → finalize.

**Architecture:** LangGraph state machine with 4 nodes - Outline Generator, Content Writer, Content Reviewer, Finalizer. Uses LangChain for Claude API integration.

**Tech Stack:** 
- Python 3.11+
- LangGraph (workflow orchestration)
- LangChain (LLM integration)
- Claude API (Anthropic)

**Spec:** `/home/swarocha/dev/Core-AI/objective.md` — electrical blog content generation.

## Global Constraints

- Python version: >= 3.11
- LangGraph: langgraph >= 0.2.0
- LangChain: langchain >= 0.3.0
- Claude model: claude-sonnet-4-5-20250929
- Blog length: 1200-1800 words

---

## Graph Architecture

```
START
  ↓
[Outline Generator Node]
  ↓
[Content Writer Node]
  ↓
[Content Reviewer Node]
  ↓ (approved)
[Finalizer Node]
  ↓
END

(reviewer can loop back to writer if issues found)
```

---

## Task 1: Setup & State Definition

**Files:**
- Create: `src/__init__.py`
- Create: `src/state.py`
- Create: `requirements.txt`
- Create: `.env.example`

**Interfaces:**
- Consumes: None (foundation)
- Produces: 
  - `BlogState` TypedDict for graph state
  - Project dependencies

- [ ] **Step 1: Create project structure**

```bash
mkdir -p src output tests
touch src/__init__.py
```

- [ ] **Step 2: Create requirements file**

```text
# requirements.txt
langgraph>=0.2.0
langchain>=0.3.0
langchain-anthropic>=0.3.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

- [ ] **Step 3: Define graph state**

```python
# src/state.py
from typing import TypedDict, List, Optional

class BlogState(TypedDict):
    """State passed between graph nodes"""
    
    # Input
    topic_title: str
    category: str
    keywords: List[str]
    target_audience: str
    
    # Outline node
    outline: Optional[str]
    
    # Writer node
    draft_title: Optional[str]
    draft_content: Optional[str]
    draft_meta: Optional[str]
    
    # Reviewer node
    review_approved: bool
    review_feedback: Optional[str]
    revision_count: int
    
    # Final output
    final_title: Optional[str]
    final_content: Optional[str]
    final_meta: Optional[str]
    final_keywords: Optional[List[str]]
```

- [ ] **Step 4: Create env template**

```bash
# .env.example
ANTHROPIC_API_KEY=your-api-key-here
```

- [ ] **Step 5: Commit**

```bash
git add src/state.py requirements.txt .env.example
git commit -m "feat: add LangGraph state and dependencies

- Define BlogState TypedDict for graph workflow
- Add LangGraph, LangChain, and Anthropic dependencies
- Set up project structure

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Outline Generator Node

**Files:**
- Create: `src/nodes/outline_generator.py`
- Create: `tests/test_outline_generator.py`

**Interfaces:**
- Consumes: `BlogState` (topic_title, category, keywords)
- Produces: `BlogState` with `outline` field populated

- [ ] **Step 1: Write test for outline generator**

```python
# tests/test_outline_generator.py
import pytest
from unittest.mock import Mock, patch
from src.nodes.outline_generator import outline_generator
from src.state import BlogState

@pytest.fixture
def mock_llm():
    with patch('src.nodes.outline_generator.ChatAnthropic') as mock:
        llm = Mock()
        mock.return_value = llm
        
        # Mock response
        response = Mock()
        response.content = """
## Introduction
- What circuit breakers do
- Why they trip

## Common Causes
1. Overloaded circuit
2. Short circuit
3. Ground fault
4. Faulty breaker
5. Old wiring

## When to Call Professional
- Safety signs
- Repeated tripping

## Conclusion
- Call to action
"""
        llm.invoke.return_value = response
        
        yield llm

def test_outline_generator_creates_outline(mock_llm):
    state = BlogState(
        topic_title="Why Does My Circuit Breaker Keep Tripping?",
        category="troubleshooting",
        keywords=["circuit breaker", "tripping"],
        target_audience="homeowners",
        outline=None,
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=False,
        review_feedback=None,
        revision_count=0,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )
    
    result = outline_generator(state)
    
    assert result["outline"] is not None
    assert len(result["outline"]) > 100
    assert "Introduction" in result["outline"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_outline_generator.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement outline generator node**

```python
# src/nodes/outline_generator.py
from langchain_anthropic import ChatAnthropic
from src.state import BlogState
import os

def outline_generator(state: BlogState) -> BlogState:
    """
    Node 1: Generate blog post outline
    
    Takes topic and creates structured outline with sections
    """
    
    # Initialize LLM
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7
    )
    
    # Build prompt
    prompt = f"""Create a detailed outline for a blog post about:

Topic: {state['topic_title']}
Category: {state['category']}
Target Keywords: {', '.join(state['keywords'])}
Target Audience: {state['target_audience']}

Requirements:
- Introduction section
- 5-7 main points/causes/solutions (numbered)
- "When to Call a Professional Electrician" section
- Safety considerations where relevant
- Conclusion with call-to-action

Format as markdown with ## for sections and numbered lists for main points.

Outline:"""
    
    # Generate outline
    response = llm.invoke(prompt)
    outline = response.content
    
    # Update state
    return {
        **state,
        "outline": outline
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_outline_generator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/nodes/outline_generator.py tests/test_outline_generator.py
git commit -m "feat: add outline generator node

- Create structured outline from topic
- Use LangChain ChatAnthropic for Claude integration
- Generate 5-7 section outline with safety and CTA

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Content Writer Node

**Files:**
- Create: `src/nodes/content_writer.py`
- Create: `tests/test_content_writer.py`

**Interfaces:**
- Consumes: `BlogState` (outline, topic_title, keywords)
- Produces: `BlogState` with draft_title, draft_content, draft_meta

- [ ] **Step 1: Write test for content writer**

```python
# tests/test_content_writer.py
import pytest
from unittest.mock import Mock, patch
from src.nodes.content_writer import content_writer
from src.state import BlogState

@pytest.fixture
def mock_llm():
    with patch('src.nodes.content_writer.ChatAnthropic') as mock:
        llm = Mock()
        mock.return_value = llm
        
        response = Mock()
        response.content = """TITLE: Why Does My Circuit Breaker Keep Tripping? 7 Common Causes

META: Learn the 7 most common reasons your circuit breaker keeps tripping and when to call a professional electrician.

CONTENT:
# Why Does My Circuit Breaker Keep Tripping?

A tripping circuit breaker is one of the most common electrical issues homeowners face...

## Common Causes

1. **Overloaded Circuit** - Too many devices...
2. **Short Circuit** - Wiring fault...

[... 1500 words of content ...]

## When to Call a Professional

If your breaker trips repeatedly...

## Conclusion

Don't ignore a tripping breaker. Contact our licensed electricians today."""
        
        llm.invoke.return_value = response
        yield llm

def test_content_writer_generates_draft(mock_llm):
    state = BlogState(
        topic_title="Test Topic",
        category="test",
        keywords=["test"],
        target_audience="homeowners",
        outline="## Intro\n## Points\n## Conclusion",
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=False,
        review_feedback=None,
        revision_count=0,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )
    
    result = content_writer(state)
    
    assert result["draft_title"] is not None
    assert result["draft_content"] is not None
    assert result["draft_meta"] is not None
    assert len(result["draft_title"]) <= 60
    assert len(result["draft_meta"]) <= 160
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_content_writer.py -v`
Expected: FAIL

- [ ] **Step 3: Implement content writer node**

```python
# src/nodes/content_writer.py
from langchain_anthropic import ChatAnthropic
from src.state import BlogState
import os

def content_writer(state: BlogState) -> BlogState:
    """
    Node 2: Write blog post content
    
    Takes outline and generates full blog post (1200-1800 words)
    """
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
        max_tokens=4096
    )
    
    # Check if this is a revision
    revision_context = ""
    if state.get("review_feedback"):
        revision_context = f"""
REVISION REQUESTED:
{state['review_feedback']}

Please address the feedback above while maintaining the quality and structure.
"""
    
    prompt = f"""Write a complete blog post following this outline:

{state['outline']}

TOPIC: {state['topic_title']}
KEYWORDS: {', '.join(state['keywords'])}
AUDIENCE: {state['target_audience']}

{revision_context}

REQUIREMENTS:
- Length: 1200-1800 words
- Clear, accessible language for {state['target_audience']}
- Natural keyword integration
- Safety warnings where appropriate
- Professional but friendly tone
- Strong call-to-action at end

FORMAT YOUR RESPONSE EXACTLY AS:

TITLE: [SEO-optimized title under 60 characters]

META: [Meta description under 160 characters]

CONTENT:
[Full markdown blog post starting with # title]"""
    
    response = llm.invoke(prompt)
    content = response.content
    
    # Parse response
    lines = content.split('\n')
    
    title = ""
    meta = ""
    content_lines = []
    
    section = None
    for line in lines:
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
            section = "title"
        elif line.startswith("META:"):
            meta = line.replace("META:", "").strip()
            section = "meta"
        elif line.startswith("CONTENT:"):
            section = "content"
        elif section == "content":
            content_lines.append(line)
    
    blog_content = '\n'.join(content_lines).strip()
    
    # Validate and truncate if needed
    if len(title) > 60:
        title = title[:57] + "..."
    if len(meta) > 160:
        meta = meta[:157] + "..."
    
    return {
        **state,
        "draft_title": title,
        "draft_content": blog_content,
        "draft_meta": meta
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_content_writer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/nodes/content_writer.py tests/test_content_writer.py
git commit -m "feat: add content writer node

- Generate 1200-1800 word blog posts from outline
- Parse structured response (title, meta, content)
- Support revision based on reviewer feedback
- Validate SEO constraints

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Content Reviewer Node

**Files:**
- Create: `src/nodes/content_reviewer.py`
- Create: `tests/test_content_reviewer.py`

**Interfaces:**
- Consumes: `BlogState` (draft_title, draft_content, draft_meta, keywords)
- Produces: `BlogState` with review_approved and review_feedback

- [ ] **Step 1: Write test for content reviewer**

```python
# tests/test_content_reviewer.py
import pytest
from unittest.mock import Mock, patch
from src.nodes.content_reviewer import content_reviewer
from src.state import BlogState

@pytest.fixture
def mock_llm():
    with patch('src.nodes.content_reviewer.ChatAnthropic') as mock:
        llm = Mock()
        mock.return_value = llm
        
        response = Mock()
        response.content = """APPROVED: YES

QUALITY SCORE: 9/10

REVIEW:
✓ SEO optimized title and meta
✓ All keywords naturally integrated
✓ Clear structure with proper headers
✓ 1450 words (within target range)
✓ Safety warnings included
✓ Strong call-to-action
✓ Accessible language for homeowners

Minor note: Excellent quality, ready to publish."""
        
        llm.invoke.return_value = response
        yield llm

def test_content_reviewer_approves_good_content(mock_llm):
    state = BlogState(
        topic_title="Test Topic",
        category="test",
        keywords=["test", "keyword"],
        target_audience="homeowners",
        outline="outline",
        draft_title="Test Title",
        draft_content="# Test\n\n" + "word " * 1500,  # 1500 words
        draft_meta="Test meta description",
        review_approved=False,
        review_feedback=None,
        revision_count=0,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )
    
    result = content_reviewer(state)
    
    assert result["review_approved"] == True
    assert result["review_feedback"] is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_content_reviewer.py -v`
Expected: FAIL

- [ ] **Step 3: Implement content reviewer node**

```python
# src/nodes/content_reviewer.py
from langchain_anthropic import ChatAnthropic
from src.state import BlogState
import os

def content_reviewer(state: BlogState) -> BlogState:
    """
    Node 3: Review blog post quality
    
    Checks for:
    - SEO optimization
    - Content quality
    - Keyword integration
    - Structure and formatting
    - Length requirements
    - Safety warnings
    - Call-to-action
    """
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.3  # Lower temp for consistent reviews
    )
    
    # Count words
    word_count = len(state['draft_content'].split())
    
    prompt = f"""Review this blog post draft for quality and completeness.

TOPIC: {state['topic_title']}
TARGET KEYWORDS: {', '.join(state['keywords'])}
AUDIENCE: {state['target_audience']}

DRAFT TITLE: {state['draft_title']}
DRAFT META: {state['draft_meta']}

DRAFT CONTENT:
{state['draft_content']}

WORD COUNT: {word_count}

REVIEW CRITERIA:
1. SEO: Title < 60 chars, meta < 160 chars, keywords naturally integrated
2. Length: 1200-1800 words
3. Structure: Clear headers, numbered lists, logical flow
4. Safety: Warnings where appropriate
5. Audience: Accessible language for {state['target_audience']}
6. Call-to-Action: Clear invitation to schedule services
7. Accuracy: Technically sound electrical information
8. Completeness: All outline sections covered

FORMAT YOUR RESPONSE AS:

APPROVED: [YES or NO]

QUALITY SCORE: [X/10]

REVIEW:
[Detailed review with ✓ for good points, ✗ for issues]

FEEDBACK:
[If APPROVED: NO, provide specific revision requests]
[If APPROVED: YES, can be brief positive note]"""
    
    response = llm.invoke(prompt)
    review_text = response.content
    
    # Parse approval
    approved = "APPROVED: YES" in review_text.upper()
    
    # Extract feedback section
    feedback = review_text
    if "FEEDBACK:" in review_text:
        feedback = review_text.split("FEEDBACK:")[1].strip()
    
    return {
        **state,
        "review_approved": approved,
        "review_feedback": feedback,
        "revision_count": state.get("revision_count", 0)
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_content_reviewer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/nodes/content_reviewer.py tests/test_content_reviewer.py
git commit -m "feat: add content reviewer node

- Review draft against 8 quality criteria
- Check SEO, length, structure, safety, CTA
- Return approval boolean and detailed feedback
- Support iterative revision workflow

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Finalizer Node & Graph Construction

**Files:**
- Create: `src/nodes/finalizer.py`
- Create: `src/graph.py`
- Create: `tests/test_graph.py`

**Interfaces:**
- Consumes: All previous nodes
- Produces: 
  - `finalizer` node that packages final output
  - `build_graph()` function that assembles workflow

- [ ] **Step 1: Implement finalizer node**

```python
# src/nodes/finalizer.py
from src.state import BlogState

def finalizer(state: BlogState) -> BlogState:
    """
    Node 4: Finalize blog post
    
    Packages approved draft as final output
    """
    
    return {
        **state,
        "final_title": state["draft_title"],
        "final_content": state["draft_content"],
        "final_meta": state["draft_meta"],
        "final_keywords": state["keywords"]
    }
```

- [ ] **Step 2: Build graph with conditional edges**

```python
# src/graph.py
from langgraph.graph import StateGraph, END
from src.state import BlogState
from src.nodes.outline_generator import outline_generator
from src.nodes.content_writer import content_writer
from src.nodes.content_reviewer import content_reviewer
from src.nodes.finalizer import finalizer

def should_revise(state: BlogState) -> str:
    """
    Conditional edge: determine if content needs revision
    
    Returns:
        "finalize" if approved
        "revise" if not approved and under max revisions
        "finalize" if max revisions reached (accept as-is)
    """
    MAX_REVISIONS = 2
    
    if state["review_approved"]:
        return "finalize"
    
    if state.get("revision_count", 0) >= MAX_REVISIONS:
        # Max revisions reached, finalize anyway
        return "finalize"
    
    return "revise"

def build_graph() -> StateGraph:
    """
    Build LangGraph workflow
    
    Graph flow:
    START -> outline -> writer -> reviewer -> [finalize OR revise]
                                    ↑              |
                                    |←←←←←←←←←←←←←←←
    """
    
    # Create graph
    workflow = StateGraph(BlogState)
    
    # Add nodes
    workflow.add_node("outline", outline_generator)
    workflow.add_node("writer", content_writer)
    workflow.add_node("reviewer", content_reviewer)
    workflow.add_node("finalize", finalizer)
    
    # Add edges
    workflow.add_edge("outline", "writer")
    workflow.add_edge("writer", "reviewer")
    
    # Conditional edge from reviewer
    workflow.add_conditional_edges(
        "reviewer",
        should_revise,
        {
            "finalize": "finalize",
            "revise": "writer"  # Loop back to writer with feedback
        }
    )
    
    workflow.add_edge("finalize", END)
    
    # Set entry point
    workflow.set_entry_point("outline")
    
    return workflow.compile()
```

- [ ] **Step 3: Write integration test**

```python
# tests/test_graph.py
import pytest
from unittest.mock import patch, Mock
from src.graph import build_graph
from src.state import BlogState

@pytest.fixture
def mock_all_llms():
    """Mock all LangChain LLM calls"""
    with patch('src.nodes.outline_generator.ChatAnthropic') as mock1, \
         patch('src.nodes.content_writer.ChatAnthropic') as mock2, \
         patch('src.nodes.content_reviewer.ChatAnthropic') as mock3:
        
        # Mock outline generator
        llm1 = Mock()
        mock1.return_value = llm1
        resp1 = Mock()
        resp1.content = "## Intro\n## Points\n1. Point 1\n## Conclusion"
        llm1.invoke.return_value = resp1
        
        # Mock content writer
        llm2 = Mock()
        mock2.return_value = llm2
        resp2 = Mock()
        resp2.content = """TITLE: Test Title

META: Test meta description

CONTENT:
# Test Title

Content here """ + "word " * 1500
        llm2.invoke.return_value = resp2
        
        # Mock reviewer (approve on first try)
        llm3 = Mock()
        mock3.return_value = llm3
        resp3 = Mock()
        resp3.content = """APPROVED: YES

QUALITY SCORE: 9/10

REVIEW: All good"""
        llm3.invoke.return_value = resp3
        
        yield (llm1, llm2, llm3)

def test_graph_runs_end_to_end(mock_all_llms):
    """Test full graph execution"""
    
    graph = build_graph()
    
    initial_state = BlogState(
        topic_title="Test Topic",
        category="test",
        keywords=["test", "keyword"],
        target_audience="homeowners",
        outline=None,
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=False,
        review_feedback=None,
        revision_count=0,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )
    
    result = graph.invoke(initial_state)
    
    # Verify all stages completed
    assert result["outline"] is not None
    assert result["draft_title"] is not None
    assert result["draft_content"] is not None
    assert result["review_approved"] == True
    assert result["final_title"] is not None
    assert result["final_content"] is not None
```

- [ ] **Step 4: Run integration test**

Run: `pytest tests/test_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/nodes/finalizer.py src/graph.py tests/test_graph.py
git commit -m "feat: build LangGraph workflow with conditional edges

- Add finalizer node to package final output
- Construct graph with outline→writer→reviewer→finalize
- Implement conditional edge for revision loop (max 2 revisions)
- Add end-to-end integration test

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: CLI Interface

**Files:**
- Create: `main.py`
- Create: `README.md`

**Interfaces:**
- Consumes: `build_graph()` from Task 5
- Produces: CLI that runs graph and saves output

- [ ] **Step 1: Create CLI script**

```python
# main.py
#!/usr/bin/env python3
"""LangGraph Blog Generator - Multi-node AI workflow"""

import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.graph import build_graph
from src.state import BlogState

load_dotenv()

def sanitize_filename(title: str) -> str:
    """Convert title to valid filename"""
    filename = title.lower().replace("?", "").replace("!", "")
    filename = filename.replace(" ", "-")
    filename = "".join(c for c in filename if c.isalnum() or c == "-")
    return filename[:60] + ".md"

def main():
    parser = argparse.ArgumentParser(
        description="LangGraph Blog Generator - Multi-node AI workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python main.py "Why Does My Circuit Breaker Keep Tripping?" \\
    --category troubleshooting \\
    --keywords "circuit breaker,tripping,overload"
        """
    )
    
    parser.add_argument("title", help="Blog topic/title")
    parser.add_argument("--category", required=True,
                       choices=["troubleshooting", "safety", "generators", 
                               "ev_chargers", "panels", "home_improvement"])
    parser.add_argument("--keywords", required=True,
                       help="Comma-separated keywords")
    parser.add_argument("--audience", default="homeowners")
    parser.add_argument("--output-dir", default="output")
    
    args = parser.parse_args()
    
    # Parse input
    keywords = [k.strip() for k in args.keywords.split(",")]
    
    print("\n🤖 LangGraph Blog Generator")
    print("=" * 70)
    print(f"\n📝 Topic: {args.title}")
    print(f"   Category: {args.category}")
    print(f"   Keywords: {', '.join(keywords)}")
    print(f"   Audience: {args.audience}")
    print("\n🔄 Starting multi-node workflow...\n")
    
    # Build graph
    graph = build_graph()
    
    # Initialize state
    initial_state = BlogState(
        topic_title=args.title,
        category=args.category,
        keywords=keywords,
        target_audience=args.audience,
        outline=None,
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=False,
        review_feedback=None,
        revision_count=0,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )
    
    try:
        # Execute graph
        print("   [1/4] 📋 Generating outline...")
        print("   [2/4] ✍️  Writing content...")
        print("   [3/4] 🔍 Reviewing quality...")
        print("   [4/4] ✅ Finalizing...\n")
        
        result = graph.invoke(initial_state)
        
        # Display results
        print("=" * 70)
        print("\n✅ Blog post generated successfully!\n")
        
        print(f"📊 Workflow Stats:")
        print(f"   Revisions: {result.get('revision_count', 0)}")
        print(f"   Review: {'APPROVED' if result['review_approved'] else 'ACCEPTED (max revisions)'}")
        
        print(f"\n📄 Final Output:")
        print(f"   Title: {result['final_title']}")
        print(f"   Meta: {result['final_meta']}")
        print(f"   Keywords: {', '.join(result['final_keywords'])}")
        
        word_count = len(result['final_content'].split())
        print(f"   Length: {word_count} words")
        
        # Save output
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        filename = sanitize_filename(args.title)
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(f"title: {result['final_title']}\n")
            f.write(f"meta_description: {result['final_meta']}\n")
            f.write(f"keywords: {', '.join(result['final_keywords'])}\n")
            f.write(f"category: {args.category}\n")
            f.write(f"generated_at: {datetime.now().isoformat()}\n")
            f.write(f"revisions: {result.get('revision_count', 0)}\n")
            f.write("---\n\n")
            f.write(result['final_content'])
        
        print(f"\n💾 Saved to: {filepath}")
        
        # Show review feedback
        if result.get('review_feedback'):
            print(f"\n📝 Review Feedback:")
            print(f"   {result['review_feedback'][:200]}...")
        
        print("\n" + "=" * 70)
        print("✅ Complete!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

- [ ] **Step 2: Create README**

```markdown
# LangGraph Blog Generator

Multi-node AI workflow for generating SEO-optimized electrical blog posts using LangGraph and Claude.

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
# Edit .env: ANTHROPIC_API_KEY=your-key
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
- **Claude API** - Content generation

## License

MIT
```

- [ ] **Step 3: Test CLI end-to-end**

Run:
```bash
python main.py "Test Topic" \
  --category troubleshooting \
  --keywords "test,keyword"
```

Expected: Full workflow executes, blog saved to output/

- [ ] **Step 4: Commit**

```bash
git add main.py README.md
git commit -m "feat: add CLI and documentation

- Create CLI with full workflow visualization
- Show progress through 4-node graph
- Display revision count and review status
- Comprehensive README with architecture diagram

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Final Checklist

- [ ] All 6 tasks completed
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Graph has 4 nodes: outline, writer, reviewer, finalizer
- [ ] Conditional edge for revision loop (max 2 revisions)
- [ ] Reviewer node validates quality
- [ ] CLI runs full workflow
- [ ] Output saved as markdown with frontmatter

---

**Plan complete! LangGraph blog generator with reviewer node.**

Ready to implement?
