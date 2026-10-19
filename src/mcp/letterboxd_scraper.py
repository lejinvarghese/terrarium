"""Letterboxd public profile scraper - uses Playwright for Cloudflare bypass.

Letterboxd's API is not public (request-only). This module scrapes
public profile data using Playwright headless browser to bypass Cloudflare.
"""

import re
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
            Dict with name, profile_url, film_count, stats, etc.
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

    def _parse_film_item(self, item: Any) -> dict[str, Any] | None:
        """Parse a single film item from list."""
        poster = item.select_one(".film-poster")
        if not poster:
            return None

        title = poster.get("data-film-name", "Unknown")
        film_slug = poster.get("data-film-slug")
        film_url = f"{self.BASE_URL}/film/{film_slug}/" if film_slug else None

        year = self._extract_film_year(item)
        rating = self._extract_user_rating(item)

        return {
            "title": title,
            "year": year,
            "rating": rating,
            "url": film_url,
            "slug": film_slug,
        }

    def _extract_film_year(self, item: Any) -> int | None:
        """Extract release year from film item."""
        year_elem = item.select_one(".film-poster img")
        if not year_elem:
            return None

        alt_text = year_elem.get("alt")
        if alt_text and isinstance(alt_text, str):
            year_match = re.search(r"\((\d{4})\)", alt_text)
            if year_match:
                return int(year_match.group(1))
        return None

    def _extract_user_rating(self, item: Any) -> float | None:
        """Extract user rating from film item."""
        rating_elem = item.select_one(".poster-viewingdata .rating")
        if rating_elem:
            stars = len(rating_elem.select(".rated-"))
            return stars / 2
        return None

    async def get_user_films(
        self, username: str, list_type: str = "films", limit: int = 20
    ) -> dict[str, Any]:
        """Get films from a user's list.

        Args:
            username: Letterboxd username
            list_type: Type of list - 'films' (all), 'diary', 'watchlist', 'likes'
            limit: Max films to return (default 20)

        Returns:
            Dict with films list and metadata
        """
        url = f"{self.BASE_URL}/{username}/{list_type}/"

        try:
            html = await self._fetch_page(url)
            soup = BeautifulSoup(html, "lxml")

            films = []
            film_items = soup.select("li.poster-container")

            for item in film_items[:limit]:
                film = self._parse_film_item(item)
                if film:
                    films.append(film)

            return {"list_type": list_type, "count": len(films), "films": films}

        except Exception as e:
            return {"error": f"Failed to fetch films: {str(e)}"}

    def _extract_film_metadata(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract film metadata from soup."""
        title_elem = soup.select_one("h1.headline-1")
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"

        year_elem = soup.select_one(".film-title-wrapper .metadata a")
        year = year_elem.get_text(strip=True) if year_elem else None

        director_elem = soup.select_one("#tab-crew .text-slug")
        director = director_elem.get_text(strip=True) if director_elem else None

        return {"title": title, "year": year, "director": director}

    def _extract_film_rating(self, soup: BeautifulSoup) -> tuple[float | None, int | None]:
        """Extract film rating and count."""
        rating = None
        rating_elem = soup.select_one(".average-rating a")
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            try:
                rating = float(rating_text)
            except ValueError:
                pass

        rating_count = None
        rating_count_elem = soup.select_one(".all-link")
        if rating_count_elem:
            count_match = re.search(r"([\d,]+)\s+ratings", rating_count_elem.get_text())
            if count_match:
                rating_count = int(count_match.group(1).replace(",", ""))

        return rating, rating_count

    def _extract_film_description(self, soup: BeautifulSoup) -> str | None:
        """Extract film description."""
        desc_elem = soup.select_one(".truncate p")
        return desc_elem.get_text(strip=True) if desc_elem else None

    def _extract_film_genres(self, soup: BeautifulSoup) -> list[str]:
        """Extract film genres."""
        genres = []
        genre_elems = soup.select("#tab-genres .text-slug")
        for genre in genre_elems:
            genres.append(genre.get_text(strip=True))
        return genres

    async def get_film_details(self, film_slug: str) -> dict[str, Any]:
        """Get details for a specific film.

        Args:
            film_slug: Letterboxd film slug (e.g., 'the-matrix')

        Returns:
            Dict with title, year, director, rating, description, etc.
        """
        url = f"{self.BASE_URL}/film/{film_slug}/"

        try:
            html = await self._fetch_page(url)
            soup = BeautifulSoup(html, "lxml")

            metadata = self._extract_film_metadata(soup)
            rating, rating_count = self._extract_film_rating(soup)
            description = self._extract_film_description(soup)
            genres = self._extract_film_genres(soup)

            return {
                **metadata,
                "rating": rating,
                "rating_count": rating_count,
                "description": description,
                "genres": genres,
                "url": url,
            }

        except Exception as e:
            return {"error": f"Failed to fetch film: {str(e)}"}
