import os

import asyncio
from fastmcp import FastMCP
import click
from runware import Runware, IImageInference, IPromptEnhance
from runware.types import ILora
from dotenv import load_dotenv
from telegram import Bot
from recipe_scrapers import scrape_me, SCRAPERS

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
) -> list[str]:
    """Create artwork using AI image generation"""
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()

    width, height = map(int, dimensions[orientation].split("x"))
    click.secho(f"Prompt: {prompt}", fg="green")

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
    request_image = IImageInference(
        positivePrompt=prompt,
        model=model_id,
        numberResults=n_results,
        height=height,
        width=width,
        lora=lora,
    )

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
        chat_id: Optional chat ID to send to. Defaults to your personal chat (902949428)
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
        except:
            pass

        try:
            recipe_data["canonical_url"] = scraper.canonical_url()
        except:
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
    supported_sites = sorted(list(SCRAPERS.keys()))
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
import httpx
from typing import Optional, List, Dict

STOCK_SCREENER_URL = os.getenv("STOCK_SCREENER_URL", "http://localhost:5004")


@mcp.tool()
async def get_stock_recommendations(
    budget: int = 1000,
    method: str = "max_sharpe",
    threshold: float = 0.05
) -> Dict:
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
                json={"budget": budget, "method": method, "threshold": threshold}
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {"error": "Stock screener API is not running. Start it with: cd /media/starscream/wheeljack1/projects/stock-screener && source .venv/bin/activate && python app.py --port 5004"}
    except Exception as e:
        return {"error": f"Failed to get recommendations: {str(e)}"}


@mcp.tool()
async def check_sell_signals(holdings: Optional[List[Dict]] = None) -> Dict:
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
            response = await client.post(
                f"{STOCK_SCREENER_URL}/check_sells/",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {"error": "Stock screener API is not running. Start it with: cd /media/starscream/wheeljack1/projects/stock-screener && source .venv/bin/activate && python app.py --port 5004"}
    except Exception as e:
        return {"error": f"Failed to check sell signals: {str(e)}"}


@mcp.tool()
async def get_watchlist() -> Dict:
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
        return {"error": "Stock screener API is not running. Start it with: cd /media/starscream/wheeljack1/projects/stock-screener && source .venv/bin/activate && python app.py --port 5004"}
    except Exception as e:
        return {"error": f"Failed to get watchlist: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
