
import os
import sys

# Add the current directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from dotenv import load_dotenv
from llama_index.llms.cerebras import Cerebras

from tools.exa_tools import (
    ExaSearchTools,
    create_search_tool,
    create_content_tool,
    create_similar_tool
)
from tools.analysis_tools import (
    AnalysisTools,
    create_summarize_tool,
    create_compare_tool,
    create_insights_tool
)
from agents.research_agent import create_research_agent
from agents.analysis_agent import create_analysis_agent
from research_workflows.research_workflow import ResearchWorkflow, run_research_query


def initialize_system():
    """
    Initialize the multi-agent research system.

    Returns:
        Tuple of (workflow, llm) for running queries
    """
    # Load environment variables
    load_dotenv()

    cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")
    model_name = os.getenv("CEREBRAS_MODEL", "llama3.3-70b")

    if not cerebras_api_key:
        raise ValueError("CEREBRAS_API_KEY not found in environment variables")
    if not exa_api_key:
        raise ValueError("EXA_API_KEY not found in environment variables")

    print("🚀 Initializing Multi-Agent Research Assistant")
    print(f"📊 Model: {model_name}")
    print(f"⚡ Provider: Cerebras (ultra-fast inference)")
    print(f"🔍 Search: Exa (semantic search)\n")

    # Initialize LLM with Cerebras
    llm = Cerebras(
        model=model_name,
        api_key=cerebras_api_key,
        temperature=0.7,
    )

    print("✓ Cerebras LLM initialized")

    # Initialize tool systems
    exa_tools = ExaSearchTools(api_key=exa_api_key)
    analysis_tools = AnalysisTools()

    print("✓ Tool systems initialized")

    # Create tools for agents
    research_tools = [
        create_search_tool(exa_tools),
        create_content_tool(exa_tools),
        create_similar_tool(exa_tools),
    ]

    analysis_tools_list = [
        create_summarize_tool(analysis_tools),
        create_compare_tool(analysis_tools),
        create_insights_tool(analysis_tools),
    ]

    print("✓ Agent tools created")

    # Create agents
    research_agent = create_research_agent(
        llm=llm,
        tools=research_tools,
        verbose=True
    )

    analysis_agent = create_analysis_agent(
        llm=llm,
        tools=analysis_tools_list,
        verbose=True
    )

    print("✓ Research Agent created")
    print("✓ Analysis Agent created")

    # Create workflow
    workflow = ResearchWorkflow(
        research_agent=research_agent,
        analysis_agent=analysis_agent,
        verbose=True
    )

    print("✓ Workflow orchestration ready\n")

    return workflow, llm


async def run_query(workflow: ResearchWorkflow, query: str):
    """
    Run a research query through the multi-agent system.

    Args:
        workflow: Configured ResearchWorkflow
        query: User's research question
    """
    print(f"\n{'='*60}")
    print(f"USER QUERY: {query}")
    print(f"{'='*60}\n")

    result = await run_research_query(workflow, query)

    print(f"\n{'='*60}")
    print(f"FINAL ANSWER")
    print(f"{'='*60}\n")
    print(result)
    print(f"\n{'='*60}\n")

    return result


async def interactive_mode(workflow: ResearchWorkflow):
    """
    Run the system in interactive mode.

    Args:
        workflow: Configured ResearchWorkflow
    """
    print("\n" + "="*60)
    print("🤖 INTERACTIVE RESEARCH ASSISTANT")
    print("="*60)
    print("Ask me anything! I'll research and provide detailed answers.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            query = input("Your question: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            await run_query(workflow, query)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


async def demo_queries(workflow: ResearchWorkflow):
    """
    Run demo queries to showcase the system.

    Args:
        workflow: Configured ResearchWorkflow
    """
    demo_questions = [
        "What are the latest developments in quantum computing?",
        "Compare the features of the top 3 AI coding assistants",
        "What is Cerebras and how does it achieve fast inference?",
    ]

    print("\n" + "="*60)
    print("🎬 RUNNING DEMO QUERIES")
    print("="*60 + "\n")

    for i, question in enumerate(demo_questions, 1):
        print(f"\n📝 Demo Query {i}/{len(demo_questions)}")
        await run_query(workflow, question)
        print("\n" + "-"*60 + "\n")


def main():
    """Main entry point."""
    import sys

    # Initialize the system
    workflow, llm = initialize_system()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            # Run demo queries
            asyncio.run(demo_queries(workflow))
        elif sys.argv[1] == "--query":
            # Run a single query from command line
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                asyncio.run(run_query(workflow, query))
            else:
                print("Usage: python main.py --query <your question>")
        else:
            print("Unknown argument. Use --demo or --query <question>")
    else:
        # Interactive mode
        asyncio.run(interactive_mode(workflow))


if __name__ == "__main__":
    main()
