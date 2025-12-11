# SSH Access to Terrarium (Mac)

## A) Local Network (Same WiFi)

**From your Mac:**
```bash
ssh starscream@10.88.111.17
```

That's it. You're in.

## B) External Access (From Anywhere)

### 1. Install cloudflared on your Mac:
```bash
brew install cloudflared
```

### 2. Get the current SSH connection command:

The SSH tunnel starts automatically with `dev up`. To get the connection command:

**Option 1:** Run on the server:
```bash
./scripts/ssh_connect.sh
```

**Option 2:** Check status:
```bash
./dev status
```

Both will show you the current SSH command. Copy and run it on your Mac.

## Make It Seamless (No Password)

### 1. Copy your SSH key to server:
```bash
ssh-copy-id starscream@10.88.111.17
```

### 2. Add to `~/.ssh/config` on your Mac:
```
Host cybertron
    HostName 10.88.111.17
    User starscream

Host cybertron-remote
    HostName https://casino-oclc-queen-else.trycloudflare.com
    User starscream
    ProxyCommand cloudflared access tcp --hostname %h
```

Now just type:
```bash
ssh cybertron           # local
ssh cybertron-remote    # external
```

Done.
