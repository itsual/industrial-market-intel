#!/usr/bin/env python3
"""
send_briefing.py — Briefing Delivery Script
Part of the industrial-market-intel OpenClaw skill.

Reads the formatted markdown report and sends it to the configured
messaging channel via OpenClaw's channel integrations.

Supported channels: telegram, slack, discord, whatsapp
Falls back to saving to workspace if no channel is configured.

Usage:
    python send_briefing.py --input /tmp/market_briefing.md --channel telegram
    python send_briefing.py --input /tmp/market_briefing.md --channel slack --workspace ~/openclaw/workspace
"""

import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Send market intelligence briefing")
    parser.add_argument("--input", default="/tmp/market_briefing.md", help="Input markdown report file")
    parser.add_argument("--channel", default="workspace",
                        choices=["telegram", "whatsapp", "slack", "discord", "workspace"],
                        help="Delivery channel")
    parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"),
                        help="OpenClaw workspace root path")
    parser.add_argument("--summary-only", action="store_true",
                        help="Send only the executive summary (shorter message for chat channels)")
    return parser.parse_args()


def read_report(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_summary(report: str) -> str:
    """Extract the Executive Summary section from the full report."""
    lines = report.split("\n")
    in_summary = False
    summary_lines = []
    for line in lines:
        if "## Executive Summary" in line:
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## ") or line.strip() == "---":
                break
            summary_lines.append(line)
    return "\n".join(summary_lines).strip()


def truncate_for_chat(text: str, max_chars: int = 4000) -> str:
    """Truncate message to fit chat platform limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 100] + "\n\n*[truncated — full report saved to workspace]*"


def save_to_workspace(report: str, workspace: str, input_path: str) -> str:
    """Save report to the OpenClaw workspace briefings directory."""
    briefings_dir = Path(workspace) / "briefings"
    briefings_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.today().strftime("%Y-%m-%d")
    dest = briefings_dir / f"market_intel_{date_str}.md"
    dest.write_text(report, encoding="utf-8")
    print(f"[send_briefing] Report saved to {dest}")
    return str(dest)


def send_telegram(report: str, summary_only: bool):
    """
    Send report via Telegram using OpenClaw's Telegram channel.

    OpenClaw handles the actual Telegram delivery via its gateway.
    This script prepares the message and writes it to a handoff file
    that the OpenClaw agent picks up for delivery.

    For direct Telegram Bot API usage, set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.
    """
    import urllib.request

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    message = extract_summary(report) if summary_only else report

    if bot_token and chat_id:
        # Direct Telegram Bot API delivery
        payload = {
            "chat_id": chat_id,
            "text": truncate_for_chat(message, 4096),
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                if result.get("ok"):
                    print("[send_briefing] Telegram message sent successfully")
                else:
                    print(f"[send_briefing] Telegram error: {result}")
        except Exception as e:
            print(f"[send_briefing] Telegram delivery failed: {e}")
    else:
        # Write to OpenClaw handoff file for gateway delivery
        handoff = {
            "channel": "telegram",
            "message": truncate_for_chat(message, 4096),
            "timestamp": datetime.now().isoformat()
        }
        handoff_path = "/tmp/openclaw_send.json"
        with open(handoff_path, "w", encoding="utf-8") as f:
            json.dump(handoff, f, indent=2)
        print(f"[send_briefing] Telegram handoff written to {handoff_path}")
        print("  OpenClaw gateway will deliver via configured Telegram channel.")
        print("  Alternatively, set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID for direct delivery.")


def send_slack(report: str, summary_only: bool):
    """Send report via Slack webhook."""
    import urllib.request

    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    message = extract_summary(report) if summary_only else report

    if webhook_url:
        payload = {"text": truncate_for_chat(message, 3000)}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15):
                print("[send_briefing] Slack message sent successfully")
        except Exception as e:
            print(f"[send_briefing] Slack delivery failed: {e}")
    else:
        print("[send_briefing] SLACK_WEBHOOK_URL not set. Writing handoff for OpenClaw gateway.")
        handoff = {"channel": "slack", "message": truncate_for_chat(message, 3000)}
        with open("/tmp/openclaw_send.json", "w") as f:
            json.dump(handoff, f)


def send_discord(report: str, summary_only: bool):
    """Send report via Discord webhook."""
    import urllib.request

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    message = extract_summary(report) if summary_only else report

    if webhook_url:
        payload = {"content": truncate_for_chat(message, 2000)}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15):
                print("[send_briefing] Discord message sent successfully")
        except Exception as e:
            print(f"[send_briefing] Discord delivery failed: {e}")
    else:
        print("[send_briefing] DISCORD_WEBHOOK_URL not set.")


def main():
    args = parse_args()

    print(f"[send_briefing] Reading report from {args.input}")
    report = read_report(args.input)
    print(f"[send_briefing] Report size: {len(report)} characters")

    # Always save to workspace as archive
    saved_path = save_to_workspace(report, args.workspace, args.input)

    # Deliver to requested channel
    if args.channel == "telegram":
        send_telegram(report, args.summary_only)
    elif args.channel == "slack":
        send_slack(report, args.summary_only)
    elif args.channel == "discord":
        send_discord(report, args.summary_only)
    elif args.channel == "whatsapp":
        # WhatsApp delivery handled by OpenClaw gateway
        message = extract_summary(report) if args.summary_only else report
        handoff = {"channel": "whatsapp", "message": truncate_for_chat(message, 4096)}
        with open("/tmp/openclaw_send.json", "w") as f:
            json.dump(handoff, f)
        print("[send_briefing] WhatsApp handoff written. OpenClaw gateway will deliver.")
    elif args.channel == "workspace":
        print(f"[send_briefing] Report saved to workspace only: {saved_path}")

    print("[send_briefing] Done.")


if __name__ == "__main__":
    main()
