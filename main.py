#!/usr/bin/env python3
"""LangGraph Blog Generator - Multi-node AI workflow"""

import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import yaml

from src.graph import build_graph
from src.state import BlogState

load_dotenv()

def sanitize_filename(title: str) -> str:
    """Convert title to valid filename"""
    filename = title.lower().replace("?", "").replace("!", "")
    filename = filename.replace(" ", "-")
    filename = "".join(c for c in filename if c.isalnum() or c == "-")
    return filename[:60] + ".md"

def main():
    parser = argparse.ArgumentParser(
        description="LangGraph Blog Generator - Multi-node AI workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python main.py "Why Does My Circuit Breaker Keep Tripping?" \\
    --category troubleshooting \\
    --keywords "circuit breaker,tripping,overload"
        """
    )

    parser.add_argument("title", help="Blog topic/title")
    parser.add_argument("--category", required=True,
                       choices=["troubleshooting", "safety", "generators",
                               "ev_chargers", "panels", "home_improvement"])
    parser.add_argument("--keywords", required=True,
                       help="Comma-separated keywords")
    parser.add_argument("--audience", default="homeowners")
    parser.add_argument("--output-dir", default="output")

    args = parser.parse_args()

    # Parse input
    keywords = [k.strip() for k in args.keywords.split(",")]

    print("\n🤖 LangGraph Blog Generator")
    print("=" * 70)
    print(f"\n📝 Topic: {args.title}")
    print(f"   Category: {args.category}")
    print(f"   Keywords: {', '.join(keywords)}")
    print(f"   Audience: {args.audience}")
    print("\n🔄 Starting multi-node workflow...\n")

    # Build graph
    graph = build_graph()

    # Initialize state
    initial_state = BlogState(
        topic_title=args.title,
        category=args.category,
        keywords=keywords,
        target_audience=args.audience,
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

    try:
        # Execute graph
        print("   [1/4] 📋 Generating outline...")
        print("   [2/4] ✍️  Writing content...")
        print("   [3/4] 🔍 Reviewing quality...")
        print("   [4/4] ✅ Finalizing...\n")

        result = graph.invoke(initial_state)

        # Display results
        print("=" * 70)
        print("\n✅ Blog post generated successfully!\n")

        print(f"📊 Workflow Stats:")
        print(f"   Revisions: {result.get('revision_count', 0)}")
        print(f"   Review: {'APPROVED' if result['review_approved'] else 'ACCEPTED (max revisions)'}")

        print(f"\n📄 Final Output:")
        print(f"   Title: {result['final_title']}")
        print(f"   Meta: {result['final_meta']}")
        print(f"   Keywords: {', '.join(result['final_keywords'])}")

        word_count = len(result['final_content'].split())
        print(f"   Length: {word_count} words")

        # Save output
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)

        filename = sanitize_filename(args.title)
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            frontmatter = {
                'title': result['final_title'],
                'meta_description': result['final_meta'],
                'keywords': ', '.join(result['final_keywords']),
                'category': args.category,
                'generated_at': datetime.now().isoformat(),
                'revisions': result.get('revision_count', 0)
            }
            f.write("---\n")
            f.write(yaml.safe_dump(frontmatter, default_flow_style=False, allow_unicode=True))
            f.write("---\n\n")
            f.write(result['final_content'])

        print(f"\n💾 Saved to: {filepath}")

        # Show review feedback
        if result.get('review_feedback'):
            print(f"\n📝 Review Feedback:")
            print(f"   {result['review_feedback'][:200]}...")

        print("\n" + "=" * 70)
        print("✅ Complete!\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
