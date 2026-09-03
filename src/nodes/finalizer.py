from src.state import BlogState


def finalizer(state: BlogState) -> BlogState:
    """
    Node 4: Finalize blog post

    Packages approved draft as final output
    """

    return {
        **state,
        "final_title": state["draft_title"],
        "final_content": state["draft_content"],
        "final_meta": state["draft_meta"],
        "final_keywords": state["keywords"]
    }
