#!/usr/bin/env python3
"""Extract a GETTR post's og:video URL from HTML meta tags.

Usage:
  python3 extract_gettr_og_video.py <gettr_post_url>

Prints:
  The best candidate video URL (one line to stdout).

Exit codes:
  0: success
  1: no video found (post may be text/image only)
  2: usage error or invalid URL
  3: network error after retries

Implementation notes:
- Uses only stdlib.
- Looks for (in order): og:video:secure_url, og:video:url, og:video
- Retries up to 3 times with exponential backoff on network errors.
"""

from __future__ import annotations

import html
import re
import sys
import time
import urllib.request
from urllib.error import HTTPError, URLError

META_RE = re.compile(
    r"<meta\s+[^>]*?(?:property|name)\s*=\s*['\"](?P<key>og:video(?::secure_url|:url)?)['\"][^>]*?>",
    re.IGNORECASE,
)
CONTENT_RE = re.compile(r"content\s*=\s*['\"](?P<val>[^'\"]+)['\"]", re.IGNORECASE)

PREF_ORDER = ["og:video:secure_url", "og:video:url", "og:video"]

MAX_RETRIES = 3
BACKOFF_BASE = 1.5  # seconds


def fetch(url: str) -> str:
    """Fetch URL with retry and exponential backoff."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    )

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            # Best effort decode
            for enc in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    return data.decode(enc)
                except Exception:
                    pass
            return data.decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = BACKOFF_BASE ** (attempt + 1)
                print(f"[retry] Attempt {attempt + 1} failed: {e}. Retrying in {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)

    raise last_error or RuntimeError("fetch failed")


def extract(html_text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for m in META_RE.finditer(html_text):
        tag = m.group(0)
        key = m.group("key").lower()
        cm = CONTENT_RE.search(tag)
        if not cm:
            continue
        val = html.unescape(cm.group("val")).strip()
        if val and key not in found:
            found[key] = val
    return found


def detect_post_type(html_text: str) -> str:
    """Detect the type of GETTR post from og:type or content hints."""
    # Check og:type
    og_type_match = re.search(
        r'<meta\s+[^>]*?(?:property|name)\s*=\s*[\'"]og:type[\'"][^>]*?content\s*=\s*[\'"]([^"\']+)[\'"]',
        html_text,
        re.IGNORECASE,
    )
    if og_type_match:
        og_type = og_type_match.group(1).lower()
        if "video" in og_type:
            return "video"
        if "image" in og_type:
            return "image"
        if "article" in og_type:
            return "article"
    return "unknown"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: extract_gettr_og_video.py <gettr_post_url>", file=sys.stderr)
        return 2

    url = argv[1]
    if not (url.startswith("http://") or url.startswith("https://")):
        print("URL must start with http:// or https://", file=sys.stderr)
        return 2

    try:
        html_text = fetch(url)
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"[error] Failed to fetch URL after {MAX_RETRIES} attempts: {e}", file=sys.stderr)
        return 3

    found = extract(html_text)

    for key in PREF_ORDER:
        v = found.get(key)
        if v:
            print(v)
            return 0

    # No video found - provide helpful diagnostics
    post_type = detect_post_type(html_text)
    print("[error] No og:video meta tag found.", file=sys.stderr)

    if post_type == "image":
        print("[hint] This appears to be an image post, not a video.", file=sys.stderr)
    elif post_type == "article":
        print("[hint] This appears to be a text/article post, not a video.", file=sys.stderr)
    else:
        print("[hint] This post may not contain a video, or it may require authentication.", file=sys.stderr)

    if found:
        print("Found meta keys: " + ", ".join(sorted(found.keys())), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
