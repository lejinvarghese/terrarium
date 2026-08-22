#!/usr/bin/env python3
"""Seed profile facts into Qdrant.

Idempotent: facts are deduplicated on exact content hash, so re-running is safe.
These land as category="profile" and are injected verbatim into every agent
prompt by src/engine/build_prompt.py.
"""

from src.engine.memory_store import DANIELLE_USER_ID, PROFILE, USER_ID, add_fact

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
    # Phrase preferences positively. A fact written as "X (not Y)" puts Y in the
    # embedding alongside her name, so every retrieval hands the agent Y as well.
    "Beverage: Yorkshire Tea is her drink, morning and through the day",
    "Morning routine: Yorkshire tea with biscuits, then meds",
    "Snacks: Biscuits, cheese, carrots",
    "Has ADHD - uses Pepper bot for accountability",
    "Work: Ontario Health, improving emergency response; on the sepsis crisis task force",
    "Joined a biking club - rides are a regular anchor in her week",
    "Loves wine and is actively moderating her intake - never offer wine, drinks, or bars as a reward or wind-down",
]


def migrate():
    print("=" * 60)
    print("SEEDING PROFILE FACTS → Qdrant")
    print("=" * 60)

    # Lejin's facts
    print(f"\n📝 Storing {len(LEJIN_FACTS)} facts for Lejin...")
    for fact in LEJIN_FACTS:
        result = add_fact(fact, user_id=USER_ID, agent_id="system", category=PROFILE)
        print(f"  {'✓' if result.get('status') == 'added' else '~'} {fact[:70]}...")

    # Danielle's facts
    print(f"\n📝 Storing {len(DANIELLE_FACTS)} facts for Danielle...")
    for fact in DANIELLE_FACTS:
        result = add_fact(fact, user_id=DANIELLE_USER_ID, agent_id="system", category=PROFILE)
        print(f"  {'✓' if result.get('status') == 'added' else '~'} {fact[:70]}...")

    print("\n✅ Migration complete!")
    print("\nNote: '~' means this exact fact was already stored (skipped)")


if __name__ == "__main__":
    migrate()
