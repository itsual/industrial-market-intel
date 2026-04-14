# 🦞 Industrial Market Intelligence Agent

An [OpenClaw](https://openclaw.ai) skill that delivers automated market intelligence briefings for **water treatment**, **specialty chemicals**, and **process industries** — straight to your WhatsApp, Telegram, Slack, or Discord.

> Built as a demonstration of domain-specific OpenClaw skills for B2B industrial markets.

---

## What It Does

- **Monitors** news, competitor activity, regulatory changes, and M&A across water treatment and specialty chemicals sectors
- **Filters & scores** results by relevance to your configured topics and regions
- **Structures** the output into a clean markdown briefing with categorized sections
- **Delivers** via your preferred messaging channel or saves to your OpenClaw workspace
- **Schedules** daily or weekly automated runs via OpenClaw's built-in cron

---

## Sectors Covered

| Domain | Sub-technologies |
|--------|-----------------|
| Water Treatment | ZLD, OARO, RO membranes, Ion Exchange, MBR, EDI, UF |
| Specialty Chemicals | Antiscalants, coagulants, biocides, corrosion inhibitors, IX resins |
| Regulatory | CPCB, CGWA, EPA, EU WFD, BIS standards |
| End-use Industries | Power, pharma, refinery, textiles, steel, food & beverage, data centers |

**Default geographies:** India, Southeast Asia, Middle East, Europe, Global

---

## Sample Output

```
# Industrial Market Intelligence Briefing
## Daily Report — 2026-04-14

---

## Executive Summary

Daily scan complete — 18 items tracked across 5 categories for 2026-04-14.
2 high-priority items flagged for immediate attention.

Top developments:
- Veolia wins ₹350 Cr ZLD contract in Maharashtra textile cluster (score: 0.85)
- CPCB issues revised ZLD compliance timeline for textile sector (score: 0.78)
- LANXESS expands ion exchange resin capacity in India (score: 0.71)

---

### 📈 Market Trends
...

### 🏭 Competitor Activity
#### 🔴 HIGH PRIORITY — Veolia wins ₹350 Cr ZLD contract in Maharashtra textile cluster
*Business Standard · 2026-04-13 · Relevance: 0.85*
Veolia Water Technologies has secured a major ZLD project...

### 🏛️ Regulatory Updates
#### 🔴 HIGH PRIORITY — CPCB issues revised ZLD compliance timeline for textile sector
...
```

---

## Installation

### Prerequisites

- [OpenClaw](https://openclaw.ai) installed and running (`openclaw onboard`)
- Python 3.10+
- A news API key (optional but recommended for live data):
  - [NewsAPI](https://newsapi.org) — free tier available
  - [Brave Search API](https://api.search.brave.com) — free tier available

### Install the Skill

```bash
# Clone the repo
git clone https://github.com/itsual/industrial-market-intel.git
cd industrial-market-intel

# Copy skill to OpenClaw workspace
cp -r skills/industrial-market-intel ~/.openclaw/workspace/skills/

# Verify skill is detected
openclaw skills list
```

### Configure

Edit `~/.openclaw/workspace/skills/industrial-market-intel/config.json` (create if not present):

```json
{
  "sectors": ["water treatment", "ZLD", "OARO", "ion exchange resins", "RO membranes"],
  "regions": ["India", "Southeast Asia", "Global"],
  "competitors": ["Veolia", "Ion Exchange India", "Thermax", "VA Tech Wabag"],
  "delivery_channel": "telegram",
  "schedule": "daily",
  "schedule_time": "07:00"
}
```

### Set API Keys (for live news)

```bash
# For NewsAPI
export NEWS_API_KEY="your_key_here"

# Or for Brave Search
export BRAVE_SEARCH_KEY="your_key_here"

# For direct Telegram delivery (optional — OpenClaw handles this via gateway too)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

---

## Usage

### On-Demand Briefing (via OpenClaw chat)

Send any of these to your OpenClaw assistant:

```
"Give me today's water treatment market news"
"What's new in ZLD and OARO this week?"
"Run a competitor watch on Veolia and Ion Exchange India"
"Any new regulatory updates on industrial wastewater in India?"
```

### Run Scripts Directly

```bash
cd ~/.openclaw/workspace/skills/industrial-market-intel

# Step 1: Fetch news
python scripts/fetch_news.py \
  --topics "ZLD,OARO,ion exchange,RO membranes" \
  --regions "India,Global" \
  --days 1 \
  --output /tmp/raw_news.json

# Step 2: Format report
python scripts/format_report.py \
  --input /tmp/raw_news.json \
  --output /tmp/market_briefing.md \
  --period Daily

# Step 3: Send briefing
python scripts/send_briefing.py \
  --input /tmp/market_briefing.md \
  --channel telegram \
  --summary-only  # shorter message for chat
```

### Set Up Scheduled Briefings

Tell your OpenClaw assistant:

```
"Schedule a daily market intel briefing every morning at 7am"
"Set up a weekly water treatment market summary every Monday at 8am"
```

---

## Project Structure

```
industrial-market-intel/
├── README.md
└── skills/
    └── industrial-market-intel/
        ├── SKILL.md                    ← OpenClaw skill definition
        ├── scripts/
        │   ├── fetch_news.py           ← News search & collection
        │   ├── format_report.py        ← Markdown report formatter
        │   └── send_briefing.py        ← Channel delivery handler
        └── references/
            ├── sectors.md              ← Tracked sectors & keywords
            └── competitors.md          ← Competitor watchlist
```

---

## Customization

### Add Your Own Sectors

Edit `references/sectors.md` to add industry-specific keywords relevant to your segment.

### Extend the Competitor List

Edit `references/competitors.md` to add or remove companies from the watchlist.

### Add New Delivery Channels

`send_briefing.py` supports Telegram, Slack, Discord, and WhatsApp out of the box. Add a new `send_<channel>` function to extend it.

### Use a Different News Source

`fetch_news.py` is designed to swap backends easily. Replace the `search_web()` function body with your preferred news API (SerpAPI, Bing News, GNews, etc.).

---

## Why OpenClaw?

OpenClaw's local-first, skill-based architecture is ideal for professional intelligence workflows:

- **Privacy** — all data stays on your machine; no cloud storage of your competitive intelligence
- **Persistence** — memory and reports persist across sessions in your workspace
- **Scheduling** — native cron support for automated recurring briefings
- **Multi-channel** — deliver to WhatsApp, Telegram, Slack, or Discord without changing the skill

---

## Contributing

PRs welcome. Ideas for improvement:

- [ ] Add RSS feed ingestion for key industry publications (GWI, Water & Wastes Digest)
- [ ] Integrate CPCB/regulatory portal scraping for India-specific regulatory alerts
- [ ] Add sentiment scoring for competitor news
- [ ] Build a weekly trend chart using matplotlib
- [ ] Add email delivery via SMTP/SendGrid

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Author

Built by [@itsual](https://github.com/itsual) as a demonstration of domain-specific OpenClaw skills for B2B industrial markets.

*Expertise: Water treatment technology (ZLD, OARO, ion exchange, RO membranes), specialty chemicals, industrial strategy.*
