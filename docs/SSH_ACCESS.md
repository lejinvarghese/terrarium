# SSH Access to Terrarium (Mac to Linux)

## Overview

This guide covers secure methods to SSH from your Mac to your home Linux PC (Terrarium) while traveling.

**⚠️ Security Notice:** The current `ssh.mutatedterrarium.com` subdomain exposes SSH to the entire internet without additional authentication. This document provides secure alternatives.

---

## Quick Access Methods

### A) Local Network (Same WiFi)

**From your Mac:**
```bash
ssh starscream@10.88.111.17
```

That's it. You're in.

---

### B) Remote Access (While Traveling) - **SECURE OPTIONS**

You have several secure options for remote SSH access:

1. **Cloudflare Access with Authentication** (Recommended - most secure)
2. **Cloudflare Quick Tunnel** (Simple, temporary URLs)
3. **Tailscale VPN** (Best UX, zero-config mesh network)
4. **Direct SSH with Dynamic DNS** (Traditional, requires router config)

---

## Option 1: Cloudflare Access with Authentication ⭐ RECOMMENDED

**Why:** Adds email/SSO authentication before allowing SSH access. Only you can connect.

### Setup on Home PC (One-time):

1. **Install Cloudflare Zero Trust** (if not already done):
   ```bash
   # Already installed via your setup
   cloudflared --version
   ```

2. **Create Access Policy** (via Cloudflare Dashboard):
   - Go to https://one.dash.cloudflare.com/
   - Navigate to **Access** → **Applications** → **Add an application**
   - Choose **Self-hosted**
   - **Application name:** Terrarium SSH
   - **Subdomain:** `ssh-secure`
   - **Domain:** `mutatedterrarium.com`
   - **Path:** Leave blank
   - Click **Next**

3. **Configure Policy:**
   - **Policy name:** Only Me
   - **Action:** Allow
   - **Include:** `Emails` → Enter your email address
   - **Require:** None (or add 2FA if desired)
   - Click **Next** → **Add application**

4. **Update Cloudflare Tunnel Config** (`~/.cloudflared/config.yml`):
   ```yaml
   ingress:
     # Other services...

     # Secure SSH with authentication
     - hostname: ssh-secure.mutatedterrarium.com
       service: ssh://localhost:22
       originRequest:
         access:
           required: true
           teamName: your-team-name  # From Zero Trust dashboard
           audTag: your-aud-tag      # From Access application settings

     # Catch-all
     - service: http_status:404
   ```

5. **Restart tunnel:**
   ```bash
   ./dev restart
   ```

### Usage from Mac:

1. **Install cloudflared:**
   ```bash
   brew install cloudflared
   ```

2. **Authenticate once:**
   ```bash
   cloudflared access login ssh-secure.mutatedterrarium.com
   ```
   This opens a browser to log in with your email. You'll see "Success" when done.

3. **Connect:**
   ```bash
   ssh starscream@ssh-secure.mutatedterrarium.com
   ```

   Or add to `~/.ssh/config`:
   ```
   Host terrarium-secure
       HostName ssh-secure.mutatedterrarium.com
       User starscream
       ProxyCommand cloudflared access ssh --hostname %h
   ```

   Then just:
   ```bash
   ssh terrarium-secure
   ```

**Security:**
- ✅ Requires authentication (your email)
- ✅ Only you can access
- ✅ Cloudflare logs all access attempts
- ✅ Can add 2FA for extra security

---

## Option 2: Cloudflare Quick Tunnel (Temporary, No Auth)

**Why:** Quick and easy, but URL changes each time. Good for occasional use.

### Setup on Home PC:

Your system already creates quick tunnels. To get the current SSH command:

**Option 1:** Run on the server:
```bash
./scripts/ssh_connect.sh
```

**Option 2:** Check status:
```bash
./dev status
```

Both will show you the current SSH command. Copy and run it on your Mac.

### Usage from Mac:

1. **Install cloudflared:**
   ```bash
   brew install cloudflared
   ```

2. **Get connection command** (from home PC terminal):
   ```bash
   ssh -o ProxyCommand="cloudflared access tcp --hostname https://casino-oclc-queen-else.trycloudflare.com" starscream@10.88.111.17
   ```

3. **Run it:**
   Copy and paste the full command into your Mac terminal.

**Security:**
- ⚠️ No authentication - anyone with the URL can attempt to connect
- ⚠️ URL is public and changes frequently
- ✅ Still requires valid SSH credentials
- ✅ Encrypted connection

**Recommendation:** Only use this for temporary access. Delete the tunnel when done:
```bash
./dev tunnel-manager down ssh
```

---

## Option 3: Tailscale VPN 🚀 BEST USER EXPERIENCE

**Why:** Zero-config mesh VPN. Best balance of security and convenience.

### Setup on Home PC (One-time):

1. **Install Tailscale:**
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   ```

2. **Authenticate:**
   ```bash
   sudo tailscale up
   ```
   Opens browser to log in with Google/GitHub/etc.

3. **Get Tailscale IP:**
   ```bash
   tailscale ip -4
   ```
   Example: `100.101.102.103`

### Setup on Mac (One-time):

1. **Install Tailscale:**
   ```bash
   brew install tailscale
   ```

   Or download from https://tailscale.com/download/mac

2. **Authenticate:**
   ```bash
   sudo tailscale up
   ```

### Usage from Mac:

```bash
ssh starscream@100.101.102.103
```

Or add to `~/.ssh/config`:
```
Host terrarium-tail
    HostName 100.101.102.103
    User starscream
```

Then:
```bash
ssh terrarium-tail
```

**Security:**
- ✅ Fully authenticated (you control who's in your network)
- ✅ End-to-end encrypted
- ✅ Works behind NATs and firewalls
- ✅ Can access from any device with Tailscale
- ✅ IP stays consistent
- ✅ Free for personal use

**This is the best option for frequent remote access.**

---

## Option 4: Direct SSH with Dynamic DNS (Traditional)

**Why:** Traditional approach if you want full control and don't want third-party services.

### Requirements:
- Router with port forwarding capability
- Dynamic DNS service (DuckDNS, No-IP, Dynu, etc.)

### Setup on Home PC:

1. **Install Dynamic DNS client:**
   ```bash
   # Example: DuckDNS
   sudo apt install curl

   # Create update script
   mkdir -p ~/duckdns
   cd ~/duckdns
   echo "url=\"https://www.duckdns.org/update?domains=YOUR_SUBDOMAIN&token=YOUR_TOKEN&ip=\"" > duck.sh
   chmod +x duck.sh

   # Test it
   ./duck.sh
   ```

2. **Add to crontab** (auto-update IP):
   ```bash
   crontab -e
   # Add line:
   */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
   ```

3. **Configure router port forwarding:**
   - Log in to your router (usually 192.168.1.1 or 10.0.0.1)
   - Find "Port Forwarding" or "Virtual Server" settings
   - Forward external port 22 (or custom port like 2222) to internal `10.88.111.17:22`

4. **Secure SSH:**
   ```bash
   # Disable password auth (key-only)
   sudo nano /etc/ssh/sshd_config
   ```

   Set:
   ```
   PasswordAuthentication no
   PubkeyAuthentication yes
   PermitRootLogin no
   Port 2222  # Optional: use non-standard port
   ```

   Restart SSH:
   ```bash
   sudo systemctl restart sshd
   ```

5. **Install fail2ban** (blocks brute force):
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

### Usage from Mac:

```bash
ssh -p 2222 starscream@your-subdomain.duckdns.org
```

Or add to `~/.ssh/config`:
```
Host terrarium-direct
    HostName your-subdomain.duckdns.org
    User starscream
    Port 2222
```

Then:
```bash
ssh terrarium-direct
```

**Security:**
- ✅ Key-only authentication (no passwords)
- ✅ fail2ban blocks brute force
- ✅ Non-standard port reduces noise
- ⚠️ Still publicly exposed to internet
- ⚠️ Requires router configuration
- ⚠️ Dependent on home internet IP

---

## Make It Seamless: SSH Key Setup

### 1. Generate SSH key on Mac (if you don't have one):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location (~/.ssh/id_ed25519)
# Enter passphrase (recommended) or leave empty
```

### 2. Copy key to home PC:

**Local network:**
```bash
ssh-copy-id starscream@10.88.111.17
```

**Tailscale:**
```bash
ssh-copy-id starscream@100.101.102.103
```

**Cloudflare or other remote:**
Connect once with password, then:
```bash
ssh-copy-id -o ProxyCommand="cloudflared access ssh --hostname ssh-secure.mutatedterrarium.com" starscream@ssh-secure.mutatedterrarium.com
```

### 3. Test passwordless login:
```bash
ssh starscream@10.88.111.17
# Should log in without password
```

---

## Recommended Setup: SSH Config

Add to `~/.ssh/config` on your Mac:

```
# Local network
Host terrarium
    HostName 10.88.111.17
    User starscream

# Tailscale (recommended for remote)
Host terrarium-remote
    HostName 100.101.102.103
    User starscream

# Cloudflare Access (authenticated)
Host terrarium-secure
    HostName ssh-secure.mutatedterrarium.com
    User starscream
    ProxyCommand cloudflared access ssh --hostname %h

# Fallback: Quick tunnel (temporary)
Host terrarium-quick
    HostName 10.88.111.17
    User starscream
    ProxyCommand cloudflared access tcp --hostname PASTE_TUNNEL_URL_HERE
```

Then simply:
```bash
ssh terrarium         # local
ssh terrarium-remote  # via Tailscale
ssh terrarium-secure  # via Cloudflare Access
```

---

## Security Comparison

| Method | Security | Convenience | Setup Complexity | Cost |
|--------|----------|-------------|------------------|------|
| **Cloudflare Access** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Free |
| **Tailscale** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |
| **Quick Tunnel** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |
| **Public SSH Subdomain** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **Direct SSH + DDNS** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ~$5/yr |

---

## Final Recommendation

**For traveling/remote access:**
1. **Best: Tailscale** - Install once, works everywhere, zero hassle
2. **Alternative: Cloudflare Access** - If you prefer Cloudflare ecosystem
3. **Occasional: Quick Tunnel** - When you need temporary access

**Remove the public `ssh.mutatedterrarium.com` subdomain** - it's a security risk with no auth.

---

## Troubleshooting

### Can't connect via Tailscale:
```bash
# Check status
tailscale status

# Restart
sudo tailscale down
sudo tailscale up
```

### Can't connect via Cloudflare:
```bash
# Check tunnel status
./dev status

# Restart tunnel
./dev restart
```

### SSH connection refused:
```bash
# Check SSH is running
sudo systemctl status ssh

# Check firewall (if enabled)
sudo ufw status
```

### Key authentication not working:
```bash
# Check permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Check SSH config on server
sudo nano /etc/ssh/sshd_config
# Ensure: PubkeyAuthentication yes
```

---

## Additional Resources

- [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
- [Tailscale Documentation](https://tailscale.com/kb/)
- [SSH Hardening Guide](https://www.ssh.com/academy/ssh/security)
