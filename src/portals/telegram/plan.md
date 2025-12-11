# Delightful Telegram Bot Experience - Implementation Plan

## 🎯 **Vision**
Transform the Terrarium Telegram bot from a text-command interface into an interactive, visual, delightful experience that makes AI personas feel alive and accessible.

---

## ⭐ **PRIORITY 1: First-Time User Experience**

### Goals
- Create magical first impression
- Guide users naturally to their ideal bot
- Establish interaction patterns immediately
- Build confidence and curiosity

### Implementation Tasks

#### Task 1.1: Interactive Welcome Flow
**File:** `src/portals/telegram/bot.py` - Enhance `start()` function

**Current:**
```
Welcome message → plain text with commands
```

**New:**
```
Welcome message → Interactive quiz → Bot recommendation → Connect
```

**Components:**
1. Welcome message with visual appeal (emoji, formatting)
2. Interest selection via inline keyboard
3. Bot recommendation based on selection
4. One-tap connection to recommended bot
5. Quick tips overlay after first message

**Inline Keyboard Structure:**
```python
InlineKeyboardMarkup([
    [InlineKeyboardButton("🎨 Creative Work", callback_data="interest_creative")],
    [InlineKeyboardButton("📅 Planning & Organization", callback_data="interest_planning")],
    [InlineKeyboardButton("💪 Health & Fitness", callback_data="interest_health")],
    [InlineKeyboardButton("🍳 Cooking & Recipes", callback_data="interest_cooking")],
    [InlineKeyboardButton("🚀 Tech & Future", callback_data="interest_tech")],
    [InlineKeyboardButton("📚 Learning & Strategy", callback_data="interest_learning")],
])
```

**Bot Recommendation Mapping:**
- Creative Work → Anya
- Planning & Organization → Cassia
- Health & Fitness → Freya
- Cooking & Recipes → Nigella
- Tech & Future → Nyx
- Learning & Strategy → Sage

#### Task 1.2: Visual Bot Introduction
After recommendation, show bot card:

```
╔════════════════════════════╗
║  🎨 ANYA                   ║
║  Creative Director         ║
║────────────────────────────║
║  I help with art, music,   ║
║  design, and creative      ║
║  expression.               ║
║                            ║
║  [✨ Connect] [🌿 See All]  ║
╚════════════════════════════╝
```

#### Task 1.3: First Message Tips
After first bot response, show persistent menu:

```
💡 Tip: Use these quick actions anytime!

[🔄 Ask More] [🎭 Switch Bot] [📊 Stats] [🧹 Clear]
```

#### Task 1.4: Callback Query Handler
**New Handler:** `CallbackQueryHandler` for all button interactions

**Callbacks to implement:**
- `interest_*` → Show bot recommendation
- `connect_*` → Connect to specific bot
- `action_switch` → Show bot selection menu
- `action_stats` → Show status dashboard
- `action_clear` → Clear conversation
- `action_help` → Context-sensitive help

---

## 🎨 **Phase 1: Core Interactive Elements**

### Task 1.5: Visual Bot Selection Gallery
**Command:** `/bots` enhancement

**Current:** Plain text list
**New:** Interactive card grid

```python
def create_bot_card(bot_name: str, emoji: str, description: str, stats: dict) -> str:
    """Create formatted bot card with stats"""
    card = f"""
╔════════════════════════════╗
║  {emoji} {bot_name.upper():<24}║
║  {description[:26]:<26}║
║────────────────────────────║
"""
    if stats['message_count'] > 0:
        card += f"║  Last: {stats['last_active']:<20}║\n"
        card += f"║  Messages: {stats['message_count']:<16}║\n"

    card += "╚════════════════════════════╝"
    return card
```

**Inline keyboard per card:**
```python
[
    InlineKeyboardButton("✨ Connect", callback_data=f"connect_{bot_name}"),
    InlineKeyboardButton("👁️ Preview", callback_data=f"preview_{bot_name}")
]
```

#### Task 1.6: Persistent Context Menu
Add context-sensitive buttons to every bot response

**Base menu:**
```python
def get_context_menu(bot_name: str = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Ask More", callback_data="action_continue"),
            InlineKeyboardButton("🎭 Switch Bot", callback_data="action_switch")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="action_stats"),
            InlineKeyboardButton("🧹 Clear", callback_data="action_clear")
        ]
    ])
```

**Bot-specific additions:**
```python
def get_bot_specific_actions(bot_name: str) -> List[List[InlineKeyboardButton]]:
    bot_actions = {
        "anya": [
            [InlineKeyboardButton("🎵 Add to Queue", callback_data="anya_queue")],
            [InlineKeyboardButton("🖼️ Generate Art", callback_data="anya_art")]
        ],
        "nigella": [
            [InlineKeyboardButton("📖 Full Recipe", callback_data="nigella_recipe")],
            [InlineKeyboardButton("🍷 Wine Pairing", callback_data="nigella_wine")]
        ],
        "cassia": [
            [InlineKeyboardButton("📅 Add Event", callback_data="cassia_event")],
            [InlineKeyboardButton("⏰ Reminder", callback_data="cassia_reminder")]
        ]
    }
    return bot_actions.get(bot_name, [])
```

#### Task 1.7: Enhanced Status Dashboard
**Command:** `/status` enhancement

Transform from plain text to visual dashboard with progress bars and inline actions.

```python
def create_status_dashboard(user_id: int, current_bot: str) -> tuple[str, InlineKeyboardMarkup]:
    """Create visual status dashboard with stats"""
    # Get stats from session_manager
    # Create formatted message with:
    # - Current bot with progress bar
    # - Activity breakdown with mini bars
    # - Cost tracking
    # - Time active

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 View All Chats", callback_data="status_history")],
        [InlineKeyboardButton("💾 Export History", callback_data="status_export")]
    ])

    return (dashboard_message, keyboard)
```

---

## 🎯 **Phase 2: Intelligence & Personalization**

### Task 2.1: Recommendation Engine
**File:** `src/portals/telegram/recommender.py` (new)

```python
class BotRecommender:
    """Intelligent bot recommendation based on usage patterns and context"""

    def should_show_recommendation(self, user_id: int, current_bot: str) -> bool:
        """Determine if recommendation should be shown"""
        # Rules:
        # - After 5 messages with same bot
        # - After 30 minutes in same conversation
        # - Time-based (morning → Cassia, evening → Anya)
        # - Keyword detection in messages
        pass

    def get_recommendation(self, context: dict) -> dict:
        """Get bot recommendation with reason"""
        # Returns: {
        #   "bot": "sage",
        #   "reason": "Want a strategic perspective?",
        #   "confidence": 0.8
        # }
        pass
```

#### Task 2.2: Proactive Messaging
Enable bots to initiate conversations via scheduled tasks

**File:** `src/portals/telegram/scheduler.py` (new)

```python
class BotScheduler:
    """Schedule proactive bot messages"""

    async def send_morning_greeting(self, user_id: int):
        """Cassia sends morning plan offer"""
        pass

    async def send_reminder(self, user_id: int, bot: str, message: str):
        """Bot sends scheduled reminder"""
        pass
```

#### Task 2.3: Conversation History Browser
**Command:** `/history`

Show searchable, resumable conversation list

```python
def create_history_browser(user_id: int, page: int = 0) -> tuple[str, InlineKeyboardMarkup]:
    """Create paginated history view"""
    # Load conversations from session_manager
    # Create message with summaries
    # Add inline keyboard with [Resume] [Preview] buttons
    # Add pagination [◀️ Prev] [Next ▶️]
    pass
```

---

## 🚀 **Phase 3: Rich Experiences**

### Task 3.1: Web App Integration
Launch mini web apps for complex interactions

**Cassia's Calendar:**
```python
@app.route('/webapp/calendar')
def calendar_webapp():
    """Full calendar view with event management"""
    # HTML/JS interface using Telegram Web Apps API
    pass
```

**Anya's Gallery:**
```python
@app.route('/webapp/gallery')
def gallery_webapp():
    """Image gallery with editing capabilities"""
    pass
```

**Launch buttons:**
```python
InlineKeyboardButton(
    "📅 Open Calendar",
    web_app=WebAppInfo(url="https://your-domain/webapp/calendar")
)
```

### Task 3.2: Inline Query Support
Use bot from any Telegram chat

```python
async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle @terrarium_bot queries from any chat"""
    query = update.inline_query.query

    # Parse: @terrarium_bot anya create a dark forest scene
    # Return: Inline results with bot responses
    pass
```

### Task 3.3: Rich Media Support
- Voice messages (transcribe → bot response)
- Image analysis (send photo → relevant bot analyzes)
- File exports (PDFs, images, recipe cards)

---

## 🎨 **Design System**

### Color Coding by Bot
- 🎨 **Anya:** Purple gradients (`#9D4EDD`)
- 📅 **Cassia:** Warm orange (`#FF9E00`)
- 💪 **Freya:** Energetic red (`#EF476F`)
- 🍳 **Nigella:** Rich browns (`#8B4513`)
- 🚀 **Nyx:** Electric blue (`#00B4D8`)
- 📚 **Sage:** Deep green (`#2D6A4F`)
- 🪴 **Casper:** Teal/cyan (`#48BFE3`)

### Button Design Patterns
- **Primary actions:** `[✨ Action]` - Main user intent
- **Secondary:** `[📖 Info]` - Additional information
- **Destructive:** `[🗑️ Delete]` - Irreversible actions
- **Navigation:** `[← Back] [Next →]` - Movement between views

### Typography Guidelines
- **Bold** for bot names and key actions
- *Italic* for metadata (timestamps, counts)
- `Monospace` for technical info
- Emoji as visual anchors (one per major element)

### Message Structure
```
[Emoji] [Title in Bold]
[Separator line or blank line]
[Body text with mixed formatting]
[Blank line]
[Inline keyboard for actions]
```

---

## 📊 **Technical Architecture**

### New Files to Create
```
src/portals/telegram/
├── bot.py (modify - add callback handlers)
├── claude_engine.py (existing)
├── session_manager.py (existing)
├── keyboards.py (new - all keyboard layouts)
├── formatters.py (new - message formatting)
├── recommender.py (new - bot recommendations)
├── scheduler.py (new - proactive messaging)
├── callbacks.py (new - callback query handlers)
└── webapp/ (new directory)
    ├── __init__.py
    ├── server.py (Flask/FastAPI)
    ├── templates/
    └── static/
```

### Handler Structure
```python
# In bot.py
from telegram.ext import CallbackQueryHandler

# Add to application
application.add_handler(CallbackQueryHandler(handle_callbacks))

# Callback router
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge

    data = query.data

    if data.startswith("interest_"):
        await handle_interest_selection(update, context)
    elif data.startswith("connect_"):
        await handle_bot_connection(update, context)
    elif data.startswith("action_"):
        await handle_action_button(update, context)
    # ... etc
```

### State Management
Extend session_manager to track:
- Current onboarding step
- Last recommendation shown
- Button interaction history
- User preferences

---

## 🎯 **Success Metrics**

### Engagement
- Average session length
- Messages per session
- Button click-through rates

### Discoverability
- % of users who complete onboarding
- % of users who try 3+ bots
- Average time to first bot switch

### Retention
- Daily active users
- Return rate after 7 days
- Bot switching frequency

### Satisfaction
- Recommendation acceptance rate
- Feature usage (stats, history, etc.)
- Error rate / support requests

---

## 🚀 **Implementation Order**

### Sprint 1: First-Time User Experience (PRIORITY)
- [ ] Task 1.1: Interactive welcome flow
- [ ] Task 1.2: Visual bot introduction
- [ ] Task 1.3: First message tips
- [ ] Task 1.4: Callback query handler foundation

### Sprint 2: Core Interactivity
- [ ] Task 1.5: Visual bot selection gallery
- [ ] Task 1.6: Persistent context menu
- [ ] Task 1.7: Enhanced status dashboard

### Sprint 3: Intelligence
- [ ] Task 2.1: Recommendation engine
- [ ] Task 2.2: Proactive messaging
- [ ] Task 2.3: Conversation history browser

### Sprint 4: Rich Experiences
- [ ] Task 3.1: Web app integration
- [ ] Task 3.2: Inline query support
- [ ] Task 3.3: Rich media support

---

## 📝 **Development Notes**

### Testing Strategy
1. **Unit tests** for formatters, recommenders
2. **Integration tests** for callback flows
3. **User testing** with 3-5 people for onboarding
4. **A/B testing** for recommendation effectiveness

### Deployment Considerations
- Backward compatibility (existing users shouldn't break)
- Gradual rollout (onboarding for new users only at first)
- Feature flags for experimental features
- Monitoring button clicks and flow completion

### Dependencies
```
python-telegram-bot>=20.0 (already installed)
Flask or FastAPI (for web apps)
APScheduler (for proactive messages)
```

---

## 💡 **Future Ideas**

### Advanced Features
- Voice message transcription → bot response
- Group chat mode (multiple users, one bot)
- Bot personalities evolve based on interactions
- Cross-bot memory (bots remember context from other bots)
- Achievement system (gamification)
- Custom bot creation (users configure their own)

### Integration Opportunities
- ComfyUI workflow builder in Web App
- Calendar sync with Google Calendar via MCP
- Spotify playlist collaboration (shared with friends)
- Export conversations as beautiful PDFs
- Share bot responses to social media

---

## 📚 **Resources**

### Documentation
- [Telegram Bot API - Keyboards](https://core.telegram.org/bots/api#inlinekeyboardmarkup)
- [python-telegram-bot - CallbackQuery](https://docs.python-telegram-bot.org/)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)

### Design Inspiration
- Notion's onboarding flow
- Discord's bot interactions
- Spotify's music recommendations
- Apple's UI design guidelines

---

**Last Updated:** 2025-11-15
**Status:** Planning Phase
**Priority:** First-Time User Experience (Sprint 1)
