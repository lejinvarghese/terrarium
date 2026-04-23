# HEARTBEAT-PROACTIVE.md - Full Proactive Monitoring

**Extends HEARTBEAT.md with comprehensive proactive behaviors across all life domains.**

This file defines proactive monitoring beyond calendar events: pantry, meal prep, events, fitness patterns, and strategic goal tracking.

## Integration with HEARTBEAT.md

**Heartbeat cadence:** Every 30 minutes (configured in OpenClaw cron)

**On each heartbeat run:**
1. Execute HEARTBEAT.md checks (calendar, pattern synthesis, memory maintenance)
2. Execute proactive checks below (pantry, meal prep, events, goals)
3. Surface only high-value insights (signal over noise)

## Proactive Checks by Category

### 1. Pantry & Grocery Monitoring

**Check frequency:** Daily (during morning heartbeat ~8am)

```javascript
// Read pantry state
const pantry = readFile("pantry/current.md")
const preferences = readFile("pantry/preferences.md")
const patterns = readFile("patterns/YYYY-MM.md")

// Low stock detection
const lowItems = parseLowStock(pantry)  // Items marked in "Needs Restocking"
if (lowItems.length > 0 && daysSinceLastOrder(patterns) >= 5) {
  // Only surface if it's been 5+ days since last order
  queueProactiveMessage(`[Canopy] Low on: ${lowItems.join(", ")}. Time to restock?`)
}

// Expiring soon detection
const expiringSoon = parseExpiringItems(pantry)  // Items expiring in < 3 days
if (expiringSoon.length > 0) {
  queueProactiveMessage(`[Canopy] Expiring soon: ${expiringSoon.join(", ")}. Use in next meal prep?`)
}
```

### 2. Meal Prep Preparation

**Check frequency:** Saturday evening (day before typical meal prep day)

```javascript
const dayOfWeek = getCurrentDayOfWeek()
const patterns = readFile("patterns/YYYY-MM.md")
const mealPrepDay = patterns.mealPrep.dayOfWeek || "Sunday"  // Default: Sunday

if (dayOfWeek === "Saturday" && mealPrepDay === "Sunday") {
  // Spawn grocery list builder
  sessions_spawn({
    task: `Build grocery list for tomorrow's meal prep:
    
           INPUTS:
           - pantry/current.md (current inventory)
           - pantry/preferences.md (dietary goals, likes/dislikes, budget)
           - patterns/YYYY-MM.md (past successful recipes)
           
           STEPS:
           1. Use mcp__spoonacular__search_recipes to find 3 recipes matching:
              - High protein (from preferences)
              - Meal prep friendly (batch cooking)
              - Within prep time constraints
              - Avoid dislikes (check preferences)
           2. Calculate ingredients needed for 7 servings each
           3. Cross-reference with pantry/current.md (subtract what's already there)
           4. Calculate total cost estimate
           5. Check if within weekly budget (from preferences)
           
           OUTPUT:
           Formatted grocery list with:
           - Items grouped by category (proteins, carbs, vegetables, staples)
           - Quantities needed
           - Estimated total cost
           - Recipe names and URLs
           
           If over budget, suggest substitutions or smaller portions.`,
    label: "Grocery-List-Saturday",
    model: "openai/gpt-5.1-codex"
  })
  
  // When subagent completes, send results via Telegram
  // Message: "[Canopy] Meal prep tomorrow. Grocery list ready: [recipes]. Total: $XX. Order now for delivery?"
}
```

### 3. Event Discovery & Monitoring

**Check frequency:** 2x daily (morning ~8am, evening ~8pm)

```javascript
// Read event sources from patterns
const patterns = readFile("patterns/YYYY-MM.md")
const eventSources = patterns.social.sources || []

// Default sources if not configured
const defaultSources = [
  { name: "Buddies in Bad Times", handle: "buddiesinbadtimes", platform: "Instagram" },
  // Add more as user provides them
]

const sources = eventSources.length > 0 ? eventSources : defaultSources

for (source of sources) {
  sessions_spawn({
    task: `Monitor ${source.name} (${source.handle}) for new events:
    
           SEARCH STRATEGY:
           - Instagram: Check recent posts for event announcements
           - Facebook: Check events page
           - Eventbrite: Search by organizer
           
           FILTER CRITERIA (from patterns and preferences):
           - Event type: dark/gothic/kink/electronic music/art
           - Date range: Next 30-60 days (3-7 day notice needed for prep)
           - Location: Toronto area
           - Price: < $50 typically
           
           EXTRACT:
           - Event name
           - Date and time
           - Venue and address
           - Ticket price
           - Dress code (if any)
           - Link to details
           
           MATCHING:
           Compare against past events attended (patterns/YYYY-MM.md)
           Flag only if strong match to user preferences
           
           OUTPUT:
           If match found, return structured event details.
           If no match, return empty (don't report "no events found").`,
    label: `Event-Monitor-${source.name}`,
    model: "anthropic/claude-haiku"  // Cheaper for monitoring
  })
}

// When subagent finds match, send via Telegram:
// "[Canopy] New event: LATEX // HADAL ZONE, Apr 11 @ Buddies. $40, latex dress code. Add to calendar?"
```

### 4. Fitness Pattern Tracking

**Check frequency:** Weekly (Sunday evening during heartbeat)

```javascript
const dayOfWeek = getCurrentDayOfWeek()

if (dayOfWeek === "Sunday") {
  const patterns = readFile("patterns/YYYY-MM.md")
  const goals = readFile("goals/strategic.md")
  
  // Gym visits this month
  const gymVisits = patterns.fitness.visits || 0
  const gymTarget = goals.fitness.targetPerMonth || 16  // 4x/week = 16/month
  const monthProgress = getCurrentDayOfMonth() / 30  // % through month
  
  // Expected visits by now
  const expectedVisits = gymTarget * monthProgress
  
  // Deviation check
  if (gymVisits < expectedVisits * 0.75) {
    // 25%+ behind target
    queueProactiveMessage(
      `[Canopy] Fitness check: ${gymVisits} gym visits this month (target: ${gymTarget}). ` +
      `You're behind pace. Need schedule reset?`
    )
  }
  
  // Also check for sudden drops week-over-week
  const lastWeekVisits = patterns.fitness.lastWeekVisits || 0
  if (lastWeekVisits === 0 && patterns.fitness.usualWeeklyVisits >= 3) {
    queueProactiveMessage(
      `[Canopy] No gym visits this week (usual: ${patterns.fitness.usualWeeklyVisits}x/week). ` +
      `Everything okay?`
    )
  }
}
```

### 5. Strategic Goal Review

**Check frequency:** Monthly (last Sunday of month during heartbeat)

```javascript
const dayOfMonth = getCurrentDayOfMonth()
const daysInMonth = getDaysInCurrentMonth()
const dayOfWeek = getCurrentDayOfWeek()

if (dayOfWeek === "Sunday" && dayOfMonth >= (daysInMonth - 7)) {
  // Last Sunday of the month
  sessions_spawn({
    task: `Monthly strategic goal review for ${getCurrentMonth()}:
    
           INPUTS:
           - goals/strategic.md (long-term goals)
           - patterns/YYYY-MM.md (this month's patterns)
           - patterns/YYYY-[last month].md (comparison)
           
           ANALYZE:
           1. Goal progress (on track? behind? ahead?)
           2. Pattern trends (improving? stable? declining?)
           3. Trajectory shifts (priorities changing?)
           4. Blockers identified (what's preventing progress?)
           5. Wins to celebrate (goals achieved, milestones hit)
           
           OUTPUT FORMAT:
           [Canopy] Monthly Review: ${month}
           
           ## Progress
           - Body recomp: X% to goal (on track / behind / ahead)
           - Event attendance: X events (target: Y)
           - [Other goals from strategic.md]
           
           ## Trends
           - Gym: [increasing/stable/declining]
           - Social: [increasing/stable/declining]
           - [Other patterns]
           
           ## Insights
           - [Key observation 1]
           - [Key observation 2]
           
           ## Recommended Adjustments
           - [Specific actionable suggestion 1]
           - [Specific actionable suggestion 2]
           
           Keep it concise (< 300 words). Focus on actionable insights.`,
    label: "Monthly-Goal-Review",
    model: "openai/gpt-5.1-codex"
  })
  
  // Send results via Telegram when complete
}
```

### 6. Budget Tracking

**Check frequency:** Weekly (Sunday evening)

```javascript
const dayOfWeek = getCurrentDayOfWeek()

if (dayOfWeek === "Sunday") {
  const patterns = readFile("patterns/YYYY-MM.md")
  const preferences = readFile("pantry/preferences.md")
  
  // Weekly grocery budget check
  const weeklyGroceryBudget = preferences.weeklyGroceryBudget || 50
  const thisWeekSpend = patterns.grocery.thisWeekSpend || 0
  
  if (thisWeekSpend > weeklyGroceryBudget * 1.15) {
    // 15%+ over budget
    queueProactiveMessage(
      `[Canopy] Budget alert: Groceries this week: $${thisWeekSpend} ` +
      `(target: $${weeklyGroceryBudget}, 15% over). Need cost optimization?`
    )
  }
  
  // Monthly rollup (first Sunday of month)
  const dayOfMonth = getCurrentDayOfMonth()
  if (dayOfMonth <= 7) {
    const monthlySpend = {
      groceries: patterns.grocery.monthTotal || 0,
      events: patterns.events.monthTotal || 0,
      diningOut: patterns.dining.monthTotal || 0
    }
    
    const total = monthlySpend.groceries + monthlySpend.events + monthlySpend.diningOut
    
    queueProactiveMessage(
      `[Canopy] ${getLastMonth()} spending summary:\n` +
      `- Groceries: $${monthlySpend.groceries}\n` +
      `- Events: $${monthlySpend.events}\n` +
      `- Dining out: $${monthlySpend.diningOut}\n` +
      `Total: $${total}`
    )
  }
}
```

### 7. Academic Research Monitoring (arXiv)

**Check frequency:** Weekly (Sunday evening, after budget tracking)

```javascript
const dayOfWeek = getCurrentDayOfWeek()

if (dayOfWeek === "Sunday") {
  const goals = readFile("goals/strategic.md")
  const researchInterests = goals.intellectualPursuits.researchInterests || [
    "adaptive intelligent systems",
    "optimization algorithms", 
    "network science",
    "psychology",
    "complexity science"
  ]
  
  // Spawn arXiv monitoring subagent
  sessions_spawn({
    task: `Weekly arXiv digest for research interests:
    
           INTERESTS: ${researchInterests.join(", ")}
           
           SEARCH STRATEGY:
           Use mcp__arxiv__search_papers for each domain:
           - cs.AI (Artificial Intelligence)
           - cs.NE (Neural and Evolutionary Computing)
           - cs.SI (Social and Information Networks)
           - q-bio.NC (Neurons and Cognition)
           - nlin.AO (Adaptation and Self-Organizing Systems)
           
           FILTER:
           - Papers from last 7 days
           - Relevance to user interests (adaptive systems, optimization, networks, complexity)
           - Prefer: high citation potential, novel approaches, bridging paradigms
           
           STEPS:
           1. Search each category for relevant papers
           2. Extract: title, authors, abstract, arXiv ID, publication date
           3. Rank by relevance to user interests
           4. Select top 3-5 papers
           5. For each, write 2-3 sentence summary highlighting key contribution
           
           OUTPUT FORMAT:
           [Canopy] Weekly arXiv Digest
           
           📚 Top papers this week (${getCurrentWeek()}):
           
           1. **[Title]** (arXiv:XXXX.XXXXX)
              Authors, Date
              Summary: [2-3 sentences on key contribution]
              Why relevant: [Connection to your interests]
           
           [Repeat for 3-5 papers]
           
           💡 Theme of the week: [If patterns emerge across papers]
           
           Keep concise (<400 words total).`,
    label: "Weekly-arXiv-Digest",
    model: "openai/gpt-5-mini"  // Cost-effective for paper scanning
  })
  
  // When subagent completes, send via Telegram
}
```

### 8. Reading Progress Tracking

**Check frequency:** Weekly (Sunday evening)

```javascript
const dayOfWeek = getCurrentDayOfWeek()

if (dayOfWeek === "Sunday") {
  const patterns = readFile("patterns/YYYY-MM.md")
  const goals = readFile("goals/strategic.md")
  
  // Books in progress from goals
  const booksInProgress = goals.intellectualPursuits.booksInProgress || []
  const readingTarget = goals.intellectualPursuits.readingTarget || {}
  
  // Check reading progress patterns
  const booksCompleted = patterns.reading.booksCompleted || 0
  const papersRead = patterns.reading.papersRead || 0
  
  const monthProgress = getCurrentDayOfMonth() / 30
  const expectedBooks = (readingTarget.booksPerMonth || 1) * monthProgress
  const expectedPapers = (readingTarget.papersPerMonth || 4) * monthProgress
  
  // Reading behind pace?
  if (booksCompleted < expectedBooks * 0.5) {
    queueProactiveMessage(
      `[Canopy] Reading check: ${booksCompleted} books this month ` +
      `(target: ${readingTarget.booksPerMonth}). Behind pace. ` +
      `Books in progress: ${booksInProgress.map(b => b.title).join(", ")}. ` +
      `Schedule reading time?`
    )
  }
  
  // Papers behind pace?
  if (papersRead < expectedPapers * 0.5) {
    queueProactiveMessage(
      `[Canopy] Paper reading: ${papersRead} papers this month ` +
      `(target: ${readingTarget.papersPerMonth}). Check arXiv digest for suggestions.`
    )
  }
  
  // Suggest reading if free time detected
  const calendar = checkCalendar("tomorrow")
  const freeBlocks = calendar.filter(e => e.type === "free" && e.duration >= 60)
  
  if (freeBlocks.length > 0 && booksCompleted < expectedBooks) {
    queueProactiveMessage(
      `[Canopy] Free time tomorrow: ${freeBlocks[0].time} (${freeBlocks[0].duration}min). ` +
      `Good for reading "${booksInProgress[0].title}"?`
    )
  }
}
```

### 9. Concentration & Focus Tracking

**Check frequency:** Daily (evening ~8pm)

```javascript
const hourOfDay = getCurrentHour()

if (hourOfDay === 20) {  // 8pm
  const patterns = readFile("patterns/YYYY-MM.md")
  const goals = readFile("goals/strategic.md")
  
  // Focus hours target from goals (2025 goal: improve concentration)
  const focusTarget = goals.intellectualPursuits.focusHours || {}
  const todayFocusHours = patterns.focus.todayHours || 0
  const targetHours = focusTarget.hoursPerDay || 4
  
  // Check if met focus goal today
  if (todayFocusHours < targetHours * 0.75) {
    // Missed 25%+ of target
    queueProactiveMessage(
      `[Canopy] Focus check: ${todayFocusHours}h deep work today ` +
      `(target: ${targetHours}h). Tomorrow: block distractions?`
    )
  }
  
  // Weekly rollup (Sunday evening)
  const dayOfWeek = getCurrentDayOfWeek()
  if (dayOfWeek === "Sunday") {
    const weekFocusHours = patterns.focus.thisWeekHours || 0
    const weekTarget = targetHours * 5  // Weekdays only
    
    if (weekFocusHours >= weekTarget) {
      queueProactiveMessage(
        `[Canopy] 🎯 Focus win: ${weekFocusHours}h deep work this week ` +
        `(target: ${weekTarget}h). Concentration improving!`
      )
    }
  }
}
```

### 10. Free Time Activity Suggestions

**Check frequency:** When free blocks detected in calendar

```javascript
// During calendar checks, identify free time blocks
const calendar = checkCalendar("next 24 hours")
const freeBlocks = calendar.filter(e => e.type === "free" && e.duration >= 60)

for (block of freeBlocks) {
  // User doesn't like empty unstructured time (from TERRARIUM_MEMORY.md)
  // Suggest options and possibilities
  
  const goals = readFile("goals/strategic.md")
  const patterns = readFile("patterns/YYYY-MM.md")
  
  // Build suggestion based on pending activities and goals
  const suggestions = []
  
  // Reading behind?
  if (patterns.reading.behindTarget) {
    suggestions.push(`Read "${goals.intellectualPursuits.booksInProgress[0].title}" (${block.duration}min = ~30 pages)`)
  }
  
  // Gym visits low?
  if (patterns.fitness.behindTarget) {
    suggestions.push(`Gym session (${block.duration}min)`)
  }
  
  // No meal prep this week?
  if (!patterns.mealPrep.doneThisWeek) {
    suggestions.push(`Cook new recipe (experiment with seasonal ingredients)`)
  }
  
  // Weekend exploration?
  if (isWeekend() && block.duration >= 120) {
    suggestions.push(`Explore Queen West/Roncesvalles (walk/streetcar)`)
    suggestions.push(`Visit local food spot or nature area`)
  }
  
  // Creative projects?
  if (patterns.projects.behindSchedule) {
    suggestions.push(`Work on Terrarium development`)
  }
  
  // Plants need attention?
  if (patterns.plants.needsCare) {
    suggestions.push(`Tend to plants`)
  }
  
  // Only suggest if there are good options
  if (suggestions.length >= 3) {
    queueProactiveMessage(
      `[Canopy] Free time ${block.date} ${block.time} (${block.duration}min). ` +
      `Options:\n` +
      suggestions.slice(0, 4).map((s, i) => `${i+1}. ${s}`).join("\n")
    )
  }
}
```

### 11. Learning Project Progress

**Check frequency:** Weekly (Sunday evening)

```javascript
const dayOfWeek = getCurrentDayOfWeek()

if (dayOfWeek === "Sunday") {
  const goals = readFile("goals/strategic.md")
  const patterns = readFile("patterns/YYYY-MM.md")
  
  // 2025 goal: Build more applications
  const projects = goals.intellectualPursuits.projects || []
  const completedMilestones = patterns.projects.milestonesCompleted || 0
  
  // Check each project for progress
  for (project of projects) {
    const lastUpdate = patterns.projects[project.name]?.lastUpdated
    const daysSinceUpdate = daysSince(lastUpdate)
    
    // No progress in 2+ weeks?
    if (daysSinceUpdate >= 14) {
      queueProactiveMessage(
        `[Canopy] Project "${project.name}": no updates in ${daysSinceUpdate} days. ` +
        `Still active? Need to reschedule or deprioritize?`
      )
    }
  }
  
  // Monthly project review
  const dayOfMonth = getCurrentDayOfMonth()
  if (dayOfMonth <= 7) {
    sessions_spawn({
      task: `Monthly learning project review:
      
             INPUTS:
             - goals/strategic.md (project goals)
             - patterns/YYYY-MM.md (this month's progress)
             
             ANALYZE:
             1. Terrarium ecosystem: What was built this month?
             2. Other projects: Progress toward milestones?
             3. Blockers identified: Technical, time, motivation?
             4. Learning achieved: New skills gained?
             
             OUTPUT:
             [Canopy] Monthly Project Review: ${getLastMonth()}
             
             ## Progress
             - Terrarium: [What was shipped]
             - [Other projects]
             
             ## Learnings
             - [Key technical insights]
             - [Skills developed]
             
             ## Blockers
             - [What's slowing progress]
             
             ## Recommendations
             - [Specific suggestions for next month]
             
             Keep concise (<300 words).`,
      label: "Monthly-Project-Review",
      model: "openai/gpt-5-mini"
    })
  }
}
```

## Message Queuing & Delivery

**Proactive messages are queued and sent via Telegram when high-value:**

```javascript
// Queue management (prevents spam)
const messageQueue = []

function queueProactiveMessage(message) {
  messageQueue.push({
    message,
    timestamp: Date.now(),
    priority: calculatePriority(message)
  })
}

// At end of heartbeat, send queued messages
function deliverQueuedMessages() {
  if (messageQueue.length === 0) {
    return "HEARTBEAT_OK"  // Nothing to surface
  }
  
  // Sort by priority (high to low)
  messageQueue.sort((a, b) => b.priority - a.priority)
  
  // Send top 3 messages max (prevent overwhelming user)
  const toSend = messageQueue.slice(0, 3)
  
  for (msg of toSend) {
    mcp__terrarium__send_telegram_message({
      message: msg.message,
      chat_id: "902949428"  // Default to primary user
    })
  }
  
  // Log what was sent
  return `[Canopy] Sent ${toSend.length} proactive updates`
}

// Priority calculation
function calculatePriority(message) {
  // High priority: time-sensitive (expiring food, event deadlines)
  if (message.includes("expiring") || message.includes("deadline")) {
    return 10
  }
  
  // Medium priority: actionable opportunities (grocery list ready, new event)
  if (message.includes("ready") || message.includes("new event")) {
    return 5
  }
  
  // Low priority: FYI updates (pattern observations, budget summaries)
  return 1
}
```

## Integration with SESSION-STATE.md

**Before every heartbeat run:**
1. Read `SESSION-STATE.md` for pending proactive actions
2. Execute checks above
3. Update `SESSION-STATE.md` with new pending actions
4. Queue proactive messages
5. Deliver via Telegram

**After every heartbeat run:**
1. Update `self-improving/heartbeat-state.md` with last run timestamp
2. Update `SESSION-STATE.md` with completed actions
3. Update `patterns/YYYY-MM.md` with new data points

## Examples of Proactive Messaging

**Good proactive messages (send these):**
- "[Canopy] Meal prep tomorrow. Grocery list ready: Thai Basil Chicken, Korean Beef Bowl, Teriyaki Salmon. Total: $47. Order now?"
- "[Canopy] New event: LATEX // HADAL ZONE, Apr 11 @ Buddies. $40, latex dress code. Add to calendar?"
- "[Canopy] Expiring soon: spinach, chicken breast. Use in tonight's meal?"
- "[Canopy] Gym visits down 30% this month (10 vs 16 target). Need schedule reset?"
- "[Canopy] Weekly arXiv Digest: 4 papers on adaptive systems & complexity science. Top pick: 'Emergent Intelligence in Multi-Agent Systems' (arXiv:2604.12345)"
- "[Canopy] Reading check: 0 books completed this month (target: 2). Free time tomorrow 7-9pm. Read 'Cryptonomicon'?"
- "[Canopy] Focus win: 22h deep work this week (target: 20h). Concentration improving!"
- "[Canopy] Free time tomorrow 2-4pm. Options: 1) Read GEB, 2) Gym session, 3) Explore Roncesvalles, 4) Work on Terrarium"
- "[Canopy] Project 'Terrarium': no updates in 16 days. Still active or reschedule?"

**Bad proactive messages (don't send these):**
- "[Canopy] Heartbeat OK" (no value, just noise)
- "[Canopy] Checked calendar, no events found" (no actionable info)
- "[Canopy] Monitoring Instagram..." (process updates, not results)
- "[Canopy] Everything looks good" (low signal)

**Key principle:** Only interrupt with **actionable insights** or **timely opportunities**.

---

**Activation:** This proactive system activates automatically when:
1. User completes `pantry/preferences.md` (enables meal planning)
2. User completes `goals/strategic.md` (enables goal tracking, academic monitoring, reading tracking)
3. User adds event sources to `patterns/YYYY-MM.md` (enables event monitoring)
4. User sets reading targets in `goals/strategic.md` (enables weekly arXiv digests, reading progress tracking)
5. User sets focus hours targets in `goals/strategic.md` (enables concentration tracking)

**Partial activation:** Even without full setup, Canopy will:
- Monitor arXiv based on interests in `goals/strategic.md` (weekly)
- Suggest free time activities based on calendar and preferences
- Track project progress for listed projects in `goals/strategic.md`

**Until then:** Canopy focuses on tactical calendar briefs and learning baseline patterns.
