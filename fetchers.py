"""Fetchers for blogs and Twitter to discover sources."""

import re
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    import tweepy
except ImportError:
    tweepy = None


class BlogFetcher:
    """Fetches and analyzes blog content to discover referenced sources."""

    def __init__(self):
        pass

    async def fetch_rss_feed(self, rss_url: str) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS feed.

        Returns:
            List of {title, link, content, published} dicts
        """
        if not feedparser:
            raise ImportError("feedparser not installed. Run: pip install feedparser")

        try:
            feed = feedparser.parse(rss_url)
            entries = []

            for entry in feed.entries[:10]:  # Get last 10 posts
                entries.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "content": entry.get("summary", ""),
                    "published": entry.get("published", datetime.now().isoformat()),
                    "source": rss_url
                })

            return entries
        except Exception as e:
            print(f"Error fetching RSS feed {rss_url}: {e}")
            return []

    def extract_referenced_sources(self, content: str) -> List[Dict[str, str]]:
        """
        Extract URLs and mentions from blog content.

        Returns:
            List of {url, text, type} where type is "url" or "mention"
        """
        sources = []

        # Extract URLs
        url_pattern = r'https?://[^\s\)]*'
        urls = re.findall(url_pattern, content)
        for url in urls:
            # Skip common services (Twitter, LinkedIn, etc as destinations, not as sources)
            if not any(skip in url for skip in ['facebook.com', 'instagram.com']):
                sources.append({
                    "url": url,
                    "text": url,
                    "type": "url"
                })

        # Extract @ mentions (Twitter handles)
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, content)
        for mention in mentions:
            sources.append({
                "handle": mention,
                "text": f"@{mention}",
                "type": "mention"
            })

        return sources

    async def analyze_blog(self, blog_name: str, rss_url: str) -> List[Dict[str, Any]]:
        """
        Fetch and analyze a blog for referenced sources.

        Returns:
            List of discovered sources {name, url, handle, type}
        """
        entries = await self.fetch_rss_feed(rss_url)
        discovered = []

        for entry in entries:
            sources = self.extract_referenced_sources(entry["content"])
            for source in sources:
                if source["type"] == "url":
                    discovered.append({
                        "name": source.get("text", ""),
                        "url": source.get("url", ""),
                        "type": "blog",
                        "found_in": blog_name
                    })
                elif source["type"] == "mention":
                    discovered.append({
                        "name": f"@{source['handle']}",
                        "handle": source["handle"],
                        "type": "twitter",
                        "found_in": blog_name
                    })

        return discovered


class TwitterFetcher:
    """Fetches Twitter data using API v2 to discover referenced sources."""

    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize Twitter fetcher with bearer token."""
        if not tweepy:
            raise ImportError("tweepy not installed. Run: pip install tweepy")

        self.bearer_token = bearer_token or os.environ.get("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not provided or set in environment")

        self.client = tweepy.Client(bearer_token=self.bearer_token)

    async def get_user_timeline(self, handle: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch recent tweets from a user.

        Returns:
            List of {id, text, created_at, author_id} dicts
        """
        try:
            # Get user ID from handle
            user = self.client.get_user(username=handle)
            if not user.data:
                return []

            # Get recent tweets
            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics'],
                expansions=['author_id']
            )

            if not tweets.data:
                return []

            return [{
                "id": tweet.id,
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
                "author_id": user.data.id
            } for tweet in tweets.data]

        except Exception as e:
            print(f"Error fetching timeline for @{handle}: {e}")
            return []

    def extract_twitter_sources(self, tweet_text: str) -> List[Dict[str, str]]:
        """Extract handles and URLs from tweet text."""
        sources = []

        # Extract @ mentions (excluding the original author)
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, tweet_text)
        for mention in mentions:
            sources.append({
                "handle": mention,
                "type": "twitter"
            })

        # Extract URLs
        url_pattern = r'https?://[^\s]*'
        urls = re.findall(url_pattern, tweet_text)
        for url in urls:
            sources.append({
                "url": url,
                "type": "url"
            })

        return sources

    async def analyze_user(self, handle: str) -> List[Dict[str, Any]]:
        """
        Analyze a Twitter user for referenced sources.

        Returns:
            List of discovered sources {name, url, handle, type}
        """
        tweets = await self.get_user_timeline(handle, max_results=15)
        discovered = []

        for tweet in tweets:
            sources = self.extract_twitter_sources(tweet["text"])
            for source in sources:
                if source["type"] == "twitter":
                    discovered.append({
                        "name": f"@{source['handle']}",
                        "handle": source["handle"],
                        "type": "twitter",
                        "found_in": f"@{handle}",
                        "last_active": tweet["created_at"]
                    })
                elif source["type"] == "url":
                    discovered.append({
                        "name": source.get("url", ""),
                        "url": source["url"],
                        "type": "blog",
                        "found_in": f"@{handle}",
                        "last_active": tweet["created_at"]
                    })

        return discovered


async def discover_sources(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Discover 2nd-degree sources from primary sources.

    Returns:
        List of discovered sources
    """
    all_discovered = []

    # Analyze blogs
    if config.get("primary_sources", {}).get("blogs"):
        blog_fetcher = BlogFetcher()
        for blog in config["primary_sources"]["blogs"]:
            sources = await blog_fetcher.analyze_blog(blog["name"], blog["url"])
            all_discovered.extend(sources)

    # Analyze Twitter accounts
    if config.get("primary_sources", {}).get("twitter"):
        try:
            twitter_fetcher = TwitterFetcher()
            for account in config["primary_sources"]["twitter"]:
                sources = await twitter_fetcher.analyze_user(account["handle"])
                all_discovered.extend(sources)
        except ValueError as e:
            print(f"Skipping Twitter analysis: {e}")

    return all_discovered
