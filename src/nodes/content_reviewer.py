from langchain_anthropic import ChatAnthropic
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

    # Parse approval using regex
    approval_match = re.search(r'^APPROVED:\s*(YES|NO)', review_text, re.MULTILINE | re.IGNORECASE)
    approved = approval_match and approval_match.group(1).upper() == "YES" if approval_match else False

    # Extract feedback section
    feedback = review_text
    if "FEEDBACK:" in review_text:
        feedback = review_text.split("FEEDBACK:")[1].strip()

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
