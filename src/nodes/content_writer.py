from langchain_groq import ChatGroq
from src.state import BlogState
import os


def content_writer(state: BlogState) -> BlogState:
    """
    Node 2: Write blog post content

    Takes outline and generates full blog post (1200-1800 words)
    """

    llm = ChatGroq(
        model="openai/gpt-oss-120b",  # Faster model with better rate limits
        api_key=os.getenv("GROQ_API_KEY"),
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

Return ONLY valid JSON in this exact format (no markdown code blocks, no other text):

{{
  "title": "SEO-optimized title under 60 characters",
  "content": "Full markdown blog post",
  "meta_description": "Compelling description under 160 characters",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

    response = llm.invoke(prompt)
    response_text = response.content.strip() if hasattr(response.content, 'strip') else str(response.content).strip()

    # Debug: Print response info
    print(f"\n=== DEBUG content_writer ===")
    print(f"Response type: {type(response.content)}")
    print(f"Response length: {len(response_text)}")
    print(f"First 500 chars: {response_text[:500]}")
    print("===\n")

    if not response_text:
        raise ValueError("Empty response from LLM")

    # Parse JSON response
    import json
    try:
        # Try direct JSON parse
        result = json.loads(response_text)
    except json.JSONDecodeError as e:
        # Try extracting from markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
            result = json.loads(response_text)
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
            result = json.loads(response_text)
        else:
            raise ValueError(f"Failed to parse LLM response as JSON: {response_text[:500]}\nJSON error: {str(e)}")

    title = result.get("title", "")
    blog_content = result.get("content", "")
    meta = result.get("meta_description", "")

    # Check for empty output
    if not title or not blog_content:
        raise ValueError(f"Empty title or content in response")

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
