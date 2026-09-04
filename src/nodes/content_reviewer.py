from langchain_groq import ChatGroq
from src.state import BlogState
import os
import re

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

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
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

Return ONLY valid JSON in this exact format (no markdown code blocks, no other text):

{{
  "approved": true or false,
  "quality_score": 8,
  "review": "Detailed review with ✓ for good points, ✗ for issues",
  "feedback": "If approved: false, provide specific revision requests. If approved: true, brief positive note"
}}"""

    response = llm.invoke(prompt)
    response_text = response.content.strip()

    # Parse JSON response
    import json
    try:
        # Try direct JSON parse
        result = json.loads(response_text)
    except json.JSONDecodeError:
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
            raise ValueError(f"Failed to parse reviewer response as JSON: {response_text[:500]}")

    approved = result.get("approved", False)
    feedback = result.get("feedback", "")

    # Increment revision count if not approved
    new_revision_count = state.get("revision_count", 0)
    if not approved:
        new_revision_count += 1

    return {
        **state,
        "review_approved": approved,
        "review_feedback": feedback,
        "revision_count": new_revision_count
    }
