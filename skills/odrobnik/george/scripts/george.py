#!/usr/bin/env python3
"""
George Banking Automation - Erste Bank/Sparkasse Austria

Modular script for:
- Listing accounts
- Downloading PDF statements (with booking receipts)
- Downloading data exports (CAMT53/MT940)
- Downloading transaction exports (CSV/JSON/OFX/XLSX)

Requires phone approval via George app during login.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl


def _load_dotenv(path: Path) -> None:
    """Best-effort .env loader (KEY=VALUE lines)."""
    try:
        if not path.exists():
            return
        for line in path.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        return


# Fast path: allow `--help` without requiring Playwright.
if "-h" in sys.argv or "--help" in sys.argv:
    sync_playwright = None  # type: ignore[assignment]
    PlaywrightTimeout = Exception  # type: ignore[assignment]
else:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("ERROR: playwright not installed. Run: pipx install playwright && playwright install chromium")
        sys.exit(1)

def _default_state_dir() -> Path:
    return Path.home() / ".clawdbot" / "george"


# Runtime state dir (override via --dir or GEORGE_DIR)
STATE_DIR: Path = _default_state_dir()
CONFIG_PATH: Path = STATE_DIR / "config.json"
PROFILE_DIR: Path = STATE_DIR / ".pw-profile"
DEFAULT_OUTPUT_DIR: Path = STATE_DIR / "data"

DEFAULT_LOGIN_TIMEOUT = 60  # seconds

# User id override for this run (set from CLI --user-id)
USER_ID_OVERRIDE: str | None = None

# George URLs
BASE_URL = "https://george.sparkasse.at"
LOGIN_URL = f"{BASE_URL}/index.html#/login"
DASHBOARD_URL = f"{BASE_URL}/index.html#/overview"


def _is_login_flow_url(url: str) -> bool:
    """Return True if URL looks like any login/SSO/OAuth page."""
    u = (url or "").lower()
    return (
        "login.sparkasse.at" in u
        or "/sts/oauth/authorize" in u
        or "#/login" in u
        or u.endswith("/login")
        or "/login" in u
    )


def _is_george_app_url(url: str) -> bool:
    u = (url or "").lower()
    return "george.sparkasse.at" in u


def _extract_token_expires_in_seconds(url: str | None) -> int | None:
    """Return expires_in seconds if the URL fragment includes an OAuth token response."""
    if not url:
        return None
    try:
        parts = urlsplit(url)
        frag = parts.fragment or ""
        if "access_token=" not in frag and "id_token=" not in frag:
            return None
        qs = dict(parse_qsl(frag, keep_blank_values=True))
        ei = qs.get("expires_in")
        return int(ei) if ei and ei.isdigit() else None
    except Exception:
        return None


def _safe_url_for_logs(url: str | None) -> str:
    """Redact sensitive info from URLs before logging.

    George sometimes returns OAuth tokens in the URL fragment, e.g.
    `index.html#access_token=...&expires_in=...&state=/overview...`.
    Never log those tokens.
    """
    if not url:
        return "<empty>"

    try:
        parts = urlsplit(url)
        frag = parts.fragment or ""
        if "access_token=" in frag or "id_token=" in frag or "refresh_token=" in frag:
            qs = dict(parse_qsl(frag, keep_blank_values=True))
            state = qs.get("state")
            expires_in = qs.get("expires_in")
            # Keep only non-sensitive debugging info
            safe_frag_bits = []
            if state:
                safe_frag_bits.append(f"state={state}")
            if expires_in:
                safe_frag_bits.append(f"expires_in={expires_in}")
            safe_frag = "&".join(safe_frag_bits) if safe_frag_bits else "<redacted>"
            return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, safe_frag))

        # Otherwise keep the URL as-is
        return url
    except Exception:
        # Last resort: coarse redaction
        return "<redacted-url>"


def _apply_state_dir(dir_value: str | None) -> None:
    """Apply state dir override and recompute derived paths."""
    global STATE_DIR, CONFIG_PATH, PROFILE_DIR, DEFAULT_OUTPUT_DIR

    if dir_value:
        STATE_DIR = Path(dir_value).expanduser().resolve()
    else:
        env_dir = os.environ.get("GEORGE_DIR")
        STATE_DIR = Path(env_dir).expanduser().resolve() if env_dir else _default_state_dir()

    CONFIG_PATH = STATE_DIR / "config.json"
    PROFILE_DIR = STATE_DIR / ".pw-profile"
    DEFAULT_OUTPUT_DIR = STATE_DIR / "data"

    # Load optional .env from the state dir.
    _load_dotenv(STATE_DIR / ".env")

def _login_timeout(args) -> int:
    return getattr(args, "login_timeout", DEFAULT_LOGIN_TIMEOUT)

def load_config() -> dict:
    """Load configuration from JSON file.

    Supports automatic migration from older formats.
    """
    if not CONFIG_PATH.exists():
        print(f"ERROR: Config file not found at {CONFIG_PATH}")
        print("Please create it with your 'user_id' and 'accounts'.")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)

    # Normalize + migrate accounts structure.
    # New format: accounts is a list of account dicts.
    accs = cfg.get("accounts")
    if accs is None:
        cfg["accounts"] = []
    elif isinstance(accs, dict):
        # Old format: { key: {account...}, ... }
        cfg["accounts"] = list(accs.values())
    elif isinstance(accs, list):
        pass
    else:
        raise ValueError("config.json: 'accounts' must be a list (preferred) or dict (legacy)")

    # user_id can be string (preferred) or list (legacy-ish)
    uid = cfg.get("user_id")
    if isinstance(uid, list):
        # Keep as-is; resolved later.
        pass
    elif uid is None:
        # allowed; resolved later.
        pass
    elif not isinstance(uid, str):
        raise ValueError("config.json: 'user_id' must be a string or a list of strings")

    return cfg

def save_config(config: dict) -> None:
    """Write config to disk (creates parent dirs)."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure accounts is always a list on disk.
    accs = config.get("accounts")
    if accs is None:
        config["accounts"] = []
    elif isinstance(accs, dict):
        config["accounts"] = list(accs.values())

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4, sort_keys=True)


_ACCOUNT_TYPE_PREFIX = {
    "currentaccount": "current",
    "currentaccount": "current",
    "saving": "saving",
    "loan": "loan",
    "credit": "credit",
    "kredit": "credit",
    "creditcard": "cc",
}


def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "account"


def _suggest_account_key(acc: dict, existing: set[str]) -> str:
    """Create a stable, human-usable account key for config.json.

    Prefer a name-based key (for readability) with a short suffix for uniqueness.
    """
    name = _slug(acc.get("name") or "")

    # Keep keys reasonably short
    name = name[:24]

    iban = (acc.get("iban") or "")
    iban_clean = re.sub(r"\s+", "", iban)
    suffix = iban_clean[-4:] if len(iban_clean) >= 4 else str(acc.get("id") or "")[-6:]
    suffix = suffix or "0000"

    base = f"{name}-{suffix}".lower()

    # If that base already exists, fall back to type-based base.
    if base in existing:
        acc_type = (acc.get("type") or "account").lower()
        prefix = _ACCOUNT_TYPE_PREFIX.get(acc_type, acc_type)
        base = f"{prefix}-{suffix}".lower()

    key = base
    i = 2
    while key in existing:
        key = f"{base}-{i}".lower()
        i += 1
    return key


def merge_accounts_into_config(config: dict, fetched_accounts: list[dict]) -> tuple[dict, list[str]]:
    """Merge fetched accounts into config['accounts'] (list).

    Returns (updated_config, changed_ids)
    """
    existing: list[dict]
    accs = config.get("accounts")
    if accs is None:
        existing = []
    elif isinstance(accs, dict):
        existing = list(accs.values())
    else:
        existing = list(accs)

    # Index by (type,id)
    by_tid: dict[tuple[str, str], int] = {}
    for idx, a in enumerate(existing):
        t = (a.get("type") or "").lower()
        i = str(a.get("id") or "")
        if t and i:
            by_tid[(t, i)] = idx

    changed: list[str] = []

    for acc in fetched_accounts:
        t = (acc.get("type") or "").lower()
        i = str(acc.get("id") or "")
        if not (t and i):
            continue

        pos = by_tid.get((t, i))
        if pos is not None:
            existing[pos] = {**existing[pos], **acc}
            changed.append(i)
        else:
            existing.append(acc)
            by_tid[(t, i)] = len(existing) - 1
            changed.append(i)

    # Stable-ish sort: type then name
    existing.sort(key=lambda a: ((a.get("type") or ""), (a.get("name") or "")))

    config["accounts"] = existing
    return config, changed


# Load configuration (lazy loaded later to allow help to run without config)
CONFIG = None


def get_account(account_key: str) -> dict:
    """Resolve an account by flexible query.

    Matches by:
    - exact id
    - exact IBAN (spaces ignored)
    - substring match on name
    - substring match on type
    - substring match on IBAN

    If ambiguous, raises with candidates.
    """
    global CONFIG
    if CONFIG is None:
        CONFIG = load_config()

    accounts: list[dict] = CONFIG.get("accounts", []) or []
    q = (account_key or "").strip().lower()

    def iban_norm(s: str | None) -> str:
        return re.sub(r"\s+", "", (s or "")).lower()

    # 1) Exact ID match
    for acc in accounts:
        if (acc.get("id") or "").lower() == q:
            return acc

    # 2) Exact IBAN match
    for acc in accounts:
        if acc.get("iban") and iban_norm(acc.get("iban")) == iban_norm(q):
            return acc

    # 3) Fuzzy matches
    matches: list[dict] = []
    for acc in accounts:
        name = (acc.get("name") or "").lower()
        typ = (acc.get("type") or "").lower()
        if q and (q in name or q in typ or (acc.get("iban") and q in iban_norm(acc.get("iban")))):
            matches.append(acc)

    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise ValueError(f"Unknown account: {account_key}. Run 'accounts' to list known accounts (and fetch if empty).")

    # Ambiguous
    lines = [f"Ambiguous account selector '{account_key}'. Matches:"]
    for acc in matches:
        lines.append(f"- {acc.get('name')} ({acc.get('type')}) id={acc.get('id')}")
    raise ValueError("\n".join(lines))


def wait_for_login_approval(page, timeout_seconds: int = 300) -> bool:
    """Wait for user to approve login on phone.

    Important: do NOT scan the entire HTML for generic phrases (they may exist in hidden UI).
    Only react to **visible** error/dismissal messages.
    """
    print(f"[login] Waiting up to {timeout_seconds}s for phone approval...", flush=True)
    start = time.time()
    last_reported = -1

    dismissed_locator = page.locator("text=The login request was dismissed")
    login_failed_locator = page.locator("text=Login failed")
    login_failed_de_locator = page.locator("text=Anmeldung fehlgeschlagen")

    while time.time() - start < timeout_seconds:
        current_url = page.url

        # Success: redirected back into George app (NOT into the IdP/OAuth page)
        if _is_george_app_url(current_url) and not _is_login_flow_url(current_url):
            # Avoid leading newline + make URL logging robust (some terminals wrap weirdly).
            print(f"[login] Approved! Redirected to: {_safe_url_for_logs(current_url)}", flush=True)

            # Optional: provide a human-friendly "expires at" hint (token expiry, not necessarily cookie session expiry).
            ei = _extract_token_expires_in_seconds(current_url)
            if ei:
                expires_at = datetime.now() + timedelta(seconds=ei)
                print(f"[login] Logged in successfully. Token expires at ~{expires_at:%Y-%m-%d %H:%M:%S}", flush=True)

            return True

        # Do not navigate away here.
        # When George is in the middle of the OAuth/approval flow, extra navigations
        # can restart the redirect chain and make approval look like it "did nothing".

        # Dismissed (user rejected)
        try:
            if dismissed_locator.first.is_visible(timeout=200):
                print("\n[login] ❌ LOGIN DISMISSED - user rejected. Start over.", flush=True)
                return False
        except Exception:
            pass

        # Explicit failure message (visible)
        try:
            if login_failed_locator.first.is_visible(timeout=200) or login_failed_de_locator.first.is_visible(timeout=200):
                print("\n[login] Login failed", flush=True)
                return False
        except Exception:
            pass

        # Progress reporting every 10 seconds
        elapsed = int(time.time() - start)
        interval = elapsed // 10
        if interval > last_reported:
            last_reported = interval
            remaining = timeout_seconds - elapsed
            print(f"[login] Still waiting... {remaining}s remaining (url={_safe_url_for_logs(page.url)})", flush=True)

        time.sleep(1)

    print("\n[login] Script timeout waiting for approval", flush=True)
    return False


def extract_verification_code(page) -> str:
    """Extract verification code from login page."""
    try:
        # Wait for the verification code section to appear
        page.wait_for_selector('text=/Verification code/i', timeout=15000)
        time.sleep(1)  # Give it a moment to fully render
        
        all_text = page.inner_text('body')

        # Look for *the* canonical line: "Verification code: XXXX"
        match = re.search(r'\bVerification code:\s*([A-Z0-9]{4})\b', all_text)
        if match:
            return match.group(1)
        
        # Fallback: scan for a line that exactly matches the format
        for line in all_text.split('\n'):
            m = re.match(r'^Verification code:\s*([A-Z0-9]{4})\s*$', line.strip())
            if m:
                return m.group(1)

        return ""
                    
    except PlaywrightTimeout:
        print("[login] Timeout waiting for verification code element", flush=True)
    except Exception as e:
        print(f"[login] Could not extract verification code: {e}", flush=True)
    return ""


def dismiss_modals(page):
    """Dismiss any modal overlays."""
    try:
        for selector in [
            'button:has-text("Dismiss")',
            'button:has-text("Close")',
            'button:has-text("OK")',
            'button[aria-label="Close"]',
        ]:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                print(f"[modal] Dismissing via {selector}", flush=True)
                btn.click()
                time.sleep(0.5)
    except Exception:
        pass


def login(page, timeout_seconds: int = 300) -> bool:
    """Perform George login with phone approval."""
    print("[login] Checking session...", flush=True)
    
    # Try dashboard first to see if session is valid.
    # NOTE: Going to about:blank first improves reliability for some SPA sessions.
    try:
        page.goto("about:blank")
        page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=15000)

        # Fast-path decision:
        # - If the session is expired, George usually redirects to the IdP within a second or two.
        # - If the session is valid, the overview tiles appear.
        tiles_visible = False
        t0 = time.time()
        while time.time() - t0 < 4.0:
            if _is_login_flow_url(page.url):
                break
            try:
                page.wait_for_selector(".g-card-overview-title", timeout=500)
                tiles_visible = True
                break
            except Exception:
                time.sleep(0.2)

        if tiles_visible and _is_george_app_url(page.url) and not _is_login_flow_url(page.url):
            # Extra guard: if the George login form is visible, session is NOT valid.
            login_form_visible = False
            try:
                login_form_visible = page.get_by_role(
                    "button", name=re.compile(r"start login", re.I)
                ).is_visible(timeout=800)
            except Exception:
                login_form_visible = False

            if not login_form_visible:
                print("[login] Session still valid!", flush=True)
                return True
    except Exception:
        pass

    print("[login] Session invalid/expired. Navigating to login...", flush=True)

    # Per observed behavior: always start from the overview and let George redirect
    # into the appropriate login/SSO flow.
    page.goto("about:blank")
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")

    # Wait for the George login form to appear. If it doesn't show up (e.g. we got
    # stuck at the IdP authorize page), fall back to the explicit /#/login route.
    try:
        # Keep this short: we want to type user_id ASAP.
        page.wait_for_selector('input[aria-label*="User"], input[placeholder*="User"], input', timeout=4000)
    except Exception:
        page.goto("about:blank")
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        page.wait_for_selector('input', timeout=4000)

    time.sleep(0.2)

    if _is_george_app_url(page.url) and not _is_login_flow_url(page.url):
        print("[login] Already logged in (redirected)!", flush=True)
        return True
    
    print(f"[login] Entering user ID...", flush=True)
    
    global CONFIG
    if CONFIG is None:
        CONFIG = load_config()
        
    try:
        user_id = _resolve_user_id(argparse.Namespace(user_id=USER_ID_OVERRIDE), CONFIG)
    except Exception as e:
        print(f"[login] ERROR: {e}")
        return False

    try:
        page.get_by_role("textbox", name=re.compile(r"user number|username", re.I)).fill(user_id)
    except Exception:
        try:
            page.get_by_role("textbox").first.fill(user_id)
        except Exception:
            page.fill('input', user_id)
    
    time.sleep(1)
    print("[login] Clicking 'Start login'...", flush=True)
    
    try:
        page.get_by_role("button", name="Start login").click()
    except Exception:
        btn = page.query_selector('button:has-text("Start login")')
        if btn:
            btn.click()
        else:
            print("[login] ERROR: Could not find login button", flush=True)
            return False
    
    # George renders the verification code asynchronously.
    # Waiting a bit here makes extraction much more reliable.
    time.sleep(5)
    code = extract_verification_code(page)

    if code:
        print(f"[login] Verification code: {code}", flush=True)
    else:
        print("[login] ⚠️ Could not extract code - CHECK BROWSER WINDOW", flush=True)
    
    # NOTE: No macOS-specific notifications. Code is printed to stdout for the caller
    # (Clawdbot session) to forward via Telegram.
    return wait_for_login_approval(page, timeout_seconds=timeout_seconds)


def _format_iban(iban: str) -> str:
    clean = re.sub(r"\s+", "", iban).strip()
    # Group in blocks of 4 for readability.
    return " ".join(clean[i : i + 4] for i in range(0, len(clean), 4))


def _first_iban_in_text(text: str) -> str | None:
    # Standard Austrian IBAN is 20 chars: AT + 18 digits.
    # Note: don't use a word-boundary here; George sometimes concatenates strings like "...KGAT31...".
    m = re.search(r"AT\d{2}(?:\s*\d{4}){4}", text)
    if m:
        return _format_iban(m.group(0))

    # Fallback: permissive, still anchored on AT + digits.
    m2 = re.search(r"AT\d{2}[0-9\s]{16,30}", text)
    if m2:
        return _format_iban(m2.group(0))

    return None


def try_extract_iban_from_account_page(page, acc_type: str, acc_id: str) -> str | None:
    """Try to extract IBAN by visiting the account detail page.

    This is slower than scraping the overview but tends to be more reliable.
    """
    try:
        page.goto("about:blank")
        page.goto(f"{BASE_URL}/index.html#/{acc_type}/{acc_id}", wait_until="domcontentloaded", timeout=15000)
        # Give SPA some time to render details.
        time.sleep(2)
        dismiss_modals(page)
        body = page.inner_text("body")
        return _first_iban_in_text(body)
    except Exception:
        return None


def list_accounts_from_page(page) -> list[dict]:
    """Fetch account list from George dashboard."""
    print("[accounts] Fetching accounts from dashboard...", flush=True)
    # Avoid networkidle (SPA + long-polling). domcontentloaded is more reliable here.
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
    ensure_list_layout(page)

    # Wait for account list + lazy loading
    try:
        page.wait_for_selector(".g-card-overview-title", timeout=30000)
        time.sleep(3)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
    except Exception:
        pass

    dismiss_modals(page)

    accounts = []

    # Parse account links from the overview (including loans)
    links = page.query_selector_all('a[href*="/currentAccount/"], a[href*="/saving/"], a[href*="/loan/"], a[href*="/credit/"], a[href*="/kredit/"], a[href*="/creditcard/"]')

    for link in links:
        try:
            href = link.get_attribute('href') or ""

            match = re.search(r'/(currentAccount|saving|loan|credit|kredit|creditcard)/([A-F0-9-]+)', href)
            if not match:
                continue

            acc_type = match.group(1)
            acc_id = match.group(2)

            # The IBAN is usually NOT inside the <a> text; it's nearby within the card.
            # Grab a larger text blob by walking up the DOM.
            card_text = ""
            try:
                card_text = link.evaluate(
                    """
                    (el) => {
                      let cur = el;
                      for (let i = 0; i < 10 && cur; i++) {
                        const t = (cur.innerText || '').trim();
                        if (t && t.length > 20) return t;
                        cur = cur.parentElement;
                      }
                      return (el.parentElement?.innerText || '').trim();
                    }
                    """
                )
            except Exception:
                card_text = (link.inner_text() or "")

            # Name: first line of the card text
            name = (card_text.split("\n")[0] if card_text else "").strip() or (link.inner_text() or "").split("\n")[0].strip()

            # IBAN: matches both spaced and non-spaced formats
            iban = _first_iban_in_text(card_text)

            accounts.append({
                "name": name,
                "iban": iban,
                "id": acc_id,
                "type": acc_type,
            })
        except Exception:
            continue

    # Deduplicate by ID
    seen = set()
    unique = []
    for acc in accounts:
        if acc["id"] not in seen:
            seen.add(acc["id"])
            unique.append(acc)

    return unique


def ensure_list_layout(page) -> None:
    """Ensure the dashboard is in list layout (not tiles).

    List layout is more consistent for scraping (IBAN next to available amount).
    """
    try:
        btn = page.locator('[data-cy="dashboard-view-mode-toggle-list-button"]')
        if btn.count() > 0:
            # If aria-pressed isn't true, click it.
            pressed = (btn.first.get_attribute("aria-pressed") or "").lower() == "true"
            if not pressed:
                btn.first.click(force=True)
                time.sleep(1)
    except Exception:
        pass


def list_account_balances_from_overview(page) -> list[dict]:
    """Return accounts with (balance, available) as shown on the George overview page."""
    # Avoid networkidle (SPA + long-polling). domcontentloaded is more reliable here.
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
    ensure_list_layout(page)
    
    # Wait for skeletons to load
    print("[accounts] Waiting for account list to load...", flush=True)
    try:
        # Wait for at least one account title to appear
        page.wait_for_selector(".g-card-overview-title", timeout=30000)
        # Give it a bit more time for all to settle
        time.sleep(5)

        # Scroll to bottom to trigger lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        print("[accounts] Scrolled to bottom, waiting 5s...", flush=True)
        time.sleep(5)

        # Try again after scroll (sometimes overview populates late)
        page.wait_for_selector(".g-card-overview-title", timeout=20000)
    except Exception:
        print("[accounts] Warning: Timeout waiting for account list", flush=True)

    dismiss_modals(page)
    
    # Account cards typically have a heading (h3) with account name and nearby balance text.
    # Include currentAccount, saving, loan/credit accounts, and credit cards
    cards = page.query_selector_all('h3:has(a[href*="/currentAccount/"]), h3:has(a[href*="/saving/"]), h3:has(a[href*="/loan/"]), h3:has(a[href*="/credit/"]), h3:has(a[href*="/kredit/"]), h3:has(a[href*="/creditcard/"])')

    results: list[dict] = []

    def parse_amount(s: str) -> float:
        return float(s.replace('.', '').replace(',', '.'))

    for h3 in cards:
        try:
            name = (h3.inner_text() or "").strip()
            link = h3.query_selector('a')
            href = link.get_attribute('href') if link else ""
            m = re.search(r'/(currentAccount|saving|loan|credit|kredit|creditcard)/([A-F0-9-]+)', href or "")
            if not m:
                continue
            acc_type, acc_id = m.group(1), m.group(2)
            
            # Debug: print card info
            # print(f"[debug] Checking card: {name} ({acc_type}/{acc_id})", flush=True)

            # Grab surrounding card text: climb ancestors until we see currency/amount patterns
            card_text = ""
            try:
                card_text = h3.evaluate(
                    """
                    (el) => {
                      const want = /(amount|betrag|stand|eur|usd|chf|gbp|€|minus|[0-9]{1,3}(\\.[0-9]{3})*,[0-9]{2})/i;
                      let cur = el;
                      for (let i = 0; i < 10 && cur; i++) {
                        const t = (cur.innerText || '').trim();
                        if (t && t.length > 20 && want.test(t)) {
                          return t;
                        }
                        cur = cur.parentElement;
                      }
                      // fallback: parent text
                      return (el.parentElement?.innerText || '').trim();
                    }
                    """
                )
            except Exception:
                card_text = (h3.inner_text() or "").strip()
            
            # Debug: print card info if needed
            # print(f"[debug] Card: {name} | Text: {card_text!r}", flush=True)

            # BALANCE: prefer the "Amount:" line if present
            balance = None
            currency = None

            # Accept currency codes or symbols
            ccy_pat = r'(EUR|USD|CHF|GBP|€|\$)'

            # Matches e.g. "Amount: 852,53 EUR" or German variants
            # Note: The "Amount:" line often has raw numbers like 155470,53 (no dots),
            # while the UI display has 155.470,53. We match both.
            amount_match = re.search(
                rf'(Amount|Betrag|Stand)\s*:?\s*(Minus\s+)?([0-9.]+,\s*[0-9]{{2}})\s*{ccy_pat}',
                card_text,
                re.IGNORECASE,
            )
            if amount_match:
                sign = -1 if amount_match.group(2) else 1
                balance = sign * parse_amount(amount_match.group(3))
                currency = amount_match.group(4)
            else:
                # Fallback: first currency amount on the card
                any_match = re.search(rf'(Minus\s+)?([0-9.]+,\s*[0-9]{{2}})\s*{ccy_pat}', card_text)
                if any_match:
                    sign = -1 if any_match.group(1) else 1
                    balance = sign * parse_amount(any_match.group(2))
                    currency = any_match.group(3)

            # Normalize currency symbols
            if currency == '€':
                currency = 'EUR'
            if currency == '$':
                currency = 'USD'

            # AVAILABLE: e.g. "434,65 EUR available" or "€ 434,65 available" or "verfügbar"
            available = None
            available_currency = None
            # Try pattern: "amount CCY available" or "CCY amount available"
            avail_match = re.search(
                rf'([0-9]{{1,3}}(?:\.[0-9]{{3}})*,[0-9]{{2}})\s*{ccy_pat}\s*(available|verf\u00fcgbar)',
                card_text,
                re.IGNORECASE,
            )
            if not avail_match:
                # Try: "€ 434,65 available"
                avail_match = re.search(
                    rf'{ccy_pat}\s*([0-9]{{1,3}}(?:\.[0-9]{{3}})*,[0-9]{{2}})\s*(available|verf\u00fcgbar)',
                    card_text,
                    re.IGNORECASE,
                )
            if avail_match:
                # Groups depend on which pattern matched
                g1, g2 = avail_match.group(1), avail_match.group(2)
                # Figure out which is amount vs currency
                if re.match(r'[0-9]', g1):
                    available = parse_amount(g1)
                    available_currency = g2
                else:
                    available_currency = g1
                    available = parse_amount(g2)
                if available_currency == '€':
                    available_currency = 'EUR'
                if available_currency == '$':
                    available_currency = 'USD'
            else:
                # Debug if the card mentions available/verfügbar but regex didn't match
                if re.search(r'(available|verf)', card_text, re.IGNORECASE):
                    snippet = re.sub(r'\s+', ' ', card_text).strip()[:220]
                    print(f"[balances] WARN could not parse AVAILABLE for '{name}'. Snippet: {snippet}", flush=True)

            # Debug snippet if we failed to parse
            if balance is None:
                snippet = re.sub(r'\s+', ' ', card_text).strip()[:180]
                print(f"[balances] WARN could not parse balance for '{name}'. Snippet: {snippet}", flush=True)

            results.append({
                "name": name,
                "type": acc_type,
                "id": acc_id,
                "balance": balance,
                "currency": currency,
                "available": available,
                "available_currency": available_currency,
            })
        except Exception:
            continue

    # Deduplicate by id
    seen = set()
    out = []
    for r in results:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    return out


def download_statements_pdf(page, account: dict, statement_ids: list[int], 
                            include_receipts: bool = True, download_dir: Path = None) -> list[Path]:
    """Download PDF statements for an account."""
    acc_type = account["type"]
    acc_id = account["id"]
    acc_name = account["name"]
    
    url = f"https://george.sparkasse.at/index.html#/{acc_type}/{acc_id}/statements"
    print(f"[statements] Downloading statements {statement_ids} for {acc_name}...", flush=True)
    
    page.goto(url, wait_until="networkidle")
    time.sleep(2)
    dismiss_modals(page)
    time.sleep(1)
    
    # Enter multi-select mode
    try:
        page.get_by_role("button", name="Download multiple").click()
        time.sleep(1)
    except Exception:
        print("[statements] Could not find 'Download multiple' button", flush=True)
        return []
    
    # Select statements
    for stmt_id in statement_ids:
        try:
            page.get_by_role("checkbox", name=f"Statement - {stmt_id}").check()
            time.sleep(0.3)
        except Exception:
            print(f"[statements] WARNING: Could not find statement {stmt_id}", flush=True)
    
    # Click Download
    print("[statements] Opening download dialog...", flush=True)
    try:
        page.get_by_role("button", name="Download").first.click()
    except Exception:
        btn = page.query_selector('button:has-text("Download"):not([disabled])')
        if btn:
            btn.click()
    time.sleep(2)
    
    # Check "incl. booking receipts"
    if include_receipts:
        print("[statements] Checking 'incl. booking receipts'...", flush=True)
        try:
            page.get_by_text("booking receipts").click()
            time.sleep(0.5)
        except Exception as e:
            print(f"[statements] Could not check receipts: {e}", flush=True)
    
    # Click Download in dialog
    print("[statements] Starting download...", flush=True)
    try:
        with page.expect_download(timeout=120000) as download_info:
            modal_download = page.locator('.g-modal button:has-text("Download")')
            if modal_download.count() > 0:
                modal_download.first.click(force=True)
            else:
                page.get_by_role("button", name="Download").last.click(force=True)
        
        download = download_info.value
        print(f"[statements] Downloaded: {download.suggested_filename}", flush=True)
        
        if download_dir:
            dest = download_dir / download.suggested_filename
            download.save_as(dest)
            print(f"[statements] Saved: {dest}", flush=True)
            return [dest]
    except Exception as e:
        print(f"[statements] Download failed: {e}", flush=True)
    
    return []


EXPORT_TYPES = ["camt53", "mt940"]
DEFAULT_EXPORT_TYPE = "camt53"
EXPORT_TYPE_LABELS = {
    "camt53": "CAMT53",
    "mt940": "MT940",
}


def download_data_exports(page, export_type: str, download_dir: Path = None) -> list[Path]:
    """Download data exports (CAMT53/MT940) for all available accounts."""
    export_type = export_type.lower()
    if export_type not in EXPORT_TYPES:
        print(f"[export] Invalid type '{export_type}'. Supported: {', '.join(EXPORT_TYPES)}", flush=True)
        return []

    label = EXPORT_TYPE_LABELS[export_type]
    print(f"[export] Downloading {label} data exports (all accounts)...", flush=True)

    page.goto("https://george.sparkasse.at/index.html#/datacarrier/download", wait_until="networkidle")
    time.sleep(2)
    dismiss_modals(page)

    downloaded = []
    rows = page.query_selector_all(f'tr:has-text("{label}")')
    if not rows:
        print(f"[export] No {label} exports found", flush=True)
        return []

    for row in rows:
        download_btn = row.query_selector("button")
        if not download_btn:
            continue
        try:
            with page.expect_download(timeout=30000) as download_info:
                download_btn.click()
            dl = download_info.value
            if download_dir:
                dest = download_dir / dl.suggested_filename
                dl.save_as(dest)
                print(f"[export] Saved: {dest.name}", flush=True)
                downloaded.append(dest)
            time.sleep(1)
        except Exception as e:
            print(f"[export] Download failed: {e}", flush=True)

    return downloaded


def _parse_ddmmyyyy(s: str) -> date:
    return datetime.strptime(s, "%d.%m.%Y").date()


def _normalize_date_range(date_from: str | None, date_to: str | None) -> tuple[str | None, str]:
    """Return (date_from, date_to) as strings in DD.MM.YYYY.

    - date_to defaults to today
    - if date_to is in the future, clamp to today
    """
    today = date.today()

    df = _parse_ddmmyyyy(date_from) if date_from else None
    dt = _parse_ddmmyyyy(date_to) if date_to else today

    if dt > today:
        dt = today

    if df and df > dt:
        raise ValueError(f"date_from {df} is after date_to {dt}")

    df_s = df.strftime("%d.%m.%Y") if df else None
    dt_s = dt.strftime("%d.%m.%Y")
    return df_s, dt_s


# Supported transaction export formats
TRANSACTION_EXPORT_FORMATS = ["csv", "json", "ofx", "xlsx"]
DEFAULT_TRANSACTION_FORMAT = "csv"

# Map format names to George UI labels (case-insensitive matching used)
TRANSACTION_FORMAT_LABELS = {
    "csv": "CSV",
    "json": "JSON",
    "ofx": "OFX",
    "xlsx": "Excel",  # George may show "Excel" or "XLSX"
}

def download_transactions(page, account: dict, date_from: str = None, date_to: str = None,
                          download_dir: Path = None, fmt: str = "csv") -> list[Path]:
    """Download transactions for an account in the specified format.
    
    Args:
        page: Playwright page object
        account: Account dict with type, id, name, iban
        date_from: Start date (DD.MM.YYYY)
        date_to: End date (DD.MM.YYYY)
        download_dir: Directory to save downloaded file
        fmt: Export format (csv, json, ofx, xlsx)
    
    Returns:
        List of downloaded file paths
    """
    acc_type = account["type"]
    acc_id = account["id"]
    acc_name = account["name"]
    fmt = fmt.lower()
    
    if fmt not in TRANSACTION_EXPORT_FORMATS:
        print(f"[transactions] Invalid format '{fmt}'. Supported: {', '.join(TRANSACTION_EXPORT_FORMATS)}", flush=True)
        return []
    
    url = f"https://george.sparkasse.at/index.html#/{acc_type}/{acc_id}"
    print(f"[transactions] Downloading {fmt.upper()} transactions for {acc_name}...", flush=True)
    
    page.goto(url, wait_until="networkidle")
    time.sleep(2)
    dismiss_modals(page)
    
    # Look for export/download button in transaction history
    # George has a "Print Overview" or export option
    try:
        # Try to find export button
        export_btn = page.query_selector('button:has-text("Export")')
        if not export_btn:
            export_btn = page.query_selector('button:has-text("Download")')
        if not export_btn:
            # Look for three-dot menu
            more_btn = page.query_selector('button:has-text("More")')
            if more_btn:
                more_btn.click()
                time.sleep(1)
                export_btn = page.query_selector('button:has-text("Export")')
        
        if export_btn:
            export_btn.click()
            time.sleep(2)
            
            # Select the requested format
            format_label = TRANSACTION_FORMAT_LABELS.get(fmt, fmt.upper())
            format_option = page.query_selector(f'text={format_label}')
            if not format_option and fmt == "xlsx":
                # Try alternate labels for Excel
                format_option = page.query_selector('text=XLSX') or page.query_selector('text=Excel')
            if format_option:
                format_option.click()
                time.sleep(1)
            elif fmt != "csv":
                # If specific format not found and it's not CSV, warn user
                print(f"[transactions] Warning: Could not find {fmt.upper()} option, attempting default download", flush=True)
            
            # Click final download
            with page.expect_download(timeout=60000) as download_info:
                dl_btn = page.query_selector('button:has-text("Download")')
                if dl_btn:
                    dl_btn.click(force=True)
            
            dl = download_info.value
            if download_dir:
                # Normalize filename to include account + date range (and clamp future end-date to today)
                iban = (account.get("iban") or "").replace(" ", "")
                if not iban:
                    iban = account.get("id")

                df, dt = _normalize_date_range(date_from, date_to)
                df_iso = _parse_ddmmyyyy(df).isoformat() if df else f"{date.today().year}-01-01"
                dt_iso = _parse_ddmmyyyy(dt).isoformat()

                dest = download_dir / f"{iban}_{df_iso}_{dt_iso}.{fmt}"
                dl.save_as(dest)
                print(f"[transactions] Saved: {dest}", flush=True)
                return [dest]
        else:
            print("[transactions] Could not find export button - trying History page", flush=True)
            
            # Navigate to history page
            history_url = f"https://george.sparkasse.at/index.html#/{acc_type}/{acc_id}/history"
            page.goto(history_url, wait_until="networkidle")
            time.sleep(2)
            
            # TODO: Implement date filtering and export from history
            print("[transactions] History-based export not yet implemented", flush=True)
            
    except Exception as e:
        print(f"[transactions] Export failed: {e}", flush=True)
    
    return []


# Legacy alias for backward compatibility
def download_csv_transactions(page, account: dict, date_from: str = None, date_to: str = None,
                              download_dir: Path = None) -> list[Path]:
    """Download transaction CSV for an account. (Legacy - use download_transactions instead)"""
    return download_transactions(page, account, date_from, date_to, download_dir, fmt="csv")


# =============================================================================
# CLI Commands
# =============================================================================

def cmd_login(args):
    """Perform standalone login."""
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        try:
            if login(page, timeout_seconds=_login_timeout(args)):
                print("[login] Success! Session saved.", flush=True)
                return 0
            else:
                return 1
        finally:
            context.close()

def cmd_logout(args):
    """Clear session profile."""
    profile_dir = PROFILE_DIR
    if profile_dir.exists():
        import shutil
        try:
            shutil.rmtree(profile_dir)
            print(f"[logout] Removed profile at {profile_dir}", flush=True)
            return 0
        except Exception as e:
            print(f"[logout] Error removing profile: {e}", flush=True)
            return 1
    else:
        print("[logout] No session found.", flush=True)
        return 0


def _resolve_user_id(args, config: dict) -> str:
    """Resolve the George user_id.

    Precedence:
    1) --user-id
    2) GEORGE_USER_ID from environment (optionally via state-dir .env)
    3) config.json user_id (only if exactly one)

    If config has no user_id or more than one, raise with guidance.
    """
    if getattr(args, "user_id", None):
        return str(args.user_id).strip()

    env_uid = os.environ.get("GEORGE_USER_ID")
    if env_uid:
        return env_uid.strip()

    uid = config.get("user_id")
    if uid is None or uid == "":
        raise ValueError(
            "No user_id configured. Set one of:\n"
            "- pass --user-id <your-user-number-or-username>\n"
            "- set GEORGE_USER_ID (or put it in ~/.clawdbot/george/.env)\n"
            "- add user_id to config.json"
        )

    if isinstance(uid, str):
        return uid.strip()

    if isinstance(uid, list):
        uids = [str(x).strip() for x in uid if str(x).strip()]
        if len(uids) == 1:
            return uids[0]
        raise ValueError(
            "Multiple user_id entries found in config.json.\n"
            "Fix by keeping exactly one, or use --user-id / GEORGE_USER_ID to override."
        )

    raise ValueError("Invalid user_id in config.json")


def cmd_setup(args):
    """Setup George user ID and ensure playwright is installed."""

    print("[setup] George Banking Setup")
    print()
    
    # Get user ID
    if args.user_id:
        user_id = args.user_id
    else:
        print("Your George user ID can be found in the George app.")
        print("It can be an 8–9 digit Verfügernummer or a custom username.")
        print("Tip: you can also set GEORGE_USER_ID in ~/.clawdbot/george/.env")
        print()
        user_id = input("User ID: ").strip()
    
    if not user_id:
        print("[setup] ERROR: User ID required")
        return 1
    
    # Create config directory
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create config.json
    config = {
        "user_id": user_id,
        "accounts": []
    }
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"[setup] ✓ Config saved to {CONFIG_PATH}")
    print(f"[setup] To discover accounts, run: george.py accounts")
    print(f"[setup] To override user_id without editing config: george.py --user-id <id> ...")
    
    # Check playwright
    print("[setup] Checking playwright...")
    try:
        from playwright.sync_api import sync_playwright
        print("[setup] ✓ Playwright already installed")
    except ImportError:
        print("[setup] Installing playwright...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            print("[setup] ✓ Playwright installed")
        except subprocess.CalledProcessError:
            print("[setup] ERROR: Failed to install playwright")
            print("[setup] Run manually: pip install playwright")
            return 1
    
    # Install chromium browser
    print("[setup] Installing chromium browser...")
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("[setup] ✓ Chromium installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[setup] WARNING: Could not install chromium")
        print("[setup] Run manually: playwright install chromium")
    
    print()
    print("[setup] ✓ Setup complete!")
    print(f"[setup] Next steps:")
    print(f"  1. george.py accounts                # Discover + save your accounts")
    print(f"  2. george.py balances           # Test with balances")
    
    return 0


def cmd_accounts(args):
    """List available accounts."""
    global CONFIG
    if CONFIG is None:
        CONFIG = load_config()

    print("\n=== Known Accounts (from config) ===\n")
    accounts: list[dict] = CONFIG.get("accounts", []) or []

    for acc in accounts:
        iban = acc.get("iban") or "N/A"
        acc_id = acc.get("id") or "N/A"
        typ = acc.get("type") or "N/A"
        name = acc.get("name") or "N/A"
        print(f"  {typ:12} {name:28} {iban:24} id={acc_id}")

    # Auto-fetch if config has no accounts. Explicit --fetch always refreshes.
    do_fetch = bool(args.fetch) or len(accounts) == 0

    if do_fetch:
        if not accounts:
            print("\n[accounts] No accounts in config.json; fetching from George...", flush=True)

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=not args.visible,
                viewport={"width": 1280, "height": 900},
            )
            page = context.new_page()

            try:
                if login(page, timeout_seconds=_login_timeout(args)):
                    dismiss_modals(page)
                    fetched = list_accounts_from_page(page)

                    # Fill missing IBANs by visiting the account pages (best-effort).
                    for acc in fetched:
                        if acc.get("iban"):
                            continue
                        if (acc.get("type") or "").lower() == "creditcard":
                            continue
                        iban = try_extract_iban_from_account_page(page, acc.get("type") or "", acc.get("id") or "")
                        if iban:
                            acc["iban"] = iban

                    print("\n=== Accounts from George ===\n")
                    for acc in fetched:
                        iban = acc.get("iban") or "N/A"
                        print(f"  {acc['type']:15} {acc['name']:25} {iban}")
                        print(f"    ID: {acc['id']}")

                    updated, changed = merge_accounts_into_config(CONFIG, fetched)
                    if changed:
                        CONFIG = updated
                        save_config(CONFIG)
                        print("\n[accounts] Updated config.json (ids):")
                        for cid in changed:
                            print(f"  - {cid}")
            finally:
                context.close()

    return 0


def cmd_balances(args):
    """List all accounts and their balances from the George overview."""
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)
            rows = list_account_balances_from_overview(page)

            # Print in a parseable format
            def fmt(amount: float | None, cur: str | None) -> str:
                if amount is None or not cur:
                    return "N/A"
                # 1234.56 -> 1.234,56
                s = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"{s} {cur}"

            print("\n=== Balances (George overview) ===\n")
            for r in rows:
                bal_str = fmt(r.get("balance"), r.get("currency"))
                avail_str = fmt(r.get("available"), r.get("available_currency") or r.get("currency"))
                if r.get("available") is not None:
                    print(f"- {r['name']}: {bal_str} (available: {avail_str})")
                else:
                    print(f"- {r['name']}: {bal_str}")

            return 0
        finally:
            context.close()


def cmd_statements(args):
    """Download PDF statements for an account."""
    account = get_account(args.account)
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{args.year}-Q{args.quarter}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Statement IDs for Q4 (validated mapping)
    if args.quarter == 4:
        stmt_ids = [11, 12, 13, 14]
    else:
        raise NotImplementedError(f"Q{args.quarter} statement mapping not yet validated")
    
    print(f"[george] Downloading Q{args.quarter}/{args.year} statements for {account['name']}")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=not args.visible,
            accept_downloads=True,
            downloads_path=str(output_dir),
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()
        
        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1
            
            dismiss_modals(page)
            files = download_statements_pdf(
                page, account, stmt_ids,
                include_receipts=not args.no_receipts,
                download_dir=output_dir
            )
            
            print(f"\n[george] Downloaded {len(files)} PDF files")
        finally:
            context.close()
    
    return 0


def cmd_export(args):
    """Download data exports (CAMT53/MT940) for all available accounts."""
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    export_type = args.type.lower()
    if export_type not in EXPORT_TYPES:
        print(f"[export] Invalid type '{export_type}'. Supported: {', '.join(EXPORT_TYPES)}")
        return 1

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=not args.visible,
            accept_downloads=True,
            downloads_path=str(output_dir),
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)
            files = download_data_exports(page, export_type, download_dir=output_dir)
            label = EXPORT_TYPE_LABELS[export_type]
            print(f"\n[george] Downloaded {len(files)} {label} export files")
        finally:
            context.close()

    return 0


def cmd_transactions(args):
    """Download transactions for an account in the specified format."""
    account = get_account(args.account)
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fmt = args.format.lower()
    if fmt not in TRANSACTION_EXPORT_FORMATS:
        print(f"[transactions] Invalid format '{fmt}'. Supported: {', '.join(TRANSACTION_EXPORT_FORMATS)}")
        return 1

    # Normalize date range: --to defaults to today; future --to clamped to today
    try:
        date_from, date_to = _normalize_date_range(args.date_from, args.date_to)
    except Exception as e:
        print(f"[transactions] Invalid date range: {e}")
        return 1

    if args.date_to:
        # Informative log if user gave a future date
        try:
            if _parse_ddmmyyyy(args.date_to) > date.today():
                print(f"[transactions] NOTE: --to {args.date_to} is in the future; using today ({date_to}) instead", flush=True)
        except Exception:
            pass

    print(f"[george] Downloading {fmt.upper()} for {account['name']} ({date_from or 'DEFAULT'} -> {date_to})")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=not args.visible,
            accept_downloads=True,
            downloads_path=str(output_dir),
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)
            files = download_transactions(
                page, account,
                date_from=date_from,
                date_to=date_to,
                download_dir=output_dir,
                fmt=fmt,
            )

            print(f"\n[george] Downloaded {len(files)} {fmt.upper()} files")
        finally:
            context.close()

    return 0


def cmd_csv(args):
    """Download transaction CSV for an account. (Deprecated: use 'transactions' instead)"""
    print("[csv] Note: 'csv' command is deprecated. Use 'transactions -f csv' instead.", flush=True)
    # Create a fake args object with format=csv
    args.format = "csv"
    return cmd_transactions(args)


def main():
    parser = argparse.ArgumentParser(
        description="George Banking Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  george.py setup                                # Initial setup (user ID + playwright)
  george.py accounts                             # If config has no accounts: fetch + save
  george.py statements -a main -y 2025 -q 4      # Download PDF statements
  george.py export                               # Download CAMT53 data exports (all accounts)
  george.py export --type mt940                  # Download MT940 data exports
  george.py transactions -a familie              # Download transactions (CSV default)
  george.py transactions -a familie -f json      # Download transactions as JSON
        """
    )
    
    # Global options
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    parser.add_argument("--dir", default=None, help="State directory (default: ~/.clawdbot/george; override via GEORGE_DIR)")
    parser.add_argument("--login-timeout", type=int, default=DEFAULT_LOGIN_TIMEOUT, help="Seconds to wait for phone approval")
    parser.add_argument("--user-id", default=None, help="Override George user number/username (or set GEORGE_USER_ID)")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    setup_parser = subparsers.add_parser("setup", help="Setup user ID and install playwright")
    setup_parser.add_argument("--user-id", help="George user ID (8-9 digit number)")
    setup_parser.set_defaults(func=cmd_setup)

    # login (standalone)
    login_parser = subparsers.add_parser("login", help="Perform login only")
    login_parser.set_defaults(func=cmd_login)

    # logout (standalone)
    logout_parser = subparsers.add_parser("logout", help="Clear session/profile")
    logout_parser.set_defaults(func=cmd_logout)

    # accounts
    acc_parser = subparsers.add_parser("accounts", help="List available accounts")
    acc_parser.add_argument("--fetch", action="store_true", help="Fetch live from George (requires login); updates config.json")
    acc_parser.set_defaults(func=cmd_accounts)

    # balances
    bal_parser = subparsers.add_parser("balances", help="List all accounts with balances (overview)")
    bal_parser.set_defaults(func=cmd_balances)

    # statements
    stmt_parser = subparsers.add_parser("statements", help="Download PDF statements")
    stmt_parser.add_argument("-a", "--account", required=True, help="Account key/name/IBAN")
    stmt_parser.add_argument("-y", "--year", type=int, required=True)
    stmt_parser.add_argument("-q", "--quarter", type=int, required=True, choices=[1, 2, 3, 4])
    stmt_parser.add_argument("-o", "--output", help="Output directory")
    stmt_parser.add_argument("--no-receipts", action="store_true", help="Skip booking receipts")
    stmt_parser.set_defaults(func=cmd_statements)
    
    # export (data export: CAMT53/MT940)
    export_parser = subparsers.add_parser(
        "export",
        help="Download data exports (CAMT53/MT940)",
        description=(
            "You can export (download) all available new data and files for all of your set-up accounts "
            "in order to use them for your bookkeeping. The Data Export is available as soon as the data "
            "for an account statement are available and a statement request with your selected frequency "
            "has been done. From then on, the Export will be available for a maximum of 3 months."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    export_parser.add_argument("--type", default=DEFAULT_EXPORT_TYPE, choices=EXPORT_TYPES,
                               help="Export type (default: camt53)")
    export_parser.add_argument("-o", "--output", help="Output directory")
    export_parser.set_defaults(func=cmd_export)

    # transactions (primary transaction export command)
    transactions_parser = subparsers.add_parser("transactions", help="Download transactions (csv/json/ofx/xlsx)")
    transactions_parser.add_argument("-a", "--account", required=True, help="Account key/name/IBAN")
    transactions_parser.add_argument("-f", "--format", default=DEFAULT_TRANSACTION_FORMAT,
                                     choices=TRANSACTION_EXPORT_FORMATS,
                                     help="Export format (default: csv)")
    transactions_parser.add_argument("-o", "--output", help="Output directory")
    transactions_parser.add_argument("--from", dest="date_from", help="Start date (DD.MM.YYYY)")
    transactions_parser.add_argument("--to", dest="date_to", help="End date (DD.MM.YYYY)")
    transactions_parser.set_defaults(func=cmd_transactions)
    
    # csv (deprecated alias for transactions -f csv)
    csv_parser = subparsers.add_parser("csv", help="[DEPRECATED] Use 'transactions' instead")
    csv_parser.add_argument("-a", "--account", required=True, help="Account key/name/IBAN")
    csv_parser.add_argument("-o", "--output", help="Output directory")
    csv_parser.add_argument("--from", dest="date_from", help="Start date (DD.MM.YYYY)")
    csv_parser.add_argument("--to", dest="date_to", help="End date (DD.MM.YYYY)")
    csv_parser.set_defaults(func=cmd_csv)
    
    args = parser.parse_args()
    _apply_state_dir(getattr(args, "dir", None))

    # Make --user-id available to login() without threading args everywhere.
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = getattr(args, "user_id", None)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
