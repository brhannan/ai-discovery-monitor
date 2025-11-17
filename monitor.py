"""Main monitor loop with scheduling."""

import asyncio
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

from db import DiscoveryDB
from fetchers import discover_sources, BlogFetcher, TwitterFetcher
from scoring import RecommendationEngine
from notifications import NotificationHandler


class AIDiscoveryMonitor:
    """Main coordinator for AI discovery monitoring."""

    def __init__(self, config_path: str = "config.yaml", db_path: str = "discovery.db"):
        """Initialize monitor with config and database."""
        self.config_path = Path(config_path)
        self.db = DiscoveryDB(db_path)

        # Load config
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.interests = self.config.get("interests", [])
        self.recommendation_engine = RecommendationEngine(self.interests)
        self.notification_handler = NotificationHandler(
            format=self.config.get("notifications", {}).get("format", "markdown"),
            output_file=self.config.get("notifications", {}).get("output_file", "recommendations.md")
        )

        # Initialize database with primary sources
        self._init_primary_sources()

    def _init_primary_sources(self):
        """Load primary sources from config into database."""
        primary = self.config.get("primary_sources", {})

        for blog in primary.get("blogs", []):
            self.db.add_primary_source(
                name=blog["name"],
                url=blog["url"],
                source_type="blog"
            )

        for account in primary.get("twitter", []):
            self.db.add_primary_source(
                name=account["name"],
                handle=account["handle"],
                source_type="twitter"
            )

    async def discover_and_score(self):
        """
        Main discovery loop:
        1. Discover 2nd-degree sources from primary sources
        2. Score them for relevance
        3. Check against thresholds
        4. Return recommendations
        """
        print("\n🔍 Starting discovery process...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Discover sources
        print("📡 Discovering sources from primary sources...")
        discovered = await discover_sources(self.config)

        if not discovered:
            print("⚠️  No sources discovered. Check your configuration and API access.")
            return []

        print(f"✅ Discovered {len(discovered)} potential sources\n")

        # Add to database and score
        print("🎯 Scoring and filtering sources...\n")
        scored_sources = []

        for source in discovered:
            # Check if already in database
            existing = self.db.get_source_by_name(source.get("name", ""), "discovered")

            # Calculate relevance score
            relevance_score = self.recommendation_engine.scorer.score_name(source.get("name", ""))

            if existing:
                # Update existing source
                print(f"  ↪️  {source.get('name')} (already tracked)")
                source["id"] = existing["id"]
                source["citation_count"] = existing.get("citation_count", 0)
                source["relevance_score"] = max(existing.get("relevance_score", 0), relevance_score)
            else:
                # Add new source
                source["relevance_score"] = relevance_score
                source["citation_count"] = 1
                source_id = self.db.add_discovered_source(
                    name=source.get("name", ""),
                    url=source.get("url"),
                    handle=source.get("handle"),
                    source_type=source.get("type", "unknown"),
                    relevance_score=relevance_score
                )
                source["id"] = source_id
                print(f"  ✨ {source.get('name')} (NEW - score: {relevance_score:.2f})")

            scored_sources.append(source)

        # Get recommendation thresholds from config
        thresholds = self.config.get("recommendation_thresholds", {})
        min_relevance = thresholds.get("min_relevance_score", 0.7)
        citation_threshold = thresholds.get("min_citation_count", 2)
        max_age = thresholds.get("max_source_age_days", 90)

        # Get recommended sources
        print(f"\n🏆 Finding sources to recommend...")
        print(f"   (min relevance: {min_relevance:.0%}, min citations: {citation_threshold})\n")

        candidates = self.db.get_recommended_sources(min_relevance, citation_threshold)

        if not candidates:
            print("   No sources meet recommendation criteria yet.\n")
            return []

        # Rank recommendations
        recommendations = self.recommendation_engine.rank_sources(candidates)

        return recommendations

    async def run_once(self):
        """Run the discovery process once."""
        try:
            recommendations = await self.discover_and_score()

            if recommendations:
                print(f"\n📬 Found {len(recommendations)} sources to recommend:\n")

                # Show recommendations
                for source, reasoning in recommendations:
                    print(f"  • {source.get('name')}")
                    print(f"    └─ {reasoning}\n")

                # Send notifications
                print("\n📤 Sending notifications...")
                self.notification_handler.notify(recommendations)

                # Mark as sent
                for source, _ in recommendations:
                    self.db.mark_recommendation_sent(
                        source["id"],
                        reasoning=f"Relevance: {source.get('relevance_score', 0):.2%}"
                    )

                print("✅ Done!")
            else:
                print("\n📭 No new recommendations at this time.")

        except Exception as e:
            print(f"\n❌ Error during discovery: {e}")
            import traceback
            traceback.print_exc()

    def close(self):
        """Clean up resources."""
        self.db.close()


async def main():
    """Main entry point."""
    monitor = AIDiscoveryMonitor()

    try:
        await monitor.run_once()
    finally:
        monitor.close()


if __name__ == "__main__":
    asyncio.run(main())
