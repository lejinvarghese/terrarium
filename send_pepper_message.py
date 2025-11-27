#!/usr/bin/env python
"""Send a Pepper message via Telegram."""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GIRLFRIEND_TELEGRAM_CHAT_ID = os.getenv("GIRLFRIEND_TELEGRAM_CHAT_ID")

message = """[Pepper] 🌙✨ TRIP EVE HYPE! ✨🌙

Okay bestie, tomorrow's the BIG DAY! Let's break this down into bite-sized wins so your brain doesn't spiral:

**🎒 PACKING MICRO-MISSIONS:**
- [ ] Grab your bag (just find it, that's step 1!)
- [ ] Toss in underwear + socks (3 sets? 4? You know the vibe)
- [ ] Outfits: pick 2-3, roll 'em up
- [ ] Toiletries pouch (toothbrush, face stuff, whatever makes you feel human)
- [ ] Chargers (phone + any other tech babies)
- [ ] Meds + any vitamins (IMPORTANT ONE!)
- [ ] Comfy travel outfit laid out for AM

**🚗 TOMORROW MORNING SURVIVAL KIT:**
- [ ] Set 2 alarms (your brain will try to negotiate with the first one 😏)
- [ ] Water bottle filled tonight
- [ ] Snacks within arm's reach for the road
- [ ] Check weather for destination (I can grab this if you want!)

**✨ BONUS LEVEL:**
- [ ] Check you have your ID/wallet/keys (the holy trinity!)
- [ ] Phone playlist downloaded for offline jamming

---

**🎵 VIBE RECOMMENDATION:**
Wanna make packing feel less like a chore? I've got the PERFECT high-energy playlist vibe for you! Want me to queue something up on Spotify to keep you moving? Just say the word! 🎧🔥

You've got this! Each checkbox is a mini-win. Let's goooo! 💪✨

P.S. Reply back when you knock out a few tasks - I wanna celebrate those wins with you! 🎉"""

# Send via Telegram Bot API
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
data = {
    "chat_id": GIRLFRIEND_TELEGRAM_CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("✅ Message sent successfully!")
else:
    print(f"❌ Failed to send message: {response.status_code}")
    print(response.text)
