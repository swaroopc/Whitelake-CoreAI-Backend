import pytest
from unittest.mock import patch, Mock
from src.graph import build_graph, should_revise
from src.state import BlogState


@pytest.fixture
def mock_all_llms():
    """Mock all LangChain LLM calls"""
    with patch('src.nodes.outline_generator.ChatGroq') as mock1, \
         patch('src.nodes.content_writer.ChatGroq') as mock2, \
         patch('src.nodes.content_reviewer.ChatGroq') as mock3:

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


def test_should_revise_approved():
    """Test conditional edge returns 'finalize' when approved"""
    state = BlogState(
        topic_title="Test",
        category="test",
        keywords=["test"],
        target_audience="homeowners",
        outline=None,
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=True,
        review_feedback=None,
        revision_count=0,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )

    assert should_revise(state) == "finalize"


def test_should_revise_not_approved_under_max():
    """Test conditional edge returns 'revise' when not approved and under max revisions"""
    state = BlogState(
        topic_title="Test",
        category="test",
        keywords=["test"],
        target_audience="homeowners",
        outline=None,
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=False,
        review_feedback="Needs work",
        revision_count=1,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )

    assert should_revise(state) == "revise"


def test_should_revise_max_revisions_reached():
    """Test conditional edge returns 'finalize' when max revisions reached"""
    state = BlogState(
        topic_title="Test",
        category="test",
        keywords=["test"],
        target_audience="homeowners",
        outline=None,
        draft_title=None,
        draft_content=None,
        draft_meta=None,
        review_approved=False,
        review_feedback="Still needs work",
        revision_count=3,
        final_title=None,
        final_content=None,
        final_meta=None,
        final_keywords=None
    )

    assert should_revise(state) == "finalize"


def test_graph_runs_end_to_end(mock_all_llms):
    """Test full graph execution with approval on first try"""

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
    assert result["final_meta"] is not None
    assert result["final_keywords"] is not None


def test_graph_with_revision_loop():
    """Test graph executes revision loop when content rejected"""

    with patch('src.nodes.outline_generator.ChatGroq') as mock1, \
         patch('src.nodes.content_writer.ChatGroq') as mock2, \
         patch('src.nodes.content_reviewer.ChatGroq') as mock3:

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

        # Mock reviewer: first reject, then approve
        llm3 = Mock()
        mock3.return_value = llm3

        reject_resp = Mock()
        reject_resp.content = """APPROVED: NO

QUALITY SCORE: 5/10

REVIEW: Needs improvement"""

        approve_resp = Mock()
        approve_resp.content = """APPROVED: YES

QUALITY SCORE: 9/10

REVIEW: Much better!"""

        llm3.invoke.side_effect = [reject_resp, approve_resp]

        graph = build_graph()

        initial_state = BlogState(
            topic_title="Test Topic",
            category="test",
            keywords=["test"],
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

        # Verify revision happened
        assert result["revision_count"] >= 1
        assert result["review_approved"] == True
        assert result["final_title"] is not None
