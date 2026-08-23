#!/usr/bin/env python3
"""Seed profile facts from data/profiles.json into Qdrant. Idempotent."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine import user_db
from src.engine.memory_store import PROFILE, add_fact

PROFILES_FILE = Path(__file__).parent.parent / "data" / "profiles.json"


def load_profiles() -> dict[str, list[str]]:
    """Load from data/profiles.json."""
    if not PROFILES_FILE.exists():
        print(f"ERROR: {PROFILES_FILE} not found")
        print('Create: {"username": ["fact1", "fact2", ...]}')
        sys.exit(1)
    with open(PROFILES_FILE) as f:
        return json.load(f)


def migrate():
    """Seed profiles into Qdrant."""
    profiles = load_profiles()

    print("=" * 60)
    print("SEEDING PROFILE FACTS → Qdrant")
    print("=" * 60)

    for username, facts in profiles.items():
        try:
            user_id = user_db.resolve_user_id(username)
            user = user_db.get_user(user_id)
            if not user:
                print(f"\n⚠️  User not found: '{username}'")
                continue

            print(f"\n📝 Storing {len(facts)} facts for {user.get('username')}...")

            for fact in facts:
                result = add_fact(fact, user_id=user_id, agent_id="system", category=PROFILE)
                status = "✓" if result.get("status") == "added" else "~"
                print(f"  {status} {fact[:70]}...")

        except ValueError as e:
            print(f"\n⚠️  Skipping unknown user '{username}': {e}")
            continue

    print("\n✅ Migration complete!")
    print("\nNote: '~' means this exact fact was already stored (skipped)")


if __name__ == "__main__":
    migrate()
