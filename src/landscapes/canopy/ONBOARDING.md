# Welcome to Fully Proactive Canopy 🌿

You've just enabled **comprehensive proactivity** for Canopy. Here's how to activate all the features.

## What Just Happened

Canopy now has:
- ✅ Full proactive architecture (`PROACTIVE.md`)
- ✅ Pantry tracking system (`pantry/`)
- ✅ Pattern learning (`patterns/`)
- ✅ Strategic goal tracking (`goals/`)
- ✅ Session state persistence (`SESSION-STATE.md`)
- ✅ Extended heartbeat monitoring (`HEARTBEAT-PROACTIVE.md`)

## Quick Start (5 minutes)

### Step 1: Set Your Food Preferences

Edit `pantry/preferences.md`:

```bash
# From Canopy directory
nano pantry/preferences.md
```

Fill in:
- Protein/carb/fat targets (if tracking macros)
- Foods you like/dislike
- Allergies or restrictions
- Weekly grocery budget
- Cooking constraints (time, equipment, skill level)

**Why this matters:** Canopy uses this to suggest recipes, build grocery lists, and stay within your budget.

### Step 2: Take Initial Pantry Inventory

Edit `pantry/current.md`:

```bash
nano pantry/current.md
```

Add what's currently in your fridge/pantry:
- Proteins (chicken, eggs, etc.)
- Carbs (rice, potatoes, etc.)
- Vegetables
- Staples (oils, spices, etc.)

**Why this matters:** Canopy tracks what's low, what's expiring, and what you need to restock.

### Step 3: Define Your Strategic Goals

Edit `goals/strategic.md`:

```bash
nano goals/strategic.md
```

Set 6-12 month goals for:
- Health & fitness (body recomp, gym frequency, etc.)
- Social & events (how many events/month, what types)
- Skill development (what you're learning)
- Career/professional (if relevant)
- Financial (savings, budget targets)

**Why this matters:** Canopy tracks progress and flags when you're deviating from goals.

### Step 4: Establish Baseline Patterns

Edit `patterns/2026-04.md`:

```bash
nano patterns/2026-04.md
```

Fill in current patterns:
- Meal prep frequency (e.g., "Weekly on Sundays")
- Recent events attended
- Grocery order pattern (e.g., "Fridays via Instacart")
- Gym visits this month

**Why this matters:** Canopy learns your rhythms and spots deviations.

### Step 5: Test Proactive Messaging

Send a message to Canopy via Telegram:

```
@canopy What's my pantry status?
```

Or via OpenClaw CLI:

```bash
openclaw agent --agent canopy --message "What's my pantry status?" --deliver --channel telegram --to 902949428
```

Canopy should:
1. Read your pantry/preferences
2. Identify what's low or missing
3. Suggest next steps

## What Canopy Will Do Proactively

Once you've completed the setup above, Canopy will:

### Tactical (Hours to Days)
- **Meal prep:** "Tomorrow is Sunday, your meal prep day. Grocery list ready?"
- **Low pantry:** "Running low on chicken and spinach. Restock?"
- **Expiring food:** "Spinach expires in 2 days. Use in tonight's meal?"
- **Event prep:** "LATEX event Saturday. Outfit ready? Rideshare booked?"

### Strategic (Weeks to Months)
- **Pattern breaks:** "No gym visits this week (usual: 4x/week). Everything okay?"
- **Budget alerts:** "Groceries 20% over budget this month. Need optimization?"
- **Goal tracking:** "You're 60% to body recomp goal. On track for 6-month target."
- **Recurring tasks:** "Last dentist visit was 5 months ago (usual: every 6). Time to book?"

### Meta (Months to Years)
- **Quarterly review:** "Q1 fitness: gym visits declined 30%. Adjust strategy or shift priorities?"
- **Trajectory analysis:** "Event attendance dropped from 4/month to 2/month. Life transition?"
- **Goal evolution:** "Body recomp goal achieved. Ready for next challenge?"

## Advanced Features

### Event Monitoring

Add event sources to `patterns/2026-04.md`:

```markdown
## Social Media Monitoring
- **Event sources:** @buddiesinbadtimes (Instagram), @undergrowthTO (Instagram)
```

Canopy will:
- Check 2x daily for new event posts
- Filter for your preferences (dark/gothic/kink/electronic)
- Alert when matches found
- Extract details (date, price, dress code, link)

### Grocery Automation

With preferences set, Canopy can:
- Auto-generate weekly grocery lists
- Find recipes matching your macros
- Estimate costs and stay within budget
- Suggest substitutions if over budget

### Pattern Learning

Canopy observes and learns:
- When you typically meal prep
- How often you order groceries
- What events you attend (types, frequency)
- Gym patterns (days, frequency)
- Budget trends

After 2-4 weeks, Canopy will have solid baselines and can spot deviations early.

## Proactive Message Examples

**You'll receive messages like:**

**Morning (8am):**
> [Canopy] Good morning. Three things:
> 1. Meal prep tomorrow. Grocery list ready ($47, 3 recipes). Order now?
> 2. Expiring today: spinach. Use in tonight's dinner?
> 3. New event: LATEX // HADAL ZONE, Apr 11. Add to calendar?

**Sunday Evening (8pm):**
> [Canopy] Weekly check-in:
> - Gym: 3 visits this week (target: 4, close!)
> - Groceries: $52 this week (target: $50, slightly over)
> - Next week: 2 events planned (good balance)

**Month End:**
> [Canopy] April summary:
> - Fitness: 14 gym visits (target: 16, 87%)
> - Social: 3 events attended (target: 4, 75%)
> - Budget: $210 groceries, $90 events = $300 total
> Insight: Gym consistency slipped mid-month. Rebalance May schedule?

## Adjusting Proactivity Level

**Too many messages?**

Edit `PROACTIVE.md` and adjust message priority thresholds:
- Only send priority 7+ (more selective)
- Only send 1 message max per heartbeat (less frequent)

**Too few messages?**

- Lower priority threshold to 3+
- Increase event monitoring to 3x daily
- Enable more pattern deviation checks

## Tools & Integrations

Canopy has access to:

**MCP Tools (already configured):**
- `mcp__google-calendar__list-events` - Calendar lookahead
- `mcp__spoonacular__search_recipes` - Recipe discovery
- `mcp__spoonacular__find_recipes_by_ingredients` - Ingredient-based search
- `mcp__terrarium__send_telegram_message` - Proactive messaging
- `mcp__tavily__tavily-search` - Web research
- `mcp__arxiv__search_papers` - Academic research

**Potential additions (not yet integrated):**
- Instacart API - Auto-order groceries
- Instagram scraping - Event discovery
- Fitness tracker API - Auto-log gym visits
- Budget tracking API - Auto-track spending

Want any of these? Let Canopy know!

## Pantry Tracking Recommendations

Since you asked about pantry tracking, here are options:

### Option 1: Manual (Current Setup)
- Update `pantry/current.md` after grocery delivery
- Update after meal prep (subtract used items)
- Canopy prompts when inventory is stale (>7 days)

**Pros:** Free, full control
**Cons:** Manual effort

### Option 2: Photo-Based Inventory
- Take photo of fridge/pantry
- Canopy uses vision API to extract items
- Updates `pantry/current.md` automatically

**Pros:** Fast updates
**Cons:** Requires vision integration (not built yet)

### Option 3: Smart Fridge Integration
- If you have a smart fridge (Samsung Family Hub, LG ThinQ)
- Integrate API to auto-track inventory
- Canopy syncs with real-time data

**Pros:** Fully automated
**Cons:** Requires smart fridge

### Option 4: Barcode Scanning App
- Use app like "Grocy" or "Out of Milk"
- Scan barcodes when adding/removing items
- Canopy pulls data from app API

**Pros:** Accurate tracking
**Cons:** Requires app setup

**Recommendation:** Start with Option 1 (manual). After 2 weeks, if it's tedious, we can explore Option 2 (photo-based) or Option 4 (barcode app).

## Next Steps

1. ✅ Fill out `pantry/preferences.md` (your food goals)
2. ✅ Fill out `goals/strategic.md` (your 6-12 month goals)
3. ✅ Take initial pantry inventory in `pantry/current.md`
4. ✅ Establish baseline patterns in `patterns/2026-04.md`
5. ✅ Test proactive messaging (send "@canopy" a message)
6. ✅ Wait for first heartbeat proactive alerts (within 30 minutes)

## Monitoring Canopy's Proactivity

**Check what Canopy is doing:**

```bash
# View recent heartbeat runs
openclaw cron runs --id <canopy-heartbeat-id> --limit 10

# View Canopy's session state
cat /media/starscream/bumblebee1/blaze/terrarium/src/landscapes/canopy/SESSION-STATE.md

# View learned patterns
cat /media/starscream/bumblebee1/blaze/terrarium/src/landscapes/canopy/patterns/2026-04.md
```

**Telegram will show:**
- Proactive alerts (low pantry, meal prep reminders, event discoveries)
- Strategic insights (goal progress, pattern deviations)
- Meta analysis (monthly reviews, quarterly pivots)

---

**You're all set!** Canopy is now fully proactive. Complete the 4 setup files above and watch it start anticipating your needs.

Questions? Ask Canopy anything:
```
@canopy How do I [task]?
@canopy What patterns have you noticed?
@canopy Suggest optimizations for my weekly routine
```

Welcome to the future of proactive AI assistance. 🚀
