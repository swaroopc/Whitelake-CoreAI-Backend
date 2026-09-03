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

PREVIOUS DRAFT:
{state.get('draft_content', '')}

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

    # Check for empty output
    if not title or not blog_content:
        raise ValueError("Failed to parse LLM response")

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
