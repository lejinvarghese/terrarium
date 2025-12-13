# Secure Access System

Compact modal-based access control with **single sign-on** across all subdomains.

## Features

- **Single Sign-On**: Enter code once, access everywhere
- Shared cookie across `*.mutatedterrarium.com`
- Works on homepage modal and direct subdomain visits
- Cyberpunk corner-bracket design
- Multiple access codes supported

## Default Access Codes

```
UNDERGROWTH
TERR4R1UM
CYB3RN3T1C
SW4RM
ECLIPSE
```

*Case-insensitive*

## Protected Services

- **Dome** (`dome.mutatedterrarium.com`)
- **Archive** (`archive.mutatedterrarium.com`)

### Single Sign-On Flow

Enter code **once** (homepage or direct subdomain) → cookie set with domain `.mutatedterrarium.com` → all services unlocked for 24h

## Quick Config

### Change Codes

`web/utils/accessConfig.ts`:
```typescript
const DEFAULT_CODES = ['CODE1', 'CODE2'];
```

### Add/Remove Protected Services

`web/components/sections/ServiceCard.tsx`:
```typescript
const SECURE_SERVICES = ['dome', 'archive'];
```

## Testing

**Option 1 - Homepage:**
1. Go to https://mutatedterrarium.com
2. Click Dome/Archive card → modal appears
3. Enter code → redirected
4. Visit other subdomain → no second login needed

**Option 2 - Direct:**
1. Go to https://dome.mutatedterrarium.com
2. Full-page login appears
3. Enter code → access granted
4. Visit https://archive.mutatedterrarium.com → already authenticated

## Architecture

**Homepage** → Sets cookie via React modal
**Subdomains** → Auth proxy checks cookie, proxies to backend

## Files

```
web/components/ui/
├── SecureAccessModal.tsx          # Homepage modal (sets cookie)
└── SecureAccessModal.module.css

src/auth-proxy/
├── server.js                      # Express auth proxy
└── config.json                    # Codes & service config

scripts/
├── start_dome_proxy.sh            # Dome proxy (port 8081 → 8080)
└── start_archive_proxy.sh         # Archive proxy (port 8503 → 8502)
```

## Usage

### Standalone Button

```tsx
<SecureButton
  label="CUSTOM ENTRY"
  targetUrl="/protected"
  modalTitle="ACCESS"
  variant="primary"
/>
```

### Custom Codes per Button

```tsx
<SecureButton
  label="ADMIN"
  targetUrl="/admin"
  validCodes={['ADMIN123', 'R00T']}
/>
```

## Logout

`https://dome.mutatedterrarium.com/auth/logout` or `https://archive.mutatedterrarium.com/auth/logout`

## Security Note

⚠️ **Convenience only** - Codes in plaintext, cookie-based, no rate limiting. For production: use Cloudflare Access.
