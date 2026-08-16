import os

import click
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from recipe_scrapers import SCRAPERS, scrape_me
from runware import IImageInference, IPromptEnhance, Runware
from runware.types import ILora
from telegram import Bot

from src.engine.memory_config import USER_ID, get_memory

load_dotenv()

RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

    # Use provided chat_id or fall back to default
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


@mcp.tool()
async def search_memory(
    query: str,
    user_id: str = None,
    agent_id: str = None,
    limit: int = 10,
) -> dict:
    """Search memories for relevant context

    Args:
        query: Search query (topic, keyword, question)
        user_id: Optional user ID filter (defaults to main user)
        agent_id: Optional agent ID filter (your bot name)
        limit: Max results to return

    Returns:
        List of relevant memories with text, metadata, and scores
    """
    try:
        memory = get_memory()
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if agent_id:
            filters["agent_id"] = agent_id

        results = memory.search(
            query=query,
            filters=filters if filters else None,
            limit=limit,
        )
        return results
    except Exception as e:
        return {"error": f"Memory search failed: {str(e)}"}


@mcp.tool()
async def add_memory(
    content: str,
    user_id: str = None,
    agent_id: str = None,
    category: str = "conversation",
) -> dict:
    """Store new memory

    Args:
        content: The memory content to store
        user_id: User ID (defaults to main user)
        agent_id: Agent ID (your bot name)
        category: Memory type (conversation, discovery, preference, goal)

    Returns:
        Stored memory details
    """
    try:
        memory = get_memory()
        target_user = user_id or USER_ID

        result = memory.add(
            messages=[{"role": "assistant", "content": f"[{category}] {content}"}],
            user_id=target_user,
            agent_id=agent_id or "system",
        )
        return result
    except Exception as e:
        return {"error": f"Memory storage failed: {str(e)}"}


@mcp.resource("memory://profile/main")
async def get_user_profile() -> str:
    """Get user profile and preferences from memory

    Returns consolidated profile information for context
    """
    try:
        memory = get_memory()
        profile_queries = [
            "user preferences personality background",
            "health fitness nutrition goals",
            "work career schedule",
        ]

        all_memories = []
        for query in profile_queries:
            results = memory.search(
                query=query,
                filters={"user_id": USER_ID},
                limit=5,
            )
            all_memories.extend(results.get("results", [])[:3])

        if not all_memories:
            return "No profile data found"

        profile_text = "# User Profile\n\n"
        for mem in all_memories[:10]:
            profile_text += f"- {mem['memory']}\n"

        return profile_text
    except Exception as e:
        return f"Error loading profile: {str(e)}"


if __name__ == "__main__":
    mcp.run()
