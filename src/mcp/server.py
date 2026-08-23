import os
import sys
from pathlib import Path

# MCP clients launch this file by path (`python src/mcp/server.py`), which puts
# src/mcp/ on sys.path instead of the project root, so the `src.` imports below
# cannot resolve. Put the project root on sys.path before importing them.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import click  # noqa: E402
import httpx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from fastmcp import FastMCP  # noqa: E402
from recipe_scrapers import SCRAPERS, scrape_me  # noqa: E402
from runware import IImageInference, IPromptEnhance, Runware  # noqa: E402
from runware.types import ILora  # noqa: E402
from telegram import Bot  # noqa: E402

from src.engine import memory_store  # noqa: E402

load_dotenv()

RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DANIELLE_TELEGRAM_CHAT_ID = os.getenv("DANIELLE_TELEGRAM_CHAT_ID")

# Persona emojis for Terrarium characters
PERSONA_EMOJIS = {
    "anya": "🎨",  # Creative director & artistic guide
    "cassia": "☀️",  # Daily planner & morning briefings
    "freya": "💪",  # Health, fitness & nutrition
    "nigella": "🍷",  # Culinary guide & sommelier
    "nyx": "🚀",  # Accelerationist & futurist
    "sage": "📚",  # Strategic visionary & wisdom guide
    "system": "🌿",  # System notifications
    "default": "🤖",  # Fallback
}

dimensions = {
    "portrait": "512x768",
    "landscape": "1344x768",  # Proper 16:9 landscape ratio
    "square": "640x640",
}

# Google Nano Banana 2 supported dimensions
google_dimensions = {
    "portrait": "1264x1696",
    "landscape": "2528x1696",  # 3:2 aspect ratio
    "square": "1024x1024",
}

mcp = FastMCP(
    "Terrarium Utilities",
    instructions="A collection of utilities for image generation, messaging, and automation.",
)


@mcp.tool()
async def generate_image(
    prompt: str,
    model_id: str = "runware:101@1",
    n_results: int = 1,
    orientation: str = "portrait",
    enhance: bool = False,
    add_lora: bool = False,
    reference_images: list[str] | None = None,
) -> list[str]:
    """Create artwork using AI image generation

    Args:
        prompt: Text description of the image to generate
        model_id: Model to use (e.g., "runware:101@1" or "google:4@3" for Nano Banana 2)
        n_results: Number of images to generate
        orientation: Image orientation (portrait, landscape, square)
        enhance: Whether to enhance the prompt
        add_lora: Whether to add LoRA models
        reference_images: Optional list of image URLs to use as references (for composition/style transfer)
    """
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    # Use google dimensions for google models, standard dimensions otherwise
    dimension_map = google_dimensions if model_id.startswith("google:") else dimensions
    width, height = map(int, dimension_map[orientation].split("x"))
    click.secho(f"Prompt: {prompt}", fg="green")

    if reference_images:
        click.secho(f"Using {len(reference_images)} reference images", fg="cyan")

    if enhance:
        prompt_enhancer = IPromptEnhance(
            prompt=prompt[:300],
            promptVersions=1,
            promptMaxLength=300,
        )
        prompt = await runware.promptEnhance(promptEnhancer=prompt_enhancer)
        prompt = prompt[0].text
        click.secho(f"Enhanced Prompt: {prompt}", fg="green")

    if add_lora:
        lora = [
            ILora(model="civitai:340248@755549", weight=0.2),
            ILora(model="civitai:308147@880134", weight=0.2),
        ]
    else:
        lora = None

    # Build request parameters
    request_params = {
        "positivePrompt": prompt,
        "model": model_id,
        "numberResults": n_results,
        "height": height,
        "width": width,
    }

    # Add optional parameters
    if lora:
        request_params["lora"] = lora

    # Add reference images if provided (for multi-image composition)
    if reference_images:
        request_params["referenceImages"] = reference_images

    request_image = IImageInference(**request_params)

    images = await runware.imageInference(requestImage=request_image)
    return images


@mcp.tool()
async def send_telegram_message(
    message: str,
    persona: str = None,
    chat_id: str = None,
) -> str:
    """Send a message to Telegram via the Casper bot

    Args:
        message: The message text to send
        persona: Optional persona name (anya, cassia, freya, nigella, nyx, sage, system)
        chat_id: Optional chat ID to send to. Defaults to TELEGRAM_CHAT_ID from environment
    """
    if not TELEGRAM_TOKEN:
        return "Error: TELEGRAM_TOKEN not found in environment"

    bot = Bot(token=TELEGRAM_TOKEN)

    # Resolve chat_id placeholders
    if chat_id == "DANIELLE_TELEGRAM_CHAT_ID":
        target_chat_id = DANIELLE_TELEGRAM_CHAT_ID
    else:
        target_chat_id = chat_id or TELEGRAM_CHAT_ID

    if not target_chat_id:
        return "Error: No chat_id provided and TELEGRAM_CHAT_ID not set in environment"

    # Format message with persona emoji if provided
    if persona:
        emoji = PERSONA_EMOJIS.get(persona.lower(), PERSONA_EMOJIS["default"])
        formatted_message = f"{emoji} *{persona.title()}*\n{message}"
        parse_mode = "Markdown"
    else:
        formatted_message = message
        parse_mode = None

    try:
        await bot.send_message(
            chat_id=target_chat_id, text=formatted_message, parse_mode=parse_mode
        )
        return f"Message sent successfully to chat {target_chat_id}"
    except Exception as e:
        return f"Error sending message: {str(e)}"


@mcp.tool()
async def send_telegram_document(
    file_path: str,
    caption: str = None,
    persona: str = None,
    chat_id: str = None,
) -> str:
    """Send a document/file to Telegram via the Casper bot

    Args:
        file_path: Path to the file to send (e.g., markdown, PDF, text files)
        caption: Optional caption/description for the document
        persona: Optional persona name (anya, cassia, freya, nigella, nyx, sage, system)
        chat_id: Optional chat ID to send to. Defaults to your personal chat
    """
    if not TELEGRAM_TOKEN:
        return "Error: TELEGRAM_TOKEN not found in environment"

    bot = Bot(token=TELEGRAM_TOKEN)

    # Use provided chat_id or fall back to default
    target_chat_id = chat_id or TELEGRAM_CHAT_ID

    if not target_chat_id:
        return "Error: No chat_id provided and TELEGRAM_CHAT_ID not set in environment"

    # Expand home directory if needed
    from pathlib import Path

    file_path = str(Path(file_path).expanduser())

    # Check if file exists
    if not Path(file_path).exists():
        return f"Error: File not found at {file_path}"

    # Format caption with persona emoji if provided
    if persona and caption:
        emoji = PERSONA_EMOJIS.get(persona.lower(), PERSONA_EMOJIS["default"])
        formatted_caption = f"{emoji} *{persona.title()}*\n{caption}"
        parse_mode = "Markdown"
    elif caption:
        formatted_caption = caption
        parse_mode = "Markdown"
    else:
        formatted_caption = None
        parse_mode = None

    try:
        with open(file_path, "rb") as doc:
            await bot.send_document(
                chat_id=target_chat_id,
                document=doc,
                caption=formatted_caption,
                parse_mode=parse_mode,
            )
        return f"Document sent successfully to chat {target_chat_id}"
    except Exception as e:
        return f"Error sending document: {str(e)}"


@mcp.tool()
async def scrape_recipe(url: str) -> dict:
    """Extract recipe data from a recipe URL

    Args:
        url: The URL of the recipe page (e.g., from NY Times, Food Network, AllRecipes, etc.)

    Returns:
        Dictionary containing recipe details: title, ingredients, instructions, time, servings, etc.
    """
    try:
        scraper = scrape_me(url, wild_mode=True)

        recipe_data = {
            "title": scraper.title(),
            "total_time": scraper.total_time(),
            "yields": scraper.yields(),
            "ingredients": scraper.ingredients(),
            "instructions": scraper.instructions(),
            "image": scraper.image(),
            "host": scraper.host(),
        }

        # Add optional fields if available
        try:
            recipe_data["nutrients"] = scraper.nutrients()
        except Exception:
            pass

        try:
            recipe_data["canonical_url"] = scraper.canonical_url()
        except Exception:
            pass

        return recipe_data
    except Exception as e:
        return {"error": f"Failed to scrape recipe: {str(e)}"}


@mcp.tool()
async def list_supported_recipe_sites() -> dict:
    """List all 100+ recipe websites supported by the scraper

    Returns:
        Dictionary with count and list of supported domains
    """
    supported_sites = sorted(SCRAPERS.keys())
    return {
        "count": len(supported_sites),
        "sites": supported_sites,
        "examples": [
            "allrecipes.com",
            "foodnetwork.com",
            "nytimes.com",
            "bonappetit.com",
            "seriouseats.com",
            "epicurious.com",
            "bbcgoodfood.com",
        ],
    }


# Stock Screener Integration

STOCK_SCREENER_URL = os.getenv("STOCK_SCREENER_URL", "http://localhost:5004")


@mcp.tool()
async def get_stock_recommendations(
    budget: int = 1000, method: str = "max_sharpe", threshold: float = 0.05
) -> dict:
    """
    Get optimized portfolio recommendations from watchlist.

    Args:
        budget: Investment amount in dollars (supports fractional shares)
        method: Optimization method - "max_sharpe" (risk-adjusted) or "hrp" (diversification)
        threshold: Minimum weight threshold (default 0.05 = 5%)

    Returns:
        Portfolio with weights, allocation, expected return, volatility, sharpe ratio,
        selected stocks, and stock sector/industry info
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{STOCK_SCREENER_URL}/recommend_stocks/",
                json={"budget": budget, "method": method, "threshold": threshold},
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {
            "error": "Stock screener API is not running. Start it with: cd $STOCK_SCREENER_PATH && source .venv/bin/activate && python app.py --port 5004"
        }
    except Exception as e:
        return {"error": f"Failed to get recommendations: {str(e)}"}


@mcp.tool()
async def check_sell_signals(holdings: list[dict] | None = None) -> dict:
    """
    Check current holdings for sell signals (stop-loss, technical breakdown, fundamentals).

    Args:
        holdings: Optional list of holdings with format:
                  [{"symbol": "AAPL", "entry_price": 150, "entry_date": "2024-01-01", "shares": 10}]
                  If omitted, reads from data/inputs/my_stocks.csv

    Returns:
        List of sell recommendations with signal reasons, current price, gain/loss,
        recommendation (SELL/HOLD), and priority (HIGH/MEDIUM/LOW)

    Signals detected:
        - Stop-loss: >12% drop from entry
        - Trailing stop: ATR-based (20-day high - 3×ATR)
        - Technical breakdown: Death cross + RSI<30 + MACD bearish
        - Fundamental issues: Earnings decline, low ROE, high debt
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"holdings": holdings} if holdings else {}
            response = await client.post(f"{STOCK_SCREENER_URL}/check_sells/", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {
            "error": "Stock screener API is not running. Start it with: cd $STOCK_SCREENER_PATH && source .venv/bin/activate && python app.py --port 5004"
        }
    except Exception as e:
        return {"error": f"Failed to check sell signals: {str(e)}"}


@mcp.tool()
async def get_watchlist() -> dict:
    """
    Get current stock watchlist symbols.

    Returns:
        Dictionary with "symbols" list of ticker symbols
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{STOCK_SCREENER_URL}/watchlist/")
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {
            "error": "Stock screener API is not running. Start it with: cd $STOCK_SCREENER_PATH && source .venv/bin/activate && python app.py --port 5004"
        }
    except Exception as e:
        return {"error": f"Failed to get watchlist: {str(e)}"}


# Memory Integration
#
# Profile facts (category="profile") are fetched by exact filter and are always
# complete; episodic memory is vector-searched. See src/engine/memory_store.py.


@mcp.tool()
async def get_profile(user_id: str = None) -> dict:
    """Get ALL profile facts for a person - identity, preferences, constraints.

    Use this instead of search_memory when you need to know who you're dealing with.
    Returns every profile fact by exact lookup, so nothing is left out. These facts
    are ground truth: they override anything you infer or remember sending before.

    Args:
        user_id: Person to look up - "lejin"/"me" or "danielle", or a raw chat ID.
                 Defaults to the main user.

    Returns:
        Dict with the person's id and the full list of profile facts
    """
    try:
        facts = memory_store.get_profile(user_id)
        return {
            "user_id": memory_store.resolve_user(user_id),
            "fact_count": len(facts),
            "facts": facts,
        }
    except Exception as e:
        return {"error": f"Profile lookup failed: {str(e)}"}


@mcp.tool()
async def search_memory(
    query: str,
    user_id: str = None,
    agent_id: str = None,
    category: str = "episodic",
    limit: int = 10,
) -> dict:
    """Search episodic memory for relevant past context

    For identity facts (what someone likes, does, needs) call get_profile instead -
    this is a similarity search and will not reliably surface every relevant fact.

    Args:
        query: Search query (topic, keyword, question)
        user_id: Person whose memory to search ("lejin", "danielle", or chat ID)
        agent_id: Optional filter to one agent's memories. These record what that
                  agent did, not facts about the person; use get_profile for those.
        category: "episodic" (default) or "profile", or None for both
        limit: Max results to return

    Returns:
        List of relevant memories with text, score, and metadata
    """
    try:
        results = memory_store.search(
            query=query,
            user_id=user_id,
            agent_id=agent_id,
            category=category,
            limit=limit,
        )
        return {"count": len(results), "results": results}
    except Exception as e:
        return {"error": f"Memory search failed: {str(e)}"}


@mcp.tool()
async def add_memory(
    content: str,
    user_id: str = None,
    agent_id: str = None,
    category: str = "episodic",
) -> dict:
    """Store a new memory, verbatim

    Stored exactly as you write it; identical text is skipped.

    Use category="episodic" (default) for what happened: discoveries, decisions,
    what you sent. Use category="profile" for a durable fact about the person that
    should shape every future message. Phrase profile facts positively - state what
    is true rather than contrasting it with what is not.

    Args:
        content: The memory content to store
        user_id: Person it belongs to ("lejin", "danielle", or chat ID)
        agent_id: Your bot name
        category: "episodic" (default) or "profile"

    Returns:
        Stored memory details
    """
    try:
        return memory_store.add_fact(
            data=content,
            user_id=user_id,
            agent_id=agent_id or "system",
            category=category,
        )
    except Exception as e:
        return {"error": f"Memory storage failed: {str(e)}"}


@mcp.tool()
async def send_agent_message(
    to_agent: str,
    content: str,
    from_agent: str,
    message_type: str = "note",
) -> dict:
    """Send a message to another terrarium agent

    Use this to delegate tasks, ask questions, leave notes, or reply to other agents.

    Args:
        to_agent: Recipient agent name (cassia, nyx, sage, freya, nigella, anya, pepper, casper)
        content: Your message content
        from_agent: Your agent name
        message_type: Type of message (delegation, question, note, reply, update)

    Returns:
        Confirmation of sent message

    Examples:
        - Delegation: send_agent_message("nigella", "User wants high-protein Italian dinner ideas", "cassia", "delegation")
        - Collaboration: send_agent_message("sage", "Found paper on quantum computing breakthroughs", "nyx", "note")
        - Question: send_agent_message("freya", "What's optimal protein intake for muscle gain?", "cassia", "question")
    """
    try:
        formatted_content = f"@{to_agent} FROM {from_agent} [{message_type}]: {content}"

        # Outbox copy (sender's context) and inbox copy (discoverable by recipient)
        memory_store.add_fact(data=formatted_content, agent_id=from_agent, category="episodic")
        memory_store.add_fact(data=formatted_content, agent_id=to_agent, category="episodic")

        return {
            "status": "sent",
            "to": to_agent,
            "from": from_agent,
            "type": message_type,
            "content": content,
        }
    except Exception as e:
        return {"error": f"Failed to send message: {str(e)}"}


@mcp.tool()
async def get_my_messages(
    agent_id: str,
    limit: int = 10,
    message_type: str = None,
) -> dict:
    """Check for messages sent to you by other agents

    Use this at startup to check your inbox for delegations, questions, or notes from other agents.

    Args:
        agent_id: Your agent name
        limit: Maximum messages to return (default 10)
        message_type: Optional filter by type (delegation, question, note, reply, update)

    Returns:
        Dictionary with message count and list of messages with content and metadata
    """
    try:
        query = f"@{agent_id} FROM"
        if message_type:
            query += f" [{message_type}]"

        messages = memory_store.search(
            query=query,
            agent_id=agent_id,
            category="episodic",
            limit=limit,
        )

        return {
            "agent": agent_id,
            "message_count": len(messages),
            "messages": messages,
        }
    except Exception as e:
        return {"error": f"Failed to get messages: {str(e)}"}


@mcp.resource("memory://profile/main")
async def get_user_profile() -> str:
    """Get the main user's full profile as a markdown block"""
    try:
        return memory_store.render_profile() or "No profile data found"
    except Exception as e:
        return f"Error loading profile: {str(e)}"


if __name__ == "__main__":
    mcp.run()
