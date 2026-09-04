import pytest
from unittest.mock import Mock, patch
from src.nodes.outline_generator import outline_generator
from src.state import BlogState

@pytest.fixture
def mock_llm():
    with patch('src.nodes.outline_generator.ChatGroq') as mock:
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
