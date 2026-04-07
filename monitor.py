#!/usr/bin/env python3
"""
Beget VPS Kazakhstan (kz1) Availability Monitor.

Checks if the Kazakhstan datacenter is available on beget.com/ru/vps.
Sends a Telegram notification when it becomes available.

How it works:
  1. Fetches the main VPS page HTML
  2. Extracts the Nuxt _payload.json URL from the HTML
  3. Fetches the payload (contains cloudRegionList with availability flags)
  4. Parses devalue format and checks kz1.available

Environment variables:
  TELEGRAM_BOT_TOKEN - Telegram bot token
  TELEGRAM_CHAT_ID   - Telegram chat ID to send notifications to
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import time

import requests

BEGET_URL = "https://beget.com/ru/vps"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5",
}


def send_telegram(message: str) -> None:
    """Send a message via Telegram bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        sys.exit(1)
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
        timeout=10,
    )
    resp.raise_for_status()
    print("Telegram: sent")


def fetch_payload_url(html: str) -> str | None:
    """Extract _payload.json URL from page HTML."""
    matches = re.findall(r'(https://assets-site\.beget\.com/[^\s"]+_payload\.json[^\s"]*)', html)
    return matches[0] if matches else None


def fetch_payload(html: str) -> list | None:
    """Fetch the Nuxt _payload.json referenced in the HTML page."""
    url = fetch_payload_url(html)
    if not url:
        print("ERROR: _payload.json URL not found in HTML")
        return None
    print(f"Payload URL: {url}")
    resp = requests.get(url, timeout=30, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return data
    return None


def check_kz1(data: list) -> bool | None:
    """
    Check kz1 availability in devalue-formatted payload data.

    Devalue format: JSON array where object values are integer
    index references into the same array.
    E.g. {"id": 1166, "available": 180} means:
      - data[1166] = "kz1"      (the id value)
      - data[180]  = False       (the available value)
    """
    for item in data:
        if not isinstance(item, dict) or "id" not in item or "available" not in item:
            continue
        id_ref = item["id"]
        if not isinstance(id_ref, int) or not (0 <= id_ref < len(data)):
            continue
        if data[id_ref] != "kz1":
            continue
        # Found the kz1 region object
        avail_ref = item["available"]
        if isinstance(avail_ref, bool):
            return avail_ref
        if isinstance(avail_ref, int) and 0 <= avail_ref < len(data):
            return data[avail_ref]
        return None
    return None


def main():
    # Random delay 0-120s to vary request timing
    delay = random.randint(0, 120)
    print(f"Delay: {delay}s")
    time.sleep(delay)

    print(f"Checking {BEGET_URL}")
    try:
        html_resp = requests.get(BEGET_URL, timeout=30, headers=HEADERS)
        html_resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Fetch error: {e}")
        sys.exit(1)

    data = fetch_payload(html_resp.text)
    if data is None:
        send_telegram(
            "\u26a0\ufe0f <b>Beget Monitor</b>\n\n"
            "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c payload.\n"
            "\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u0441\u0430\u0439\u0442\u0430 \u043c\u043e\u0433\u043b\u0430 \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u044c\u0441\u044f.\n"
            f"\u041f\u0440\u043e\u0432\u0435\u0440\u044c \u0432\u0440\u0443\u0447\u043d\u0443\u044e: {BEGET_URL}"
        )
        sys.exit(1)

    available = check_kz1(data)
    if available is None:
        send_telegram(
            "\u26a0\ufe0f <b>Beget Monitor</b>\n\n"
            "kz1 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d \u0432 payload.\n"
            "\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u043c\u043e\u0433\u043b\u0430 \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u044c\u0441\u044f.\n"
            f"\u041f\u0440\u043e\u0432\u0435\u0440\u044c \u0432\u0440\u0443\u0447\u043d\u0443\u044e: {BEGET_URL}"
        )
        sys.exit(1)

    print(f"kz1 available = {available}")

    if available:
        send_telegram(
            "\ud83c\udf89 <b>\u041a\u0430\u0437\u0430\u0445\u0441\u0442\u0430\u043d (kz1) \u0414\u041e\u0421\u0422\u0423\u041f\u0415\u041d \u043d\u0430 Beget!</b>\n\n"
            "\u0421\u0435\u0440\u0432\u0435\u0440 \u0432 \u041a\u0430\u0437\u0430\u0445\u0441\u0442\u0430\u043d\u0435 \u043f\u043e\u044f\u0432\u0438\u043b\u0441\u044f \u0432 \u0441\u043f\u0438\u0441\u043a\u0435 VPS.\n\n"
            f"\ud83d\udc49 {BEGET_URL}"
        )
    else:
        print("kz1 not yet available")


if __name__ == "__main__":
    main()
