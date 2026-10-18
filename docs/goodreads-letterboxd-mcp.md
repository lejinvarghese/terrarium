# Goodreads & Letterboxd MCP Integration

Integration for reading public Goodreads and Letterboxd profiles via the Terrarium MCP server.

## Why Web Scraping?

- **Goodreads**: Amazon/Goodreads shut down their public API in December 2020 and stopped issuing new developer keys. No official API access is available.
- **Letterboxd**: Their API exists but is not public - available only by request to select developers with OAuth2 authentication.

Both integrations use web scraping to access **public profile data only**. The user's profile must be set to public for these tools to work.

## Available Tools

### Goodreads

#### `goodreads_get_profile(username: str)`

Get basic profile info for a public Goodreads user.

**Args:**

- `username`: Goodreads username or numeric user ID

**Returns:**

- Profile with name, stats (books, reviews, etc.), currently reading list

**Example:**

```python
result = await goodreads_get_profile("neilhimself")
# Returns: {name, username, profile_url, stats, currently_reading}
```

#### `goodreads_get_books(username: str, shelf: str = "read", limit: int = 20)`

Get books from a user's Goodreads shelf.

**Args:**

- `username`: Goodreads username or numeric user ID
- `shelf`: Shelf name - `read`, `currently-reading`, `to-read`, or custom shelf
- `limit`: Max books to return (default 20, max 100)

**Returns:**

- List of books with title, author, rating, date read, review snippet

**Examples:**

```python
# Recently read books
goodreads_get_books("username", shelf="read", limit=10)

# Current reads
goodreads_get_books("username", shelf="currently-reading")

# TBR pile
goodreads_get_books("username", shelf="to-read", limit=50)
```

#### `goodreads_get_book(book_id: str)`

Get details for a specific book on Goodreads.

**Args:**

- `book_id`: Goodreads book ID (numeric) or book URL

**Returns:**

- Book details with title, author, rating, description, review count

**Examples:**

```python
# By ID
goodreads_get_book("21787")

# By URL
goodreads_get_book("https://www.goodreads.com/book/show/21787-the-hobbit")
```

### Letterboxd

#### `letterboxd_get_profile(username: str)`

Get basic profile info for a public Letterboxd user.

**Args:**

- `username`: Letterboxd username

**Returns:**

- Profile with name, stats (films, lists, etc.), favorites, recent activity

**Example:**

```python
result = await letterboxd_get_profile("jack")
# Returns: {name, username, profile_url, stats, favorites, recent_activity}
```

#### `letterboxd_get_films(username: str, list_type: str = "films", limit: int = 20)`

Get films from a user's Letterboxd list.

**Args:**

- `username`: Letterboxd username
- `list_type`: Type of list - `films` (all rated), `diary`, `watchlist`, `likes`
- `limit`: Max films to return (default 20, max 100)

**Returns:**

- List of films with title, year, rating (if rated), URL

**Examples:**

```python
# All rated films
letterboxd_get_films("username", "films", 50)

# Diary entries
letterboxd_get_films("username", "diary", 20)

# Watchlist
letterboxd_get_films("username", "watchlist")

# Liked films
letterboxd_get_films("username", "likes", 30)
```

#### `letterboxd_get_film(film_slug: str)`

Get details for a specific film on Letterboxd.

**Args:**

- `film_slug`: Letterboxd film slug (e.g., `the-matrix`, `parasite-2019`)

**Returns:**

- Film details with title, year, director, rating, description, genres

**Examples:**

```python
letterboxd_get_film("the-matrix")
letterboxd_get_film("everything-everywhere-all-at-once")
```

## Use Cases

### Sage (Reading Recommendations)

```python
# Check what someone is currently reading for context
profile = await goodreads_get_profile("username")
currently_reading = profile["currently_reading"]

# Get their recent reads to understand taste
recent = await goodreads_get_books("username", shelf="read", limit=10)

# Recommend based on their reading history
```

### Anya (Film Curation)

```python
# Check someone's film taste via recent diary
recent_films = await letterboxd_get_films("username", "diary", 20)

# See their favorites
profile = await letterboxd_get_profile("username")
favorites = profile["favorites"]

# Curate recommendations based on their ratings
```

### Cross-Domain Analysis

```python
# Compare reading vs watching habits
books = await goodreads_get_books("username", limit=50)
films = await letterboxd_get_films("username", "films", 50)

# Find book-to-film adaptations in their library
# Analyze genre preferences across media
```

## Implementation Details

### Dependencies

- `httpx`: Async HTTP client
- `beautifulsoup4`: HTML parsing
- `lxml`: Fast XML/HTML parser

### Scraping Approach

- **Goodreads**: Uses JSON-LD structured data where available (more stable than HTML selectors)
- **Letterboxd**: Parses HTML with CSS selectors targeting public profile pages
- Both use realistic User-Agent headers to avoid bot detection
- Rate limiting: Built-in httpx timeout (30s) prevents hammering

### Limitations

- Only works with **public profiles** - private profiles return errors
- HTML structure can change - selectors may need updates if sites redesign
- No authentication - can't access private shelves/lists/ratings
- Rate limiting: Respect the sites' terms of service, don't spam requests
- Cloudflare: Letterboxd uses Cloudflare - may occasionally block automated requests

### Terms of Service

Check both sites' ToS before heavy scraping:

- **Goodreads ToS**: https://www.goodreads.com/about/terms
- **Letterboxd ToS**: https://letterboxd.com/legal/terms-of-use/

## Future Enhancements

Potential improvements if needed:

- [ ] Caching layer to reduce duplicate requests
- [ ] Retry logic with exponential backoff
- [ ] User-configurable request delays
- [ ] Support for custom lists/shelves
- [ ] Review text extraction (full reviews, not just snippets)
- [ ] Search functionality (find books/films by title/author/director)
- [ ] Export to CSV/JSON for archival

## Testing

Quick test of both scrapers:

```bash
cd /media/starscream/bumblebee1/blaze/terrarium
PYTHONPATH=. python3 /path/to/test_scrapers.py
```

## Sources

Research links for reference:

**Goodreads:**

- [Goodreads API Deprecation Discussion](https://www.goodreads.com/topic/show/21788520-api-deprecation)
- [YashTotale/goodreads-user-scraper](https://github.com/YashTotale/goodreads-user-scraper)
- [How to Scrape Goodreads (Scrapfly Guide)](https://scrapfly.io/blog/posts/how-to-scrape-goodreads)

**Letterboxd:**

- [bobtiki/letterboxd Python Wrapper](https://pypi.org/project/letterboxd/)
- [L-Dot/Letterboxd-list-scraper](https://github.com/L-Dot/Letterboxd-list-scraper)
- [Gurubase: Scraping Letterboxd with Python](https://gurubase.io/g/python/scraping-individual-reviews-letterboxd-python)
