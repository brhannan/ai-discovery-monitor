"""Database layer for tracking sources and recommendations."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class DiscoveryDB:
    """SQLite database for tracking sources and recommendations."""

    def __init__(self, db_path: str = "discovery.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Primary sources table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS primary_sources (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT,
                    source_type TEXT,
                    handle TEXT,
                    last_checked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Discovered 2nd-degree sources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discovered_sources (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT,
                    handle TEXT,
                    source_type TEXT,
                    relevance_score REAL,
                    citation_count INTEGER DEFAULT 0,
                    last_active TIMESTAMP,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    recommendation_sent BOOLEAN DEFAULT 0,
                    recommendation_sent_at TIMESTAMP
                )
            """)

            # Citation records (links between primary and discovered sources)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citations (
                    id INTEGER PRIMARY KEY,
                    primary_source_id INTEGER NOT NULL,
                    discovered_source_id INTEGER NOT NULL,
                    citation_text TEXT,
                    citation_date TIMESTAMP,
                    FOREIGN KEY(primary_source_id) REFERENCES primary_sources(id),
                    FOREIGN KEY(discovered_source_id) REFERENCES discovered_sources(id)
                )
            """)

            # Recommendation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY,
                    source_id INTEGER NOT NULL,
                    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    relevance_score REAL,
                    reasoning TEXT,
                    FOREIGN KEY(source_id) REFERENCES discovered_sources(id)
                )
            """)

            conn.commit()

    def add_primary_source(self, name: str, url: Optional[str] = None,
                          source_type: str = "blog", handle: Optional[str] = None) -> int:
        """Add a primary source to track."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO primary_sources (name, url, source_type, handle)
                VALUES (?, ?, ?, ?)
            """, (name, url, source_type, handle))
            conn.commit()
            cursor.execute("SELECT id FROM primary_sources WHERE name = ?", (name,))
            return cursor.fetchone()[0]

    def add_discovered_source(self, name: str, url: Optional[str] = None,
                             source_type: str = "blog", handle: Optional[str] = None,
                             relevance_score: float = 0.0) -> int:
        """Add a discovered 2nd-degree source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO discovered_sources
                (name, url, handle, source_type, relevance_score, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, url, handle, source_type, relevance_score, datetime.now().isoformat()))
            conn.commit()
            cursor.execute("SELECT id FROM discovered_sources WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def record_citation(self, primary_source_id: int, discovered_source_id: int,
                       citation_text: str = ""):
        """Record that a primary source cited a discovered source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO citations
                (primary_source_id, discovered_source_id, citation_text, citation_date)
                VALUES (?, ?, ?, ?)
            """, (primary_source_id, discovered_source_id, citation_text, datetime.now().isoformat()))

            # Update citation count
            cursor.execute("""
                UPDATE discovered_sources
                SET citation_count = (
                    SELECT COUNT(*) FROM citations
                    WHERE discovered_source_id = ?
                )
                WHERE id = ?
            """, (discovered_source_id, discovered_source_id))

            conn.commit()

    def get_recommended_sources(self, min_relevance: float = 0.7,
                               citation_threshold: int = 2) -> List[Dict[str, Any]]:
        """Get sources that meet recommendation criteria and haven't been recommended yet."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM discovered_sources
                WHERE relevance_score >= ?
                AND citation_count >= ?
                AND recommendation_sent = 0
                ORDER BY relevance_score DESC, citation_count DESC
            """, (min_relevance, citation_threshold))

            return [dict(row) for row in cursor.fetchall()]

    def mark_recommendation_sent(self, source_id: int, reasoning: str = ""):
        """Mark that a recommendation has been sent for a source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE discovered_sources
                SET recommendation_sent = 1, recommendation_sent_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), source_id))

            cursor.execute("""
                INSERT INTO recommendations
                (source_id, relevance_score, reasoning)
                SELECT id, relevance_score, ? FROM discovered_sources WHERE id = ?
            """, (reasoning, source_id))

            conn.commit()

    def get_source_by_name(self, name: str, source_type: str = "discovered") -> Optional[Dict[str, Any]]:
        """Get a source by name."""
        table = "discovered_sources" if source_type == "discovered" else "primary_sources"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE name = ?", (name,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def close(self):
        """Close database connection."""
        # SQLite connections are closed automatically
        pass
