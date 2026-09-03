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


def test_content_writer_handles_revision(mock_llm):
    """Test that content writer incorporates review feedback"""
    state = BlogState(
        topic_title="Test Topic",
        category="test",
        keywords=["test"],
        target_audience="homeowners",
        outline="## Intro\n## Points\n## Conclusion",
        draft_title="Old Title",
        draft_content="Old content",
        draft_meta="Old meta",
        review_approved=False,
        review_feedback="Add more safety warnings",
        revision_count=1,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )

    result = content_writer(state)

    # Should have new draft based on feedback
    assert result["draft_title"] is not None
    assert result["draft_content"] is not None
    assert result["draft_meta"] is not None
    # Verify LLM was called with feedback in prompt
    mock_llm.invoke.assert_called_once()
    call_args = mock_llm.invoke.call_args[0][0]
    assert "REVISION REQUESTED" in call_args
    assert "Add more safety warnings" in call_args


def test_content_writer_truncates_long_title():
    """Test that title >60 chars gets truncated"""
    with patch('src.nodes.content_writer.ChatAnthropic') as mock:
        llm = Mock()
        mock.return_value = llm

        response = Mock()
        response.content = """TITLE: This Is An Extremely Long Title That Definitely Exceeds The Sixty Character Limit For SEO

META: Short meta

CONTENT:
# Content here"""

        llm.invoke.return_value = response

        state = BlogState(
            topic_title="Test",
            category="test",
            keywords=["test"],
            target_audience="homeowners",
            outline="test",
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

        assert len(result["draft_title"]) <= 60
        assert result["draft_title"].endswith("...")


def test_content_writer_truncates_long_meta():
    """Test that meta >160 chars gets truncated"""
    with patch('src.nodes.content_writer.ChatAnthropic') as mock:
        llm = Mock()
        mock.return_value = llm

        response = Mock()
        response.content = """TITLE: Short Title

META: This is an extremely long meta description that goes on and on and definitely exceeds the one hundred sixty character limit for SEO meta descriptions which should be concise.

CONTENT:
# Content here"""

        llm.invoke.return_value = response

        state = BlogState(
            topic_title="Test",
            category="test",
            keywords=["test"],
            target_audience="homeowners",
            outline="test",
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

        assert len(result["draft_meta"]) <= 160
        assert result["draft_meta"].endswith("...")
