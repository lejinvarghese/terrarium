# Terrarium Auth Proxy

Lightweight authentication middleware for Dome and Archive services with cyberpunk aesthetics matching the main Terrarium interface.

## Features

- 🔐 **Session-based authentication** with secure signed cookies
- 🎨 **Matching aesthetics** - uses the exact same modal design as homepage
- 🚀 **Zero-config proxy** - automatically proxies to backend services after auth
- 🔄 **Shared access codes** - same codes work across all services
- ⚡ **Minimal overhead** - Express + http-proxy-middleware

## Architecture

```
External Request
    ↓
Cloudflare Tunnel (dome.mutatedterrarium.com)
    ↓
Auth Proxy (localhost:8081)
    ↓ (if authenticated)
Open WebUI (localhost:8080)
```

## Configuration

Edit `config.json` to customize:

```json
{
  "dome": {
    "port": 8081,              // Auth proxy port
    "targetUrl": "http://localhost:8080",  // Service URL
    "title": "DOME ACCESS REQUIRED"
  },
  "archive": {
    "port": 8503,
    "targetUrl": "http://localhost:8502",
    "title": "ARCHIVE ACCESS REQUIRED"
  },
  "accessCodes": [
    "UNDERGROWTH",
    "TERR4R1UM",
    "CYB3RN3T1C",
    "SW4RM",
    "ECLIPSE"
  ],
  "cookieMaxAge": 86400000  // 24 hours
}
```

## Running

The auth proxies start automatically with `./dev up`:

```bash
./dev up         # Start all services including auth proxies
./dev status     # Check if proxies are running
./dev down       # Stop everything
```

### Manual Start

```bash
# Dome proxy
cd src/auth-proxy
SERVICE=dome node server.js

# Archive proxy
SERVICE=archive node server.js
```

## How It Works

1. **Request arrives** at auth proxy (e.g., dome.mutatedterrarium.com)
2. **Check cookie**: Does request have valid `terrarium_auth` cookie?
   - ✅ Yes → Proxy request to backend service
   - ❌ No → Show login page
3. **User enters code** → POST to `/auth/validate`
4. **Valid code** → Set signed cookie, redirect
5. **All subsequent requests** automatically proxied

## Security Notes

⚠️ **This is client-side protection for convenience, not enterprise security:**

- Access codes are in plain config (not hashed)
- Cookie signing prevents tampering but isn't encryption
- No rate limiting on login attempts
- No audit logging

**For production security**, use Cloudflare Access or similar identity provider.

## Cookie Management

- **Name**: `terrarium_auth`
- **Type**: Signed (tamper-proof)
- **Duration**: 24 hours (configurable)
- **HttpOnly**: Yes (not accessible via JavaScript)
- **SameSite**: Lax

### Logout

Visit `/auth/logout` to clear authentication cookie.

## Troubleshooting

### "Connection Error" on login
- Check if backend service is running
- Verify `targetUrl` in config.json
- Check proxy logs: `./dev attach dome-proxy`

### Login page shows but backend unreachable
- Verify backend service port matches config
- Check if backend is listening on localhost
- Try curl: `curl http://localhost:8080`

### Changes to config not applying
- Restart the proxy: `./dev down && ./dev up`
- Auth proxies don't hot-reload config changes

### Need to change access codes
- Edit `config.json`
- Restart proxies
- Or better: set via environment in services.conf

## Development

### Test without full stack

```bash
# Terminal 1: Start backend service
npm run dev  # or docker run...

# Terminal 2: Start auth proxy
cd src/auth-proxy
npm install
SERVICE=dome node server.js

# Terminal 3: Test
curl http://localhost:8081  # Should show login page
```

### Customize styling

The login page HTML is embedded in `server.js`. Edit the `loginPageHTML` constant to modify:
- Colors (cyan: `#00FFF2`, yellow: `#EBFA1D`)
- Layout and spacing
- Text content
- Animations

### Add more services

1. Add config to `config.json`:
```json
"newservice": {
  "port": 9001,
  "targetUrl": "http://localhost:9000",
  "title": "NEW SERVICE ACCESS"
}
```

2. Create startup script `scripts/start_newservice_proxy.sh`

3. Add to `services.conf`

4. Update Cloudflare tunnel config

## Files

```
src/auth-proxy/
├── server.js       # Main Express server with embedded HTML
├── config.json     # Service & access code configuration
├── package.json    # Dependencies
└── README.md       # This file

scripts/
├── start_dome_proxy.sh    # Dome proxy launcher
└── start_archive_proxy.sh # Archive proxy launcher
```

## Dependencies

- **express** - Web framework
- **http-proxy-middleware** - Proxy requests to backend
- **cookie-parser** - Parse and sign cookies

All installed automatically on first run.
