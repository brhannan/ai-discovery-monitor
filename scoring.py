"""Scoring and recommendation logic for discovered sources."""

import re
from typing import List, Dict, Any
from datetime import datetime, timedelta


class RelevanceScorer:
    """Scores discovered sources based on relevance to user interests."""

    def __init__(self, interests: List[str]):
        """Initialize with user interests."""
        self.interests = [i.lower() for i in interests]

    def score_content(self, content: str) -> float:
        """
        Score content relevance based on how many user interests are mentioned.
        Returns score 0.0-1.0.
        """
        if not content:
            return 0.0

        content_lower = content.lower()
        matched_interests = sum(1 for interest in self.interests if interest in content_lower)

        if not self.interests:
            return 0.5  # Default if no interests defined

        return min(1.0, matched_interests / len(self.interests))

    def score_name(self, name: str) -> float:
        """Score based on how relevant the source name is."""
        if not name:
            return 0.0

        name_lower = name.lower()
        matched_interests = sum(1 for interest in self.interests if interest in name_lower)

        if matched_interests > 0:
            return min(1.0, matched_interests / len(self.interests))
        return 0.3  # Low score if name doesn't match interests

    def calculate_combined_score(self, source: Dict[str, Any], content: str = "") -> float:
        """
        Calculate combined relevance score.
        - 40% name relevance
        - 60% content relevance
        """
        name_score = self.score_name(source.get("name", "")) * 0.4
        content_score = self.score_content(content) * 0.6

        return name_score + content_score


class RecommendationEngine:
    """Determines which sources should be recommended."""

    def __init__(self, interests: List[str]):
        self.scorer = RelevanceScorer(interests)

    def should_recommend(self, source: Dict[str, Any],
                        min_relevance: float = 0.7,
                        citation_threshold: int = 2,
                        max_age_days: int = 90) -> tuple[bool, str]:
        """
        Determine if a source should be recommended.

        Args:
            source: Source dict with relevance_score, citation_count, last_active
            min_relevance: Minimum relevance score (0-1)
            citation_threshold: Minimum number of citations from primary sources
            max_age_days: Maximum days since source was active

        Returns:
            (should_recommend, reasoning)
        """
        reasons = []

        # Check relevance score
        relevance_score = source.get("relevance_score", 0.0)
        if relevance_score < min_relevance:
            return False, f"Relevance score too low: {relevance_score:.2f} < {min_relevance}"

        reasons.append(f"Good relevance: {relevance_score:.2f}")

        # Check citation count
        citation_count = source.get("citation_count", 0)
        if citation_count < citation_threshold:
            return False, f"Not enough citations: {citation_count} < {citation_threshold}"

        reasons.append(f"Cited {citation_count} times by trusted sources")

        # Check source freshness
        last_active = source.get("last_active")
        if last_active:
            try:
                last_active_date = datetime.fromisoformat(last_active)
                age_days = (datetime.now() - last_active_date).days
                if age_days > max_age_days:
                    return False, f"Source inactive for too long: {age_days} days"
                reasons.append(f"Actively posting ({age_days} days ago)")
            except:
                pass

        return True, " | ".join(reasons)

    def rank_sources(self, sources: List[Dict[str, Any]]) -> List[tuple[Dict[str, Any], str]]:
        """
        Rank sources by recommendation strength.

        Returns:
            List of (source, reasoning) tuples, sorted by recommendation strength
        """
        recommendations = []

        for source in sources:
            should_recommend, reasoning = self.should_recommend(source)
            if should_recommend:
                # Calculate recommendation strength for sorting
                strength = (
                    (source.get("relevance_score", 0) * 0.5) +
                    ((source.get("citation_count", 0) / 10) * 0.5)  # Normalize citation count
                )
                recommendations.append((source, reasoning, strength))

        # Sort by strength (descending)
        recommendations.sort(key=lambda x: x[2], reverse=True)

        return [(src, reason) for src, reason, _ in recommendations]
