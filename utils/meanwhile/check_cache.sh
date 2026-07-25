#!/bin/bash
# Quick cache status checker

CACHE="$HOME/.cache/meanwhile/headlines.json"

if [ -f "$CACHE" ]; then
    echo "✓ Cache exists: $CACHE"
    python3 << 'EOF'
import json, time

with open("/home/starscream/.cache/meanwhile/headlines.json") as f:
    data = json.load(f)
    items = data.get("items", [])
    timestamp = data.get("at", 0)
    age = int(time.time() - timestamp)

    news = [i for i in items if i["kind"] == "news"]
    local = [i for i in items if i["kind"] == "local"]

    print(f"  Items: {len(items)} total")
    print(f"  News: {len(news)} (cyan)")
    print(f"  Local intel: {len(local)} (red)")
    print(f"  Age: {age} seconds ago ({age//60} minutes)")

    if len(items) > 0:
        print(f"\n  Sample headlines:")
        for item in items[:3]:
            print(f"    - {item['text'][:70]}...")
EOF
else
    echo "✗ No cache file at: $CACHE"
    echo "  Meanwhile hasn't fetched yet"
fi
