"""Track API costs for Claude SDK operations."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ModelCosts:
    """Pricing for Claude models (in USD per 1K tokens)."""
    # As of November 2024
    haiku_input = 0.80 / 1000      # $0.80 per 1M input tokens
    haiku_output = 4.00 / 1000     # $4.00 per 1M output tokens
    sonnet_input = 3.00 / 1000     # $3.00 per 1M input tokens
    sonnet_output = 15.00 / 1000   # $15.00 per 1M output tokens
    opus_input = 15.00 / 1000      # $15.00 per 1M input tokens
    opus_output = 75.00 / 1000     # $75.00 per 1M output tokens


class CostTracker:
    """Track costs across API calls."""

    def __init__(self):
        self.calls = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def log_call(self, model: str, input_tokens: int, output_tokens: int, agent: str = "orchestrator"):
        """Log an API call with token usage."""
        # Get pricing
        if model.lower() == "haiku":
            input_cost = input_tokens * ModelCosts.haiku_input
            output_cost = output_tokens * ModelCosts.haiku_output
        elif model.lower() == "sonnet":
            input_cost = input_tokens * ModelCosts.sonnet_input
            output_cost = output_tokens * ModelCosts.sonnet_output
        elif model.lower() == "opus":
            input_cost = input_tokens * ModelCosts.opus_input
            output_cost = output_tokens * ModelCosts.opus_output
        else:
            # Default to haiku
            input_cost = input_tokens * ModelCosts.haiku_input
            output_cost = output_tokens * ModelCosts.haiku_output

        call_cost = input_cost + output_cost

        self.calls.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": call_cost,
        })

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += call_cost

    def get_summary(self) -> str:
        """Get a formatted cost summary."""
        summary = "\n" + "=" * 70 + "\n"
        summary += "COST SUMMARY\n"
        summary += "=" * 70 + "\n\n"

        summary += f"Total Input Tokens:  {self.total_input_tokens:,}\n"
        summary += f"Total Output Tokens: {self.total_output_tokens:,}\n"
        summary += f"Total Tokens:        {self.total_input_tokens + self.total_output_tokens:,}\n\n"

        summary += f"Total Cost: ${self.total_cost:.4f}\n\n"

        if self.calls:
            summary += "DETAILED BREAKDOWN:\n"
            summary += "-" * 70 + "\n"
            for call in self.calls:
                summary += f"\n[{call['agent'].upper()}] {call['model']}\n"
                summary += f"  Input:  {call['input_tokens']:,} tokens (${call['input_cost']:.4f})\n"
                summary += f"  Output: {call['output_tokens']:,} tokens (${call['output_cost']:.4f})\n"
                summary += f"  Total:  ${call['total_cost']:.4f}\n"

        summary += "\n" + "=" * 70 + "\n"
        return summary

    def log_cost_message(self):
        """Return a log message with cost info."""
        return f"[COST] Total so far: ${self.total_cost:.4f} ({self.total_input_tokens + self.total_output_tokens} tokens)"
