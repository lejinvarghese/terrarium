# Meanwhile - Toronto Edition

A modified version of [tomdavenport/meanwhile](https://github.com/tomdavenport/meanwhile) customized for Toronto with Tavily search integration.

## What is Meanwhile?

A terminal Matrix-style "code rain" that displays live news headlines, local intelligence, and poetic real-time facts sweeping across your terminal.

## Modifications from Original

### 1. **Tavily Search Integration** (instead of Exa)

- Uses Tavily API for AI-powered news search
- Requires `TAVILY_API_KEY` environment variable
- Falls back to RSS feeds if no API key configured

### 2. **Toronto Customization**

- Default region: Canada (`ca`)
- Default places: `["Toronto", "Ontario"]`
- Default topics: `["world news", "artificial intelligence", "science", "canada"]`

### 3. **Enhanced News Sources**

- **Main News**: Fox News RSS feed
- **Scientific RSS Feeds**:
  - Nature
  - Science Magazine
  - Phys.org
  - Scientific American
  - ScienceDaily
  - Nature Biotechnology
  - arXiv (Computer Science & Physics)
  - MIT Technology Review
  - Quanta Magazine

## Installation

### Prerequisites

- Python 3.11 or later
- Optional: Tavily API key for enhanced news search

### Setup

1. **Clone or copy this directory**:

   ```bash
   cd /media/starscream/bumblebee1/blaze/terrarium/meanwhile-toronto
   ```

2. **Make the script executable**:

   ```bash
   chmod +x meanwhile.py
   ```

3. **Create a symlink** (optional, for easy access):

   ```bash
   ln -sf "$PWD/meanwhile.py" ~/.local/bin/meanwhile
   ```

4. **Set up API key** (optional, for Tavily search):

   ```bash
   export TAVILY_API_KEY="your-api-key-here"
   ```

   Or add to `~/.env`:

   ```bash
   echo 'TAVILY_API_KEY=your-api-key-here' >> ~/.env
   ```

## Usage

```bash
# Run directly
./meanwhile.py

# Or if you created the symlink
meanwhile

# Offline mode (poetic facts only, no news)
meanwhile --offline
```

### Keyboard Controls

- **Click/Enter**: Decode story summary
- **t**: Edit topics
- **g**: Edit places
- **f**: Toggle focus mode
- **Space**: Pause/resume
- **q**: Quit

## Configuration

Configuration is stored in `~/.config/meanwhile/config.json` and auto-created on first run.

### Default Config (Toronto Edition)

```json
{
  "topics": ["world news", "artificial intelligence", "science", "canada"],
  "places": ["Toronto", "Ontario"],
  "refresh_minutes": 15,
  "hours_back": 36,
  "region": "ca",
  "theme": "auto",
  "env_files": ["~/.env", "~/dev/.env"]
}
```

### Customization Options

- **topics**: List of news topics to track
- **places**: List of locations for local intelligence
- **refresh_minutes**: How often to fetch new headlines (default: 15)
- **hours_back**: How far back to search for news (default: 36)
- **poetic_ratio**: Ratio of poetic facts to news (0.0-1.0, default: 0.4)
- **density**: Visual density of the rain effect (default: 0.75)
- **speed**: Animation speed multiplier (default: 1.0)
- **theme**: `"auto"` (detect), `"terminal"`, or `"matrix"`
- **show_source**: Append domain name to headlines (default: false)

## API Key Setup

### Tavily API

1. Get a free API key from [tavily.com](https://tavily.com)
2. Add to environment:
   ```bash
   export TAVILY_API_KEY="tvly-xxxxx"
   ```

### Without API Key

The application will automatically fall back to RSS feeds (Fox News + Science feeds) if no Tavily API key is configured.

## Differences from Original

| Feature        | Original                     | This Version                                |
| -------------- | ---------------------------- | ------------------------------------------- |
| Search API     | Exa                          | Tavily                                      |
| Default Region | Auto-detect                  | Canada (Toronto)                            |
| News Sources   | BBC, Guardian, Al Jazeera    | Fox News                                    |
| Science Feeds  | None                         | 10 scientific sources                       |
| Default Topics | `["world news", "ai", "uk"]` | `["world news", "ai", "science", "canada"]` |

## Files

- `meanwhile.py` - Main application (modified)
- `meanwhile_original.py` - Original unmodified version from upstream
- `README.md` - This file

## License

MIT License (same as original)

## Credits

- Original project: [tomdavenport/meanwhile](https://github.com/tomdavenport/meanwhile)
- Modified for Toronto with Tavily integration
