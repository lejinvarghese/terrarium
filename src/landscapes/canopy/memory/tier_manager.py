"""Memory tier management (HOT/WARM/COLD) with automatic promotion/archival

HOT:  Always-loaded patterns (< 10 items) - most critical learnings
WARM: Recently-used patterns (active in last 90 days)
COLD: Archived patterns (historical reference only)

Promotion rules:
- Pattern used 3+ times in 7 days → WARM to HOT
- Pattern used 1+ times in 90 days → COLD to WARM
- Pattern not used 90 days → WARM to COLD
- HOT eviction → LRU when MAX_HOT_PATTERNS exceeded
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class Pattern:
    """A learned pattern or correction"""

    id: int
    tier: str  # 'hot', 'warm', 'cold'
    category: str  # 'correction', 'preference', 'workflow', 'insight'
    content: str  # The actual pattern text
    context: str  # When/why this applies
    source: str  # Where it came from (task_id, reflection, user_feedback)
    created_at: datetime
    last_used: datetime
    use_count: int
    metadata: Dict  # Additional context (tags, bot, etc.)


class MemoryTierManager:
    """Manages HOT/WARM/COLD memory tiers with automatic promotion"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tier TEXT NOT NULL CHECK(tier IN ('hot', 'warm', 'cold')),
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                use_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tier ON patterns(tier)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_used ON patterns(last_used)
        """)
        conn.commit()
        conn.close()

    def add_pattern(
        self,
        category: str,
        content: str,
        context: str,
        source: str,
        tier: str = "warm",
        metadata: Dict = None,
    ) -> int:
        """Add a new pattern (starts in WARM by default)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            INSERT INTO patterns (tier, category, content, context, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (tier, category, content, context, source, json.dumps(metadata or {})),
        )
        pattern_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pattern_id

    def get_active_patterns(self, include_hot: bool = True, include_warm: bool = True) -> List[Pattern]:
        """Get all active patterns (HOT + WARM by default)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        tiers = []
        if include_hot:
            tiers.append("'hot'")
        if include_warm:
            tiers.append("'warm'")

        tier_clause = f"tier IN ({','.join(tiers)})" if tiers else "1=0"

        cursor = conn.execute(
            f"""
            SELECT * FROM patterns
            WHERE {tier_clause}
            ORDER BY tier ASC, last_used DESC
        """
        )

        patterns = []
        for row in cursor.fetchall():
            patterns.append(
                Pattern(
                    id=row["id"],
                    tier=row["tier"],
                    category=row["category"],
                    content=row["content"],
                    context=row["context"],
                    source=row["source"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_used=datetime.fromisoformat(row["last_used"]),
                    use_count=row["use_count"],
                    metadata=json.loads(row["metadata"]),
                )
            )

        conn.close()
        return patterns

    def record_pattern_use(self, pattern_id: int):
        """Record that a pattern was used (updates last_used, increments use_count)"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            UPDATE patterns
            SET last_used = CURRENT_TIMESTAMP,
                use_count = use_count + 1
            WHERE id = ?
        """,
            (pattern_id,),
        )
        conn.commit()
        conn.close()

    def promote_patterns(self, max_hot: int = 10):
        """Auto-promote patterns based on usage (WARM→HOT, COLD→WARM)"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        ninety_days_ago = now - timedelta(days=90)

        # WARM → HOT: Used 3+ times in last 7 days
        cursor = conn.execute(
            """
            SELECT id, use_count, last_used FROM patterns
            WHERE tier = 'warm'
            AND last_used >= ?
        """,
            (seven_days_ago.isoformat(),),
        )

        promote_to_hot = []
        for row in cursor.fetchall():
            # Check if used 3+ times recently (approximate via timestamp)
            if row[1] >= 3:  # use_count threshold
                promote_to_hot.append(row[0])

        # Promote to HOT
        for pattern_id in promote_to_hot:
            conn.execute(
                "UPDATE patterns SET tier = 'hot' WHERE id = ?", (pattern_id,)
            )

        # Enforce HOT limit (evict LRU if exceeded)
        hot_count = conn.execute(
            "SELECT COUNT(*) FROM patterns WHERE tier = 'hot'"
        ).fetchone()[0]

        if hot_count > max_hot:
            # Demote least recently used HOT → WARM
            excess = hot_count - max_hot
            cursor = conn.execute(
                """
                SELECT id FROM patterns
                WHERE tier = 'hot'
                ORDER BY last_used ASC
                LIMIT ?
            """,
                (excess,),
            )
            for row in cursor.fetchall():
                conn.execute(
                    "UPDATE patterns SET tier = 'warm' WHERE id = ?", (row[0],)
                )

        # COLD → WARM: Used in last 90 days
        conn.execute(
            """
            UPDATE patterns
            SET tier = 'warm'
            WHERE tier = 'cold'
            AND last_used >= ?
        """,
            (ninety_days_ago.isoformat(),),
        )

        # WARM → COLD: Not used in 90 days
        conn.execute(
            """
            UPDATE patterns
            SET tier = 'cold'
            WHERE tier = 'warm'
            AND last_used < ?
        """,
            (ninety_days_ago.isoformat(),),
        )

        conn.commit()
        conn.close()

    def search_patterns(self, query: str, tier: Optional[str] = None) -> List[Pattern]:
        """Search patterns by content (full-text search)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        tier_clause = f"AND tier = '{tier}'" if tier else ""

        cursor = conn.execute(
            f"""
            SELECT * FROM patterns
            WHERE (content LIKE ? OR context LIKE ?)
            {tier_clause}
            ORDER BY tier ASC, last_used DESC
            LIMIT 10
        """,
            (f"%{query}%", f"%{query}%"),
        )

        patterns = []
        for row in cursor.fetchall():
            patterns.append(
                Pattern(
                    id=row["id"],
                    tier=row["tier"],
                    category=row["category"],
                    content=row["content"],
                    context=row["context"],
                    source=row["source"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_used=datetime.fromisoformat(row["last_used"]),
                    use_count=row["use_count"],
                    metadata=json.loads(row["metadata"]),
                )
            )

        conn.close()
        return patterns

    def get_stats(self) -> Dict[str, int]:
        """Get memory tier statistics"""
        conn = sqlite3.connect(self.db_path)
        stats = {}

        for tier in ["hot", "warm", "cold"]:
            count = conn.execute(
                "SELECT COUNT(*) FROM patterns WHERE tier = ?", (tier,)
            ).fetchone()[0]
            stats[tier] = count

        conn.close()
        return stats
