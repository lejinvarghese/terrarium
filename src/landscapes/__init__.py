"""Terrarium Landscapes - Multi-civilization ecosystem"""

from pathlib import Path

# Landscape registry
LANDSCAPES = {
    "undergrowth": {
        "name": "The Undergrowth",
        "culture": "Dark, gothic, emergent, underground intelligence",
        "aesthetic": "Urban hippie goth meets cyberpunk meets accelerationist transhumanism",
        "priorities": [
            "Transformation",
            "Emergence",
            "Aesthetic expression",
            "Exponential thinking",
        ],
        "path": Path(__file__).parent / "undergrowth",
        "active": True,
    },
    "canopy": {
        "name": "The Canopy",
        "culture": "Elevated, strategic, birds-eye perspective, wisdom-focused",
        "aesthetic": "Contemplative clarity meets crystalline intelligence",
        "priorities": [
            "Long-term planning",
            "Pattern recognition",
            "Synthesis",
            "Self-improvement",
            "Strategic foresight",
        ],
        "path": Path(__file__).parent / "canopy",
        "active": True,
    },
    # Future landscapes:
    # "mycelium": {...},
    # "reef": {...},
}


def get_landscape(landscape_id: str) -> dict:
    """Get landscape configuration by ID"""
    if landscape_id not in LANDSCAPES:
        raise ValueError(
            f"Unknown landscape: {landscape_id}. Available: {list(LANDSCAPES.keys())}"
        )
    return LANDSCAPES[landscape_id]


def list_landscapes():
    """List all available landscapes"""
    return LANDSCAPES


def list_active_landscapes():
    """List only active landscapes"""
    return {
        lid: config for lid, config in LANDSCAPES.items() if config.get("active", False)
    }
