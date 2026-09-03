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
    MAX_REVISIONS = 3

    if state["review_approved"]:
        return "finalize"

    if state.get("revision_count", 0) >= MAX_REVISIONS:
        # Max revisions reached, finalize anyway
        return "finalize"

    return "revise"


def build_graph():
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
