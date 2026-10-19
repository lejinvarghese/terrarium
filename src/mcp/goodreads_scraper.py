"""Goodreads public profile scraper - no API required.

Goodreads shut down its API in December 2020. This module scrapes
public profile data using BeautifulSoup + structured JSON-LD data.

ONLY WORKING METHODS INCLUDED - broken shelf/book methods removed.
"""

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup


class GoodreadsScraper:
    """Scraper for public Goodreads profiles."""

    BASE_URL = "https://www.goodreads.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    def __init__(self):
        self.client = httpx.AsyncClient(headers=self.HEADERS, timeout=30.0, follow_redirects=True)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_user_url(self, username: str) -> str:
        """Build user profile URL from username or ID."""
        if username.isdigit():
            return f"{self.BASE_URL}/user/show/{username}"
        return f"{self.BASE_URL}/{username}"

    def _extract_profile_stats(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract profile statistics from soup and meta tags."""
        stats = {}

        # Try structured stats first
        stat_elems = soup.select(".userStats .statItem")
        for stat in stat_elems:
            label_elem = stat.select_one(".statLabel")
            count_elem = stat.select_one(".statNumber")
            if label_elem and count_elem:
                label = label_elem.get_text(strip=True).lower()
                count_text = count_elem.get_text(strip=True)
                stats[label] = int(count_text.replace(",", ""))

        # Fallback: extract from meta description
        # e.g., "Lejin Varghese has 319 books on Goodreads"
        if not stats:
            meta = soup.find("meta", {"name": "description"})
            if meta:
                desc = meta.get("content", "")
                book_count_match = re.search(r"has (\d+) books", desc)
                if book_count_match:
                    stats["books"] = int(book_count_match.group(1))

        return stats

    def _extract_currently_reading(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extract currently reading books from profile page.

        Note: Goodreads shows 1-3 books on the public profile page.
        """
        currently_reading = []

        # Profile page uses ALL .Updates divs (not just .no_border)
        current_reading_div = soup.select_one("#currentlyReadingReviews")
        if current_reading_div:
            books = current_reading_div.select(".Updates")
            for book in books:
                title_elem = book.select_one(".bookTitle")
                author_elem = book.select_one(".authorName")
                if title_elem:
                    currently_reading.append(
                        {
                            "title": title_elem.get_text(strip=True),
                            "author": (author_elem.get_text(strip=True) if author_elem else None),
                        }
                    )

        return currently_reading

    async def get_user_profile(self, username: str) -> dict[str, Any]:
        """Get basic profile info for a Goodreads user.

        Args:
            username: Goodreads username or user ID

        Returns:
            Dict with name, profile_url, books_count, currently_reading
        """
        url = self._build_user_url(username)

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            name_elem = soup.select_one("h1.userProfileName")
            name = name_elem.get_text(strip=True) if name_elem else "Unknown"

            stats = self._extract_profile_stats(soup)
            currently_reading = self._extract_currently_reading(soup)

            return {
                "name": name,
                "username": username,
                "profile_url": url,
                "stats": stats,
                "currently_reading": currently_reading,
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"User '{username}' not found"}
            return {"error": f"HTTP error {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to fetch profile: {str(e)}"}
