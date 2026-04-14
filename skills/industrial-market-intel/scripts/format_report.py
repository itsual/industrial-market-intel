#!/usr/bin/env python3
"""
format_report.py — Market Intelligence Report Formatter
Part of the industrial-market-intel OpenClaw skill.

Reads the JSON news items from fetch_news.py and produces a structured
markdown briefing report ready for delivery or saving to workspace.

Usage:
    python format_report.py --input /tmp/raw_news.json --output /tmp/market_briefing.md --period Daily
    python format_report.py --input /tmp/raw_news.json --output /tmp/market_briefing.md --period Weekly --date 2026-04-14
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime


CATEGORIES = [
    "Market Trends",
    "Competitor Activity",
    "Technology Developments",
    "Regulatory Updates",
    "Contracts & Projects",
    "M&A / Funding",
]

PRIORITY_THRESHOLD = 0.65  # Items above this score are flagged as high priority

CATEGORY_ICONS = {
    "Market Trends": "📈",
    "Competitor Activity": "🏭",
    "Technology Developments": "⚙️",
    "Regulatory Updates": "🏛️",
    "Contracts & Projects": "📋",
    "M&A / Funding": "💰",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Format market intelligence report")
    parser.add_argument("--input", default="/tmp/raw_news.json", help="Input JSON file from fetch_news.py")
    parser.add_argument("--output", default="/tmp/market_briefing.md", help="Output markdown file path")
    parser.add_argument("--period", default="Daily", choices=["Daily", "Weekly"], help="Briefing period")
    parser.add_argument("--date", default=datetime.today().strftime("%Y-%m-%d"), help="Report date (YYYY-MM-DD)")
    parser.add_argument("--min-score", type=float, default=0.3, help="Minimum relevance score to include")
    return parser.parse_args()


def load_news(path: str, min_score: float) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return [i for i in items if i.get("relevance_score", 0) >= min_score]


def group_by_category(items: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for item in items:
        cat = item.get("category", "Market Trends")
        if cat not in CATEGORIES:
            cat = "Market Trends"
        grouped[cat].append(item)
    return grouped


def build_executive_summary(grouped: dict, period: str, date: str) -> str:
    total = sum(len(v) for v in grouped.values())
    high_priority = sum(
        1 for items in grouped.values()
        for item in items
        if item.get("relevance_score", 0) >= PRIORITY_THRESHOLD
    )
    active_categories = [cat for cat in CATEGORIES if grouped.get(cat)]

    lines = [
        f"**{period} scan complete** — {total} items tracked across "
        f"{len(active_categories)} categories for {date}.",
    ]
    if high_priority:
        lines.append(f"**{high_priority} high-priority item(s)** flagged for immediate attention.")
    else:
        lines.append("No high-priority items flagged this period.")

    top_items = sorted(
        [item for items in grouped.values() for item in items],
        key=lambda x: x.get("relevance_score", 0),
        reverse=True
    )[:3]
    if top_items:
        lines.append("\n**Top developments:**")
        for item in top_items:
            lines.append(f"- {item['title']} *(score: {item['relevance_score']})*")

    return "\n".join(lines)


def format_item(item: dict) -> str:
    score = item.get("relevance_score", 0)
    priority_flag = "🔴 **HIGH PRIORITY** — " if score >= PRIORITY_THRESHOLD else ""
    title = item.get("title", "Untitled")
    source = item.get("source", "Unknown source")
    url = item.get("url", "")
    date = item.get("date", "")
    summary = item.get("summary", "")

    link = f"[{source}]({url})" if url else source
    header = f"#### {priority_flag}{title}"
    meta = f"*{link} · {date} · Relevance: {score}*"
    body = f"{summary}" if summary else ""

    return "\n".join(filter(None, [header, meta, body]))


def build_section(category: str, items: list[dict]) -> str:
    icon = CATEGORY_ICONS.get(category, "📌")
    lines = [f"\n### {icon} {category}\n"]
    if not items:
        lines.append("*No significant updates this period.*")
    else:
        for item in sorted(items, key=lambda x: x.get("relevance_score", 0), reverse=True):
            lines.append(format_item(item))
            lines.append("")
    return "\n".join(lines)


def format_report(items: list[dict], period: str, date: str, min_score: float) -> str:
    filtered = [i for i in items if i.get("relevance_score", 0) >= min_score]
    grouped = group_by_category(filtered)

    report_lines = [
        f"# Industrial Market Intelligence Briefing",
        f"## {period} Report — {date}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        build_executive_summary(grouped, period, date),
        "",
        "---",
    ]

    for category in CATEGORIES:
        section_items = grouped.get(category, [])
        report_lines.append(build_section(category, section_items))
        report_lines.append("---")

    report_lines += [
        "",
        "---",
        f"*Generated by [industrial-market-intel](https://github.com/itsual/industrial-market-intel) "
        f"OpenClaw skill · {datetime.now().strftime('%Y-%m-%d %H:%M IST')}*",
        "",
        "> **Sectors covered:** Water treatment (ZLD, OARO, RO, ion exchange, MBR) · "
        "Specialty chemicals · Industrial wastewater · Regulatory (India, EU, Global)",
    ]

    return "\n".join(report_lines)


def main():
    args = parse_args()

    print(f"[format_report] Loading news from {args.input}")
    items = load_news(args.input, min_score=0.0)  # load all, filter inside format_report
    print(f"[format_report] {len(items)} items loaded")

    report = format_report(items, args.period, args.date, args.min_score)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[format_report] Report written to {args.output} ({len(report)} chars)")


if __name__ == "__main__":
    main()
