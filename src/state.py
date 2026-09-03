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
