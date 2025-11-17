"""AI Discovery Monitor - Claude SDK Agent with Subagents"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from cost_tracker import CostTracker

# Unbuffered output for GitHub Actions
sys.stdout.flush()
sys.stderr.flush()

# Load environment variables
load_dotenv()

# Initialize cost tracker
cost_tracker = CostTracker()

print("[INIT] Starting AI Discovery Monitor...", flush=True)

# Paths to prompt files
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


async def run_discovery_monitor():
    """Run the AI Discovery Monitor with Claude SDK and subagents."""

    print("[CHECK] Verifying API key...", flush=True)
    # Check API key first
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\nError: ANTHROPIC_API_KEY not found.")
        print("Set it in a .env file or export it in your shell.")
        print("Get your key at: https://console.anthropic.com/settings/keys\n")
        return

    print("[LOAD] Loading prompts...", flush=True)
    # Load prompts
    orchestrator_prompt = load_prompt("orchestrator.txt")
    print(f"  - Loaded orchestrator prompt ({len(orchestrator_prompt)} chars)", flush=True)
    researcher_prompt = load_prompt("researcher.txt")
    print(f"  - Loaded researcher prompt ({len(researcher_prompt)} chars)", flush=True)
    analyzer_prompt = load_prompt("source_analyzer.txt")
    print(f"  - Loaded analyzer prompt ({len(analyzer_prompt)} chars)", flush=True)
    trend_prompt = load_prompt("trend_detector.txt")
    print(f"  - Loaded trend detector prompt ({len(trend_prompt)} chars)", flush=True)
    writer_prompt = load_prompt("report_writer.txt")
    print(f"  - Loaded report writer prompt ({len(writer_prompt)} chars)", flush=True)

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

    print("[SETUP] Configuring subagents...", flush=True)
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
    print("[CONNECT] Initializing Claude SDK client...", flush=True)

    async with ClaudeSDKClient(options=options) as client:
        print("[CONNECTED] Claude SDK client ready", flush=True)
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

        print("📋 Sending discovery request to orchestrator...\n", flush=True)

        # Send discovery request
        print("[QUERY] Sending prompt to orchestrator...", flush=True)
        await client.query(prompt=discovery_prompt)
        print("[AWAITING] Waiting for orchestrator response...", flush=True)

        print("\n🔄 Orchestrator is delegating to subagents...\n", flush=True)
        print("-" * 70, flush=True)

        # Stream and display response, capture for report
        msg_count = 0
        report_content = []
        print("[STREAMING] Receiving response messages...", flush=True)
        async for msg in client.receive_response():
            msg_count += 1
            msg_type = type(msg).__name__

            if msg_type == 'TextBlock':
                print(msg.text, end="", flush=True)
                report_content.append(msg.text)

                # Try to extract usage data if available
                if hasattr(msg, 'usage') and msg.usage:
                    input_tokens = msg.usage.get('input_tokens', 0)
                    output_tokens = msg.usage.get('output_tokens', 0)
                    if input_tokens > 0 or output_tokens > 0:
                        cost_tracker.log_call("haiku", input_tokens, output_tokens, "orchestrator")

            elif msg_type == 'ToolUseBlock':
                # Log to stdout for visibility but don't add to report (too noisy)
                print(f"[{msg.name}]", end=" ", flush=True)

            elif msg_type == 'AssistantMessage':
                # AssistantMessage contains content blocks (TextBlock, ToolUseBlock, etc)
                for block in msg.content:
                    block_type = type(block).__name__
                    if block_type == 'TextBlock':
                        # Only add non-empty text to report (filter out just whitespace)
                        text = block.text
                        if text and text.strip():
                            print(text, end="", flush=True)
                            report_content.append(text)
                    elif block_type == 'ToolUseBlock':
                        # Log tool use but don't add to report
                        print(f"[{block.name}]", end=" ", flush=True)

            elif msg_type == 'ResultMessage':
                # Capture cost from result message
                if hasattr(msg, 'total_cost_usd') and msg.total_cost_usd:
                    print(f"[COST] Result message reports: ${msg.total_cost_usd:.4f}", flush=True)
                if hasattr(msg, 'usage') and msg.usage:
                    input_tokens = msg.usage.get('input_tokens', 0)
                    output_tokens = msg.usage.get('output_tokens', 0)
                    if input_tokens > 0 or output_tokens > 0:
                        cost_tracker.log_call("haiku", input_tokens, output_tokens, "result")

            else:
                # Log any other message types we encounter
                print(f"[{msg_type}] Message received", flush=True)

            # Log every 5 messages to show progress
            if msg_count % 5 == 0:
                print(f"\n[MSG {msg_count}] Processing messages...", flush=True)

        print(f"\n[COMPLETE] Received {msg_count} messages total", flush=True)
        print("\n" + "-" * 70, flush=True)

        # Save report to file
        print("[SAVE] Writing report to recommendations.md...", flush=True)
        report_text = "".join(report_content)
        with open("recommendations.md", "w") as f:
            f.write("# AI Discovery Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(report_text)
            f.write("\n\n")
            f.write(cost_tracker.get_summary())
        print("[SAVED] Report written to recommendations.md", flush=True)

        # Log cost summary
        print(cost_tracker.get_summary(), flush=True)

        print("\n✅ Discovery complete!", flush=True)
        print("\nReport generated and ready. Check the output above for the full AI Discovery Report.", flush=True)


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
