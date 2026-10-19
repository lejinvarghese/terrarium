"""Letterboxd public profile scraper - uses Playwright for Cloudflare bypass.

Letterboxd's API is not public (request-only). This module scrapes
public profile data using Playwright headless browser to bypass Cloudflare.

ONLY WORKING METHODS INCLUDED - broken films/details methods removed.
"""

from typing import Any

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class LetterboxdScraper:
    """Scraper for public Letterboxd profiles using Playwright."""

    BASE_URL = "https://letterboxd.com"

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def _ensure_browser(self):
        """Ensure browser is initialized."""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            )

    async def close(self):
        """Close the browser and playwright."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _fetch_page(self, url: str) -> str:
        """Fetch page content using Playwright."""
        await self._ensure_browser()
        page = await self.context.new_page()
        try:
            # Navigate and wait for DOM to load (not networkidle - Cloudflare challenges don't settle)
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Wait for Cloudflare challenge to complete (if present)
            await page.wait_for_timeout(5000)
            # Wait for profile content to appear
            try:
                await page.wait_for_selector("h1.title-1", timeout=10000)
            except Exception:
                pass  # Profile might not have this element
            content = await page.content()
            return content
        finally:
            await page.close()

    def _extract_profile_stats(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extract profile statistics from soup."""
        stats = {}
        # Stats are in h4.profile-statistic elements
        stat_elems = soup.select("h4.profile-statistic a")
        for link in stat_elems:
            count_elem = link.select_one(".value")
            label_elem = link.select_one(".definition")
            if count_elem and label_elem:
                count_text = count_elem.get_text(strip=True).replace(",", "")
                label = label_elem.get_text(strip=True).lower()
                try:
                    stats[label] = str(int(count_text))
                except ValueError:
                    stats[label] = count_text
        return stats

    def _extract_favorite_films(self, soup: BeautifulSoup) -> list[str]:
        """Extract favorite films from soup."""
        favorites = []
        fav_section = soup.select(".poster-list.-p70 li")
        for fav in fav_section[:4]:
            img = fav.select_one("img")
            if img and img.get("alt"):
                favorites.append(img.get("alt"))
        return favorites

    def _extract_recent_activity(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extract recent film activity from soup."""
        recent_films = []
        # Activity is in span.activity-summary elements
        activity_items = soup.select("span.activity-summary")
        for activity in activity_items[:5]:
            # Film link in .target
            film_link = activity.select_one(".target")
            if film_link:
                title = film_link.get_text(strip=True)
                film_data = {"title": title}

                # Rating in .rating.-tiny
                rating_elem = activity.select_one(".rating.-tiny")
                if rating_elem:
                    # Count stars - each one is a full star
                    star_text = rating_elem.get_text(strip=True)
                    star_count = star_text.count("★")
                    film_data["rating"] = float(star_count)

                recent_films.append(film_data)
        return recent_films

    async def get_user_profile(self, username: str) -> dict[str, Any]:
        """Get basic profile info for a Letterboxd user.

        Args:
            username: Letterboxd username

        Returns:
            Dict with name, profile_url, stats, favorites, recent_activity
        """
        url = f"{self.BASE_URL}/{username}/"

        try:
            html = await self._fetch_page(url)
            soup = BeautifulSoup(html, "lxml")

            name_elem = soup.select_one("h1.title-1")
            name = name_elem.get_text(strip=True) if name_elem else username

            stats = self._extract_profile_stats(soup)
            favorites = self._extract_favorite_films(soup)
            recent_films = self._extract_recent_activity(soup)

            return {
                "name": name,
                "username": username,
                "profile_url": url,
                "stats": stats,
                "favorites": favorites,
                "recent_activity": recent_films,
            }

        except Exception as e:
            return {"error": f"Failed to fetch profile: {str(e)}"}
