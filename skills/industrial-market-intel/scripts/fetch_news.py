#!/usr/bin/env python3
"""
fetch_news.py — Industrial Market Intelligence News Fetcher
Part of the industrial-market-intel OpenClaw skill.

Searches for market news across water treatment, specialty chemicals,
and related industrial sectors using web search APIs.

Usage:
    python fetch_news.py --topics "ZLD,OARO,ion exchange" --regions "India" --days 1
    python fetch_news.py --topics "ZLD" --competitors "Veolia,Ion Exchange India" --days 7 --output /tmp/news.json
"""

import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Fetch industrial market intelligence news")
    parser.add_argument("--topics", default="water treatment,ZLD,OARO,ion exchange resins,RO membranes",
                        help="Comma-separated list of topics to search")
    parser.add_argument("--regions", default="India,Global",
                        help="Comma-separated list of geographic regions to filter")
    parser.add_argument("--competitors", default="",
                        help="Comma-separated competitor names for focused watch")
    parser.add_argument("--days", type=int, default=1,
                        help="Lookback window in days (1=daily, 7=weekly)")
    parser.add_argument("--output", default="/tmp/raw_news.json",
                        help="Output file path for the JSON results")
    parser.add_argument("--max-results", type=int, default=30,
                        help="Maximum number of results to return")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

def build_queries(topics: list[str], regions: list[str], competitors: list[str], days: int) -> list[dict]:
    """Build a list of search query objects."""
    queries = []
    date_label = "today" if days == 1 else f"last {days} days"

    # Topic + region queries
    for topic in topics:
        for region in regions:
            q = f"{topic} {region} {date_label} news" if region.lower() != "global" else f"{topic} {date_label} news"
            queries.append({"query": q, "category": categorize(topic), "topic": topic, "region": region})

    # Competitor-specific queries
    for competitor in competitors:
        queries.append({
            "query": f"{competitor} water treatment announcement {date_label}",
            "category": "Competitor Activity",
            "topic": competitor,
            "region": "Global"
        })
        queries.append({
            "query": f"{competitor} contract win project award {date_label}",
            "category": "Contracts & Projects",
            "topic": competitor,
            "region": "Global"
        })

    # Regulatory queries
    for region in regions:
        if region.lower() != "global":
            queries.append({
                "query": f"industrial wastewater regulation policy {region} {date_label}",
                "category": "Regulatory Updates",
                "topic": "regulatory",
                "region": region
            })

    return queries


def categorize(topic: str) -> str:
    """Assign a default category based on topic keywords."""
    topic_lower = topic.lower()
    if any(k in topic_lower for k in ["regulation", "policy", "standard", "guideline", "bpcb", "cpcb", "epa"]):
        return "Regulatory Updates"
    if any(k in topic_lower for k in ["oaro", "zld", "membrane", "ion exchange", "mbr", "edi"]):
        return "Technology Developments"
    if any(k in topic_lower for k in ["funding", "investment", "acquisition", "merger", "ipo", "series"]):
        return "M&A / Funding"
    if any(k in topic_lower for k in ["contract", "order", "project", "tender", "bid", "award"]):
        return "Contracts & Projects"
    return "Market Trends"


def relevance_score(item: dict, topics: list[str], regions: list[str]) -> float:
    """Score a news item 0.0–1.0 based on keyword relevance."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    score = 0.0

    # Topic keyword hits
    topic_keywords = " ".join(topics).lower().split()
    hits = sum(1 for kw in topic_keywords if kw in text and len(kw) > 3)
    score += min(hits * 0.15, 0.6)

    # Region hits
    region_hits = sum(1 for r in regions if r.lower() in text)
    score += min(region_hits * 0.1, 0.2)

    # Recency boost (already filtered by date range, so slight boost for newer)
    score += 0.1

    # Penalise generic/unrelated content
    noise_words = ["opinion", "lifestyle", "sports", "cricket", "bollywood", "recipe"]
    if any(n in text for n in noise_words):
        score -= 0.4

    return round(max(0.0, min(score, 1.0)), 2)


# ---------------------------------------------------------------------------
# Mock search backend (replace with real API integration)
# ---------------------------------------------------------------------------

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search for news using a public search endpoint.

    For production use, replace this with one of:
    - SerpAPI (https://serpapi.com) with SERP_API_KEY env var
    - Brave Search API with BRAVE_SEARCH_KEY env var
    - NewsAPI (https://newsapi.org) with NEWS_API_KEY env var
    - OpenClaw's built-in browser tool via the gateway

    This implementation uses a lightweight RSS/headline approach as a demo.
    """
    import os
    import time

    results = []

    # --- Option A: NewsAPI (if key is set) ---
    news_api_key = os.environ.get("NEWS_API_KEY", "")
    if news_api_key:
        try:
            encoded_q = urllib.parse.quote_plus(query)
            url = f"https://newsapi.org/v2/everything?q={encoded_q}&sortBy=publishedAt&pageSize={max_results}&apiKey={news_api_key}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                for article in data.get("articles", []):
                    results.append({
                        "title": article.get("title", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", ""),
                        "date": article.get("publishedAt", "")[:10],
                        "summary": article.get("description", "") or article.get("content", ""),
                        "relevance_score": 0.0  # will be scored later
                    })
            return results
        except Exception as e:
            print(f"[NewsAPI] Error: {e}")

    # --- Option B: Brave Search API (if key is set) ---
    brave_key = os.environ.get("BRAVE_SEARCH_KEY", "")
    if brave_key:
        try:
            encoded_q = urllib.parse.quote_plus(query)
            url = f"https://api.search.brave.com/res/v1/news/search?q={encoded_q}&count={max_results}&freshness=pd"
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "X-Subscription-Token": brave_key
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "source": item.get("meta_url", {}).get("hostname", ""),
                        "url": item.get("url", ""),
                        "date": item.get("age", ""),
                        "summary": item.get("description", ""),
                        "relevance_score": 0.0
                    })
            return results
        except Exception as e:
            print(f"[Brave] Error: {e}")

    # --- Option C: Demo/fallback — return placeholder items ---
    print(f"[search_web] No API key found. Running in demo mode for query: '{query}'")
    print("  Set NEWS_API_KEY or BRAVE_SEARCH_KEY environment variable for live results.")
    return [
        {
            "title": f"[DEMO] Sample result for: {query}",
            "source": "Demo Source",
            "url": "https://example.com",
            "date": datetime.today().strftime("%Y-%m-%d"),
            "summary": "This is a placeholder result. Configure NEWS_API_KEY or BRAVE_SEARCH_KEY for live data.",
            "relevance_score": 0.5
        }
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    regions = [r.strip() for r in args.regions.split(",") if r.strip()]
    competitors = [c.strip() for c in args.competitors.split(",") if c.strip()] if args.competitors else []

    print(f"[fetch_news] Topics: {topics}")
    print(f"[fetch_news] Regions: {regions}")
    print(f"[fetch_news] Competitors: {competitors}")
    print(f"[fetch_news] Lookback: {args.days} day(s)")

    queries = build_queries(topics, regions, competitors, args.days)
    print(f"[fetch_news] Running {len(queries)} queries...")

    seen_urls = set()
    all_results = []

    for q in queries:
        items = search_web(q["query"], max_results=5)
        for item in items:
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            item["category"] = q["category"]
            item["matched_topic"] = q["topic"]
            item["matched_region"] = q["region"]
            item["relevance_score"] = relevance_score(item, topics, regions)
            all_results.append(item)

    # Sort by relevance score descending
    all_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Truncate to max results
    all_results = all_results[:args.max_results]

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"[fetch_news] {len(all_results)} results written to {args.output}")


if __name__ == "__main__":
    main()
