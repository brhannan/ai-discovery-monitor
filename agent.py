"""AI Discovery Monitor - Claude SDK Agent with Subagents"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition

# Load environment variables
load_dotenv()

# Paths to prompt files
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


async def run_discovery_monitor():
    """Run the AI Discovery Monitor with Claude SDK and subagents."""

    # Check API key first
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\nError: ANTHROPIC_API_KEY not found.")
        print("Set it in a .env file or export it in your shell.")
        print("Get your key at: https://console.anthropic.com/settings/keys\n")
        return

    # Load prompts
    orchestrator_prompt = load_prompt("orchestrator.txt")
    researcher_prompt = load_prompt("researcher.txt")
    analyzer_prompt = load_prompt("source_analyzer.txt")
    trend_prompt = load_prompt("trend_detector.txt")
    writer_prompt = load_prompt("report_writer.txt")

    # Define specialized subagents
    agents = {
        "researcher": AgentDefinition(
            description=(
                "Search for latest AI news, developments, and announcements. "
                "Use WebSearch to find breaking news, tool launches, research papers, "
                "and community discussions. Focus on AI agents, LLMs, safety, and emerging tools."
            ),
            tools=["WebSearch", "Write"],
            prompt=researcher_prompt,
            model="haiku"
        ),
        "source-analyzer": AgentDefinition(
            description=(
                "Analyze trusted blogs and Twitter accounts for key insights and themes. "
                "Extract what trusted voices are discussing, identify consensus areas, "
                "note who is citing whom, and synthesize community perspectives."
            ),
            tools=["WebSearch", "Read", "Glob"],
            prompt=analyzer_prompt,
            model="haiku"
        ),
        "trend-detector": AgentDefinition(
            description=(
                "Identify patterns and emerging trends across the AI space. "
                "Detect inflection points, connect disparate developments, "
                "and forecast what might be important next. Focus on paradigm shifts and momentum changes."
            ),
            tools=["Task"],
            prompt=trend_prompt,
            model="haiku"
        ),
        "report-writer": AgentDefinition(
            description=(
                "Synthesize findings from other agents into a polished, comprehensive report. "
                "Create a well-structured report with executive summary, key insights, trends, "
                "and actionable takeaways. Cite all sources properly."
            ),
            tools=["Write"],
            prompt=writer_prompt,
            model="haiku"
        )
    }

    # Configure options with subagents
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        system_prompt=orchestrator_prompt,
        allowed_tools=["Task"],
        agents=agents,
        model="haiku"
    )

    print("\n" + "=" * 70)
    print("AI DISCOVERY MONITOR - Powered by Claude SDK")
    print("=" * 70)
    print("\nOrchestrating specialized agents to discover and analyze AI developments...")
    print(f"Registered subagents: {', '.join(agents.keys())}\n")

    async with ClaudeSDKClient(options=options) as client:
        # Create discovery prompt for the orchestrator
        discovery_prompt = (
            "It's time for your weekly AI discovery report. "
            "Please coordinate with all subagents to:\n"
            "1. Use the Researcher to find latest AI news and developments\n"
            "2. Use the Source Analyzer to extract insights from trusted sources\n"
            "3. Use the Trend Detector to identify emerging patterns\n"
            "4. Use the Report Writer to synthesize everything into a comprehensive report\n\n"
            "Please delegate tasks to each subagent, collect their findings, "
            "and generate a final AI Discovery Report that covers what's new, "
            "what's trending, and what it all means for the AI ecosystem."
        )

        print("📋 Sending discovery request to orchestrator...\n")

        # Send discovery request
        await client.query(prompt=discovery_prompt)

        print("\n🔄 Orchestrator is delegating to subagents...\n")
        print("-" * 70)

        # Stream and display response
        async for msg in client.receive_response():
            if type(msg).__name__ == 'TextBlock':
                print(msg.text, end="", flush=True)
            elif type(msg).__name__ == 'ToolUseBlock':
                print(f"\n[Agent Task: {msg.name}]", flush=True)

        print("\n" + "-" * 70)
        print("\n✅ Discovery complete!")
        print("\nReport generated and ready. Check the output above for the full AI Discovery Report.")


async def main():
    """Main entry point."""
    try:
        await run_discovery_monitor()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
