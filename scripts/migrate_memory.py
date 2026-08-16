#!/usr/bin/env python3
"""Migrate TERRARIUM_MEMORY.md → Qdrant memory system"""

from src.engine.memory_config import DANIELLE_USER_ID, USER_ID, get_memory

LEJIN_FACTS = [
    # Identity & Background
    "Name: Lejin, born June 22, 1989 at 10:45 AM",
    "Astrology: Cancer sun, Aquarius moon, Virgo rising",
    "Location: 510, 1169 Queen Street West, Toronto, Canada",
    "Personality: INFJ with Hero and Sage archetypes",
    "Identity: Continuous learner, scientist, engineer, philosopher, artist, aspiring polymath",
    "Values: Integrity, innovation, pluralism, human-centric progress",
    "Aesthetic: Urban hippie goth - Bohemian/Scandinavian elegance meets Goth/Cyberpunk darkness",
    # Favorites
    "Favorite color: Black",
    "Favorite drinks: Wine and whiskey",
    "Favorite sport: Basketball",
    # Home & Lifestyle
    "Pet: Piqiu (pronounced Pi-Chou) - brindle pie French Bulldog",
    "Home: Filled with plants and terrarium of AI assistants",
    "Neighborhood: Queen West & Roncesvalles - vibrant, artsy area",
    "Weekday preference: Close to home - reading, workouts, cooking",
    "Weekend preference: Exploring local food, nature, beaches, culture in warm weather",
    # Work & Career
    "Work: Staff Machine Learning Engineer at Tubi",
    "Work schedule: In-office Tuesday and Thursday",
    "Work style: Needs tasks broken into concrete daily items",
    "Technical interests: Adaptive intelligent systems, optimization algorithms, network science, psychology, complexity science, multimodal large language models, robotics",
    # Health & Fitness
    "Fitness goals: Gain lean muscle, burn fat, improve flexibility",
    "Activities: Gym strength training",
    "Diet: High protein, low carb",
    "Cuisine preference: Italian, meat and seafood, seasonal ingredients",
    "Cooking inspiration: Gordon Ramsay, Ina Garten, Jamie Oliver",
    "Supplements: Whey protein, cottage cheese, creatine, maca, ashwagandha",
    "Family health history: Diabetes, cancer, heart disease, high blood pressure (no personal diagnoses)",
    # Interests & Reading
    "Big interests: Plants, nature, sci-fi, fantasy (huge Trekkie), cooking, walking/streetcar",
    "Current reading: Cryptonomicon, Private Truths Public Lies, Software Engineering at Google, The Flavour Matrix, Gödel Escher Bach",
    "Ambition: Uncover mysteries of intelligence bridging scientific paradigms, help humans become multi-planetary",
    "2025 goals: Minimize social media, improve concentration, gain lean muscle, read more books/papers, build applications",
    "Free time needs: Options and possibilities - dislikes empty unstructured time",
    # Communication Style
    "Communication preference: Concise, structured, actionable - skip formalities",
    "Engagement style: Don't recite known facts - assume familiarity",
    "INFJ cognitive functions: Honors vision (Ni), empowers mission (Fe), sharpens plan (Ti), manifests reality (Se)",
]

DANIELLE_FACTS = [
    "Name: Danielle Mearns, born December 10, 1989",
    "Background: British, grew up in Regina",
    "Beverage: Yorkshire Tea (not coffee)",
    "Morning routine: Yorkshire tea with biscuits, then meds",
    "Snacks: Biscuits, cheese, carrots",
    "Has ADHD - uses Pepper bot for accountability",
]


def migrate():
    memory = get_memory()

    print("=" * 60)
    print("MIGRATING TERRARIUM_MEMORY.md → Qdrant")
    print("=" * 60)

    # Lejin's facts
    print(f"\n📝 Storing {len(LEJIN_FACTS)} facts for Lejin...")
    for fact in LEJIN_FACTS:
        result = memory.add(
            messages=[{"role": "assistant", "content": f"[profile] {fact}"}],
            user_id=USER_ID,
            agent_id="system",
        )
        stored = len(result.get("results", []))
        print(f"  {'✓' if stored > 0 else '~'} {fact[:70]}...")

    # Danielle's facts
    print(f"\n📝 Storing {len(DANIELLE_FACTS)} facts for Danielle...")
    for fact in DANIELLE_FACTS:
        result = memory.add(
            messages=[{"role": "assistant", "content": f"[profile] {fact}"}],
            user_id=DANIELLE_USER_ID,
            agent_id="system",
        )
        stored = len(result.get("results", []))
        print(f"  {'✓' if stored > 0 else '~'} {fact[:70]}...")

    print("\n✅ Migration complete!")
    print("\nNote: '~' means fact was similar to existing memory (skipped)")


if __name__ == "__main__":
    migrate()
