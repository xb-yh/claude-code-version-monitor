#!/usr/bin/env python3
"""
Claude Code version monitor.

Checks the npm registry for updates to @anthropic-ai/claude-code and sends a
notification to a Feishu (Lark) group bot when a new version is published.

Environment variables:
    FEISHU_WEBHOOK_URL  Webhook URL of the Feishu group bot.
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests


PACKAGE_NAME = "@anthropic-ai/claude-code"
NPM_REGISTRY_URL = f"https://registry.npmjs.org/{PACKAGE_NAME.replace('/', '%2F')}"
STATE_FILE = "state.json"


def fetch_latest_version():
    """Fetch the latest published version and its publish time from npm."""
    resp = requests.get(
        NPM_REGISTRY_URL,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    latest = data.get("dist-tags", {}).get("latest")
    if not latest:
        raise RuntimeError("Could not find 'latest' dist-tag in npm registry response")

    version_info = data.get("versions", {}).get(latest, {})
    published = version_info.get("time") or data.get("time", {}).get(latest)
    return latest, published


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def send_feishu(webhook_url, version, published):
    """Send a text notification to the Feishu webhook."""
    lines = [
        f"🚀 Claude Code 新版本发布：{version}",
        "",
        f"📦 包名：{PACKAGE_NAME}",
        f"🏷️ 版本：{version}",
        f"🕒 发布时间：{published or '未知'}",
        f"🔗 npm 页面：https://www.npmjs.com/package/{PACKAGE_NAME.replace('/', '%2F')}",
        "",
        "请及时更新你的 Claude Code CLI。",
    ]
    payload = {
        "msg_type": "text",
        "content": {"text": "\n".join(lines)},
    }
    resp = requests.post(webhook_url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")
    if not webhook_url:
        print("Error: FEISHU_WEBHOOK_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching latest version of {PACKAGE_NAME} ...")
    latest_version, published = fetch_latest_version()
    print(f"Latest version: {latest_version} (published: {published})")

    state = load_state()
    last_version = state.get("last_version")

    if last_version is None:
        print(f"No previous state found. Starting monitoring at {latest_version}.")
        save_state({
            "last_version": latest_version,
            "last_checked": datetime.now(timezone.utc).isoformat(),
        })
        return

    if last_version == latest_version:
        print(f"No update. Current version remains {latest_version}.")
        return

    print(f"Update detected: {last_version} -> {latest_version}")
    send_feishu(webhook_url, latest_version, published)
    print("Feishu notification sent.")

    save_state({
        "last_version": latest_version,
        "last_published": published,
        "last_notified": datetime.now(timezone.utc).isoformat(),
        "previous_version": last_version,
    })


if __name__ == "__main__":
    main()
