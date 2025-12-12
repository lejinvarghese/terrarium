#!/bin/bash
# Interactive Cloudflare Named Tunnel Setup for Terrarium

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Load common utilities
source "$SCRIPT_DIR/../lib/common.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

DOMAIN="mutatedterrarium.com"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🌿 Terrarium Cloudflare Tunnel Setup Wizard         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Domain: ${DOMAIN}${NC}"
echo ""

# Check cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo_error "cloudflared is not installed"
    echo ""
    echo "Install with:"
    echo "  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    echo "  sudo dpkg -i cloudflared-linux-amd64.deb"
    exit 1
fi

echo_success "cloudflared $(cloudflared --version | head -1 | awk '{print $3}')"
echo ""

# Step 1: Domain setup
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 1: Add Domain to Cloudflare${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Go to: ${CYAN}https://dash.cloudflare.com${NC}"
echo "2. Click '${GREEN}Add a Site${NC}'"
echo "3. Enter: ${GREEN}${DOMAIN}${NC}"
echo "4. Select '${GREEN}Free${NC}' plan"
echo "5. Update nameservers at your registrar"
echo "6. Wait for Cloudflare confirmation email"
echo ""
read -p "Press Enter when domain is active in Cloudflare..."
echo ""

# Step 2: Authenticate
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 2: Authenticate cloudflared${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f ~/.cloudflared/cert.pem ]; then
    echo_success "Already authenticated"
else
    echo "Opening browser for authentication..."
    echo ""
    read -p "Press Enter to continue..."

    cloudflared tunnel login

    if [ -f ~/.cloudflared/cert.pem ]; then
        echo ""
        echo_success "Authentication successful"
    else
        echo_error "Authentication failed"
        exit 1
    fi
fi
echo ""

# Step 3: Create tunnel
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 3: Create Named Tunnel${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

TUNNEL_NAME="terrarium"

if cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo_success "Tunnel '${TUNNEL_NAME}' already exists"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
else
    echo "Creating tunnel..."
    cloudflared tunnel create "$TUNNEL_NAME"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
    echo_success "Tunnel created: ${TUNNEL_ID}"
fi

echo ""
echo_info "Tunnel ID: ${TUNNEL_ID}"

CREDS_FILE=$(ls ~/.cloudflared/${TUNNEL_ID}.json 2>/dev/null || ls ~/.cloudflared/*.json 2>/dev/null | head -1)

if [ -z "$CREDS_FILE" ]; then
    echo_error "Could not find tunnel credentials"
    exit 1
fi

echo_info "Credentials: ${CREDS_FILE}"
echo ""

# Step 4: Create config
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 4: Configure Tunnel Routing${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

CONFIG_FILE="$HOME/.cloudflared/config.yml"

cat > "$CONFIG_FILE" << EOF
# Terrarium Cloudflare Tunnel Configuration
# Domain: ${DOMAIN}
# Created: $(date)

tunnel: ${TUNNEL_ID}
credentials-file: ${CREDS_FILE}

ingress:
  # Main web interface
  - hostname: ${DOMAIN}
    service: http://localhost:3000

  # Dome (Open WebUI)
  - hostname: dome.${DOMAIN}
    service: http://localhost:8080

  # Archive (Stash)
  - hostname: archive.${DOMAIN}
    service: http://localhost:8502

  # Archive API - Protected by Cloudflare Access (manual setup required)
  # See docs/CLOUDFLARE_ACCESS.md for setup instructions
  - hostname: api.${DOMAIN}
    service: http://localhost:5055

  # SSH access - REMOVED (security): Use Tailscale/Cloudflare Access instead (see docs/SSH_ACCESS.md)

  # Catch-all
  - service: http_status:404
EOF

echo_success "Configuration created"
echo ""
echo "Services configured:"
echo "  🌐 ${DOMAIN}               → Web"
echo "  🤖 dome.${DOMAIN}          → Dome"
echo "  📚 archive.${DOMAIN}       → Archive"
echo "  🔌 api.${DOMAIN}           → API"
echo "  🔐 ssh.${DOMAIN}           → SSH"
echo ""

# Step 5: Route DNS
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 5: Configure DNS Routing${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

ROUTES=("${DOMAIN}" "dome.${DOMAIN}" "archive.${DOMAIN}" "api.${DOMAIN}" "ssh.${DOMAIN}")

for route in "${ROUTES[@]}"; do
    echo -n "  Routing ${route}... "
    OUTPUT=$(cloudflared tunnel route dns "$TUNNEL_NAME" "$route" 2>&1)
    if echo "$OUTPUT" | grep -q "already exists"; then
        echo -e "${YELLOW}exists${NC}"
    elif echo "$OUTPUT" | grep -q "error"; then
        echo -e "${RED}failed${NC}"
    else
        echo -e "${GREEN}✓${NC}"
    fi
done

echo ""
echo_success "DNS routing configured"
echo ""

# Step 6: Update .env
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 6: Update Environment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    sed -i '/^USE_NAMED_TUNNEL=/d' "$ENV_FILE"
    sed -i '/^TUNNEL_NAME=/d' "$ENV_FILE"
    sed -i '/^TUNNEL_DOMAIN=/d' "$ENV_FILE"
    sed -i '/^TUNNEL_ID=/d' "$ENV_FILE"
else
    touch "$ENV_FILE"
fi

cat >> "$ENV_FILE" << EOF

# Cloudflare Named Tunnel
USE_NAMED_TUNNEL=true
TUNNEL_NAME=${TUNNEL_NAME}
TUNNEL_DOMAIN=${DOMAIN}
TUNNEL_ID=${TUNNEL_ID}
EOF

echo_success "Environment updated"
echo ""

# Step 7: Validate
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Step 7: Validate Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if cloudflared tunnel ingress validate 2>&1 | grep -qi "ok\|valid"; then
    echo_success "Configuration is valid"
else
    echo_error "Configuration validation failed"
    echo ""
    echo "Run this to see details:"
    echo "  cloudflared tunnel ingress validate"
    exit 1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✨ Setup Complete! ✨                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Your services will be available at:${NC}"
echo ""
echo -e "  🌐 ${GREEN}https://${DOMAIN}${NC}"
echo -e "  🤖 ${GREEN}https://dome.${DOMAIN}${NC}"
echo -e "  📚 ${GREEN}https://archive.${DOMAIN}${NC}"
echo -e "  🔌 ${GREEN}https://api.${DOMAIN}${NC}"
echo ""
echo -e "${YELLOW}Next:${NC} Run ${CYAN}./dev up${NC} to start all services with the named tunnel"
echo ""
