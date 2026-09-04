from langchain_groq import ChatGroq
from src.state import BlogState
import os

def outline_generator(state: BlogState) -> BlogState:
    """
    Node 1: Generate blog post outline

    Takes topic and creates structured outline with sections
    """

    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.1-405b-reasoning",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )

    # Build prompt
    prompt = f"""Create a detailed outline for a blog post about:

Topic: {state['topic_title']}
Category: {state['category']}
Target Keywords: {', '.join(state['keywords'])}
Target Audience: {state['target_audience']}

Requirements:
- Introduction section
- 5-7 main points/causes/solutions (numbered)
- "When to Call a Professional Electrician" section
- Safety considerations where relevant
- Conclusion with call-to-action

Format as markdown with ## for sections and numbered lists for main points.

Outline:"""

    # Generate outline
    response = llm.invoke(prompt)
    outline = response.content

    # Update state
    return {
        **state,
        "outline": outline
    }
