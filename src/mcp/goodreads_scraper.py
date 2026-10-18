"""Goodreads public profile scraper - no API required.

Goodreads shut down its API in December 2020. This module scrapes
public profile data using BeautifulSoup + structured JSON-LD data.
"""

import json
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

    def _extract_profile_stats(self, soup: BeautifulSoup) -> dict[str, int]:
        """Extract profile statistics from soup."""
        stats = {}
        stat_elems = soup.select(".userStats .statItem")
        for stat in stat_elems:
            label_elem = stat.select_one(".statLabel")
            count_elem = stat.select_one(".statNumber")
            if label_elem and count_elem:
                label = label_elem.get_text(strip=True).lower()
                count_text = count_elem.get_text(strip=True)
                stats[label] = int(count_text.replace(",", ""))
        return stats

    def _extract_currently_reading(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extract currently reading books from soup."""
        currently_reading = []
        reading_section = soup.select(".currentlyReadingReviews .bookalike")
        for book in reading_section[:5]:
            title_elem = book.select_one(".title")
            author_elem = book.select_one(".author")
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
            Dict with name, profile_url, books_count, reviews_count, etc.
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

    def _parse_book_row(self, row: Any) -> dict[str, Any] | None:
        """Parse a single book row from shelf."""
        title_elem = row.select_one(".title a")
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        href = title_elem.get("href")
        book_url = f"{self.BASE_URL}{href}" if href else None

        author_elem = row.select_one(".author a")
        author = author_elem.get_text(strip=True) if author_elem else None

        rating = self._extract_rating(row)
        date_elem = row.select_one(".date_read .value")
        date_read = date_elem.get_text(strip=True) if date_elem else None

        review_elem = row.select_one(".review_text_container")
        review = review_elem.get_text(strip=True)[:200] if review_elem else None

        return {
            "title": title,
            "author": author,
            "rating": rating,
            "date_read": date_read,
            "review_snippet": review,
            "url": book_url,
        }

    def _extract_rating(self, row: Any) -> int | None:
        """Extract user rating from book row."""
        rating_elem = row.select_one(".rating .value")
        if not rating_elem:
            return None

        rating_text = rating_elem.get_text(strip=True)
        if rating_text and rating_text != "did not like it":
            try:
                return int(rating_text[0])
            except (ValueError, IndexError):
                pass
        return None

    async def get_user_books(
        self, username: str, shelf: str = "read", limit: int = 20
    ) -> dict[str, Any]:
        """Get books from a user's shelf.

        Args:
            username: Goodreads username or user ID
            shelf: Shelf name (read, currently-reading, to-read, or custom shelf)
            limit: Max books to return (default 20)

        Returns:
            Dict with books list and metadata
        """
        if username.isdigit():
            base_url = f"{self.BASE_URL}/review/list/{username}"
        else:
            base_url = f"{self.BASE_URL}/review/list/{username}"

        try:
            response = await self.client.get(base_url, params={"shelf": shelf, "per_page": limit})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            books = []
            book_rows = soup.select("#booksBody tr")

            for row in book_rows[:limit]:
                book = self._parse_book_row(row)
                if book:
                    books.append(book)

            return {"shelf": shelf, "count": len(books), "books": books}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "User or shelf not found"}
            return {"error": f"HTTP error {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to fetch books: {str(e)}"}

    def _extract_book_id(self, book_id: str) -> str:
        """Extract numeric book ID from URL if needed."""
        if "/" in book_id:
            match = re.search(r"/book/show/(\d+)", book_id)
            if match:
                return match.group(1)
        return book_id

    def _extract_json_ld_book_data(self, soup: BeautifulSoup) -> dict[str, Any] | None:
        """Try to extract book data from JSON-LD structured data."""
        json_ld = soup.find("script", {"type": "application/ld+json"})
        if not json_ld or not json_ld.string:
            return None

        try:
            data = json.loads(str(json_ld.string))
            return {
                "title": data.get("name"),
                "author": (data.get("author", [{}])[0].get("name") if data.get("author") else None),
                "rating": data.get("aggregateRating", {}).get("ratingValue"),
                "rating_count": data.get("aggregateRating", {}).get("ratingCount"),
                "review_count": data.get("aggregateRating", {}).get("reviewCount"),
                "description": data.get("description"),
            }
        except (json.JSONDecodeError, KeyError):
            return None

    def _extract_html_book_data(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Fallback: extract book data from HTML."""
        title_elem = soup.select_one("h1.Text__title1")
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"

        author_elem = soup.select_one(".ContributorLink__name")
        author = author_elem.get_text(strip=True) if author_elem else None

        rating = None
        rating_elem = soup.select_one(".RatingStatistics__rating")
        if rating_elem:
            try:
                rating = float(rating_elem.get_text(strip=True))
            except ValueError:
                pass

        return {"title": title, "author": author, "rating": rating}

    async def get_book_details(self, book_id: str) -> dict[str, Any]:
        """Get details for a specific book using structured data.

        Args:
            book_id: Goodreads book ID or book URL slug

        Returns:
            Dict with title, author, rating, description, etc.
        """
        book_id = self._extract_book_id(book_id)
        url = f"{self.BASE_URL}/book/show/{book_id}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            book_data = self._extract_json_ld_book_data(soup)
            if book_data:
                book_data["url"] = url
                return book_data

            book_data = self._extract_html_book_data(soup)
            book_data["url"] = url
            return book_data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "Book not found"}
            return {"error": f"HTTP error {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to fetch book: {str(e)}"}
