import pytest
from unittest.mock import Mock, patch
from src.nodes.content_reviewer import content_reviewer
from src.state import BlogState

@pytest.fixture
def mock_llm():
    with patch('src.nodes.content_reviewer.ChatGroq') as mock:
        llm = Mock()
        mock.return_value = llm

        response = Mock()
        response.content = '''{
  "approved": true,
  "quality_score": 9,
  "review": "✓ SEO optimized title and meta\\n✓ All keywords naturally integrated\\n✓ Clear structure with proper headers\\n✓ 1450 words (within target range)\\n✓ Safety warnings included\\n✓ Strong call-to-action\\n✓ Accessible language for homeowners",
  "feedback": "Minor note: Excellent quality, ready to publish."
}'''

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
