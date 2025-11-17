"""Notification system for recommendations."""

from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path


class NotificationFormatter:
    """Formats recommendations for various output formats."""

    @staticmethod
    def format_markdown(recommendations: List[tuple[Dict[str, Any], str]]) -> str:
        """Format recommendations as Markdown."""
        if not recommendations:
            return "# AI Discovery Recommendations\n\nNo new sources to recommend at this time.\n"

        md = "# AI Discovery Recommendations\n\n"
        md += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for source, reasoning in recommendations:
            md += "## " + source.get("name", "Unknown") + "\n\n"

            if source.get("url"):
                md += f"- **URL**: [{source['url']}]({source['url']})\n"
            if source.get("handle"):
                md += f"- **Twitter**: [@{source['handle']}](https://twitter.com/{source['handle']})\n"

            md += f"- **Type**: {source.get('source_type', 'unknown')}\n"
            md += f"- **Relevance Score**: {source.get('relevance_score', 0):.2%}\n"
            md += f"- **Citations**: {source.get('citation_count', 0)} times\n"
            md += f"- **Why recommend**: {reasoning}\n\n"

        return md

    @staticmethod
    def format_json(recommendations: List[tuple[Dict[str, Any], str]]) -> str:
        """Format recommendations as JSON."""
        import json

        data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(recommendations),
            "recommendations": [
                {
                    "name": source.get("name"),
                    "url": source.get("url"),
                    "handle": source.get("handle"),
                    "type": source.get("source_type"),
                    "relevance_score": source.get("relevance_score"),
                    "citation_count": source.get("citation_count"),
                    "reasoning": reasoning
                }
                for source, reasoning in recommendations
            ]
        }

        return json.dumps(data, indent=2)

    @staticmethod
    def format_text(recommendations: List[tuple[Dict[str, Any], str]]) -> str:
        """Format recommendations as plain text."""
        if not recommendations:
            return "AI Discovery Recommendations\n\nNo new sources to recommend at this time.\n"

        text = "AI Discovery Recommendations\n"
        text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "=" * 50 + "\n\n"

        for i, (source, reasoning) in enumerate(recommendations, 1):
            text += f"{i}. {source.get('name', 'Unknown')}\n"

            if source.get("url"):
                text += f"   URL: {source['url']}\n"
            if source.get("handle"):
                text += f"   Twitter: @{source['handle']}\n"

            text += f"   Type: {source.get('source_type', 'unknown')}\n"
            text += f"   Relevance: {source.get('relevance_score', 0):.2%}\n"
            text += f"   Citations: {source.get('citation_count', 0)}\n"
            text += f"   Why: {reasoning}\n\n"

        return text


class NotificationHandler:
    """Handles sending notifications in various formats."""

    def __init__(self, format: str = "markdown", output_file: str = "recommendations.md"):
        """
        Initialize notification handler.

        Args:
            format: Output format ("markdown", "json", "text")
            output_file: File to write recommendations to
        """
        self.format = format
        self.output_file = Path(output_file)
        self.formatter = NotificationFormatter()

    def notify(self, recommendations: List[tuple[Dict[str, Any], str]]) -> str:
        """
        Send notifications for recommendations.

        Returns:
            Formatted output
        """
        if self.format == "markdown":
            content = self.formatter.format_markdown(recommendations)
        elif self.format == "json":
            content = self.formatter.format_json(recommendations)
        else:
            content = self.formatter.format_text(recommendations)

        # Write to file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(content, encoding="utf-8")

        print(f"\n✅ Recommendations saved to: {self.output_file}")

        return content

    def notify_console(self, recommendations: List[tuple[Dict[str, Any], str]]) -> None:
        """Print recommendations to console."""
        if self.format == "markdown":
            content = self.formatter.format_markdown(recommendations)
        elif self.format == "json":
            content = self.formatter.format_json(recommendations)
        else:
            content = self.formatter.format_text(recommendations)

        print(content)
