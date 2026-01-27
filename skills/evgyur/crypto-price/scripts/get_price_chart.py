#!/usr/bin/env python3
import json
import math
import re
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DEFAULT_HOURS = 24
CANDLE_MINUTES = 15
CACHE_TTL_SEC = 300
COINGECKO_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies={currency}"
COINGECKO_OHLC_URL = "https://api.coingecko.com/api/v3/coins/{id}/ohlc?vs_currency={currency}&days=1"
COINGECKO_SEARCH_URL = "https://api.coingecko.com/api/v3/search?query={query}"
COINGECKO_MARKET_CHART_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart?vs_currency={currency}&days=1"
COINGECKO_MARKET_CHART_DAYS_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart?vs_currency={currency}&days={days}"
HYPERLIQUID_INFO_URL = "https://api.hyperliquid.xyz/info"

TOKEN_ID_MAP = {
    "HYPE": "hyperliquid",
    "HYPERLIQUID": "hyperliquid",
}


def _json_error(message, details=None):
    payload = {"error": message}
    if details:
        payload["details"] = details
    print(json.dumps(payload))
    return 0


def _cache_path(prefix, token_id):
    safe = token_id.replace("/", "-")
    return f"/tmp/crypto_price_{prefix}_{safe}.json"


def _read_cache(path, max_age_sec):
    try:
        stat = os.stat(path)
    except FileNotFoundError:
        return None
    age = time.time() - stat.st_mtime
    if age > max_age_sec:
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def _write_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
    except OSError:
        return


def _fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "clawdbot-crypto-price/1.0"},
    )
    retry_codes = {429, 502, 503, 504}
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError("invalid JSON") from exc
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in retry_codes and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(str(exc)) from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(str(exc)) from exc
    raise RuntimeError(str(last_error))


def _post_json(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "clawdbot-crypto-price/1.0"},
    )
    retry_codes = {429, 502, 503, 504}
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError("invalid JSON") from exc
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in retry_codes and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(str(exc)) from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(str(exc)) from exc
    raise RuntimeError(str(last_error))


def _post_json(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "clawdbot-crypto-price/1.0"},
    )
    retry_codes = {429, 502, 503, 504}
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError("invalid JSON") from exc
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in retry_codes and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(str(exc)) from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(str(exc)) from exc
    raise RuntimeError(str(last_error))


def _get_price(token_id, currency):
    cache_path = _cache_path(f"price_{currency}", token_id)
    cached = _read_cache(cache_path, CACHE_TTL_SEC)
    if cached is not None:
        return cached
    data = _fetch_json(COINGECKO_PRICE_URL.format(id=token_id, currency=currency))
    _write_cache(cache_path, data)
    return data


def _get_ohlc(token_id, currency):
    cache_path = _cache_path(f"ohlc_{currency}", token_id)
    cached = _read_cache(cache_path, CACHE_TTL_SEC)
    if cached is not None:
        return cached
    data = _fetch_json(COINGECKO_OHLC_URL.format(id=token_id, currency=currency))
    _write_cache(cache_path, data)
    return data


def _get_market_chart(token_id, currency, days):
    cache_path = _cache_path(f"market_{currency}_{days}", token_id)
    cached = _read_cache(cache_path, CACHE_TTL_SEC)
    if cached is not None:
        return cached
    if days == 1:
        url = COINGECKO_MARKET_CHART_URL.format(id=token_id, currency=currency)
    else:
        url = COINGECKO_MARKET_CHART_DAYS_URL.format(id=token_id, currency=currency, days=days)
    data = _fetch_json(url)
    _write_cache(cache_path, data)
    return data


def _get_hyperliquid_meta():
    cache_path = _cache_path("hyperliquid_meta", "meta")
    cached = _read_cache(cache_path, CACHE_TTL_SEC)
    if cached is not None:
        return cached
    data = _post_json(HYPERLIQUID_INFO_URL, {"type": "metaAndAssetCtxs"})
    _write_cache(cache_path, data)
    return data


def _hyperliquid_lookup(symbol):
    try:
        meta, ctxs = _get_hyperliquid_meta()
    except RuntimeError:
        return None, None
    universe = meta.get("universe", [])
    mapping = {}
    for idx, entry in enumerate(universe):
        name = str(entry.get("name", "")).upper()
        if name:
            mapping[name] = idx
    idx = mapping.get(symbol.upper())
    if idx is None or idx >= len(ctxs):
        return None, None
    return universe[idx], ctxs[idx]


def _pick_hyperliquid_interval_minutes(total_minutes):
    if total_minutes <= 180:
        return 1
    if total_minutes <= 360:
        return 3
    if total_minutes <= 720:
        return 5
    if total_minutes <= 1440:
        return 15
    if total_minutes <= 4320:
        return 30
    if total_minutes <= 10080:
        return 60
    if total_minutes <= 20160:
        return 120
    if total_minutes <= 40320:
        return 240
    if total_minutes <= 80640:
        return 480
    return 1440


def _interval_minutes_to_str(minutes):
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours}h"
    days = int(hours / 24)
    return f"{days}d"


def _get_hyperliquid_candles(symbol, total_minutes, interval_minutes):
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - int(total_minutes * 60 * 1000)
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": symbol.upper(),
            "interval": _interval_minutes_to_str(interval_minutes),
            "startTime": start_ms,
            "endTime": now_ms,
        },
    }
    data = _post_json(HYPERLIQUID_INFO_URL, payload)
    candles = []
    for row in data:
        try:
            ts_ms = int(row["t"])
            open_price = float(row["o"])
            high_price = float(row["h"])
            low_price = float(row["l"])
            close_price = float(row["c"])
        except (KeyError, TypeError, ValueError):
            continue
        candles.append((ts_ms, open_price, high_price, low_price, close_price))
    return candles


def _get_hyperliquid_meta():
    cache_path = _cache_path("hyperliquid_meta", "meta")
    cached = _read_cache(cache_path, CACHE_TTL_SEC)
    if cached is not None:
        return cached
    data = _post_json(HYPERLIQUID_INFO_URL, {"type": "metaAndAssetCtxs"})
    _write_cache(cache_path, data)
    return data


def _hyperliquid_lookup(symbol):
    try:
        meta, ctxs = _get_hyperliquid_meta()
    except RuntimeError:
        return None, None
    universe = meta.get("universe", [])
    mapping = {}
    for idx, entry in enumerate(universe):
        name = str(entry.get("name", "")).upper()
        if name:
            mapping[name] = idx
    idx = mapping.get(symbol.upper())
    if idx is None or idx >= len(ctxs):
        return None, None
    return universe[idx], ctxs[idx]


def _pick_hyperliquid_interval_minutes(total_minutes):
    if total_minutes <= 180:
        return 1
    if total_minutes <= 360:
        return 3
    if total_minutes <= 720:
        return 5
    if total_minutes <= 1440:
        return 15
    if total_minutes <= 4320:
        return 30
    if total_minutes <= 10080:
        return 60
    if total_minutes <= 20160:
        return 120
    if total_minutes <= 40320:
        return 240
    if total_minutes <= 80640:
        return 480
    return 1440


def _interval_minutes_to_str(minutes):
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours}h"
    days = int(hours / 24)
    return f"{days}d"


def _get_hyperliquid_candles(symbol, total_minutes, interval_minutes):
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - int(total_minutes * 60 * 1000)
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": symbol.upper(),
            "interval": _interval_minutes_to_str(interval_minutes),
            "startTime": start_ms,
            "endTime": now_ms,
        },
    }
    data = _post_json(HYPERLIQUID_INFO_URL, payload)
    candles = []
    for row in data:
        try:
            ts_ms = int(row["t"])
            open_price = float(row["o"])
            high_price = float(row["h"])
            low_price = float(row["l"])
            close_price = float(row["c"])
            volume = float(row.get("v", 0))
        except (KeyError, TypeError, ValueError):
            continue
        candles.append((ts_ms, open_price, high_price, low_price, close_price, volume))
    return candles


def _find_fractals(ohlc_rows, window=10, max_fractals=3):
    """Find true swing highs and lows.
    Swing high: highest high within window candles on both sides.
    Swing low: lowest low within window candles on both sides.
    Returns list of (index, type, price) where type is 'up' or 'down'.
    """
    if len(ohlc_rows) < window * 2 + 1:
        return []
    
    swing_highs = []
    swing_lows = []
    
    for i in range(window, len(ohlc_rows) - window):
        current_high = ohlc_rows[i][2]
        current_low = ohlc_rows[i][3]
        
        # Check if this is a swing high (highest high in the window)
        is_swing_high = True
        for j in range(i - window, i + window + 1):
            if j != i and ohlc_rows[j][2] >= current_high:
                is_swing_high = False
                break
        
        if is_swing_high:
            swing_highs.append((i, current_high))
        
        # Check if this is a swing low (lowest low in the window)
        is_swing_low = True
        for j in range(i - window, i + window + 1):
            if j != i and ohlc_rows[j][3] <= current_low:
                is_swing_low = False
                break
        
        if is_swing_low:
            swing_lows.append((i, current_low))
    
    # Sort by price extremity and take top N
    # For highs: sort by price descending (highest first)
    swing_highs.sort(key=lambda x: -x[1])
    # For lows: sort by price ascending (lowest first)  
    swing_lows.sort(key=lambda x: x[1])
    
    result = []
    for idx, price in swing_highs[:max_fractals]:
        result.append((idx, 'down', price))  # down arrow for resistance/high
    for idx, price in swing_lows[:max_fractals]:
        result.append((idx, 'up', price))  # up arrow for support/low
    
    return sorted(result, key=lambda x: x[0])


def _search_token_id(symbol):
    cache_path = _cache_path("search", symbol.upper())
    cached = _read_cache(cache_path, CACHE_TTL_SEC)
    if cached is None:
        data = _fetch_json(COINGECKO_SEARCH_URL.format(query=urllib.parse.quote(symbol)))
        _write_cache(cache_path, data)
    else:
        data = cached

    coins = data.get("coins", [])
    symbol_upper = symbol.upper()
    matches = [coin for coin in coins if coin.get("symbol", "").upper() == symbol_upper]
    if not matches:
        return None

    def _rank_key(coin):
        rank = coin.get("market_cap_rank")
        return rank if isinstance(rank, int) else 10**9

    matches.sort(key=_rank_key)
    return matches[0].get("id")


def _format_price(value):
    if value is None:
        return "n/a"
    if value >= 1:
        return f"{value:.2f}"
    return f"{value:.6f}"


def _build_candles_from_prices(price_points, hours, candle_minutes):
    if not price_points:
        return []
    price_points.sort(key=lambda row: row[0])
    last_ts = price_points[-1][0]
    start_ts = last_ts - (hours * 3600 * 1000)
    bucket_ms = candle_minutes * 60 * 1000
    candles = []
    bucket = None
    for ts, price in price_points:
        if ts < start_ts:
            continue
        bucket_start = (int(ts) // bucket_ms) * bucket_ms
        if bucket is None or bucket["bucket_start"] != bucket_start:
            if bucket is not None:
                candles.append((
                    bucket["bucket_start"],
                    bucket["open"],
                    bucket["high"],
                    bucket["low"],
                    bucket["close"],
                ))
            bucket = {
                "bucket_start": bucket_start,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
            }
        else:
            bucket["high"] = max(bucket["high"], price)
            bucket["low"] = min(bucket["low"], price)
            bucket["close"] = price
    if bucket is not None:
        candles.append((
            bucket["bucket_start"],
            bucket["open"],
            bucket["high"],
            bucket["low"],
            bucket["close"],
        ))
    return candles


def _parse_duration(args):
    for arg in args:
        cleaned = arg.strip().lower()
        match = re.match(r"^(\d+(?:\.\d+)?)([mhd])?$", cleaned)
        if not match:
            continue
        value = float(match.group(1))
        unit = match.group(2) or "h"
        if unit == "m":
            total_minutes = max(1.0, value)
            label = f"{int(value)}m" if value.is_integer() else f"{value}m"
        elif unit == "d":
            total_minutes = max(1.0, value * 24 * 60)
            label = f"{int(value)}d" if value.is_integer() else f"{value}d"
        else:
            total_minutes = max(1.0, value * 60)
            label = f"{int(value)}h" if value.is_integer() else f"{value}h"
        return total_minutes, label
    return float(DEFAULT_HOURS * 60), f"{DEFAULT_HOURS}h"


def _pick_candle_minutes(total_minutes):
    if total_minutes <= 360:
        return 5
    if total_minutes <= 1440:
        return 15
    if total_minutes <= 4320:
        return 30
    return 60


def _timestamp_to_datetime(ts_value):
    ts = float(ts_value)
    if ts >= 1e12:
        ts = ts / 1000.0
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _build_chart(symbol, ohlc_rows, currency, label, use_gradient=False):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle
        import matplotlib.font_manager as fm
        
        # Load custom font
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Tomorrow.ttf')
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            custom_font = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams['font.family'] = custom_font
    except Exception:
        return None

    if not ohlc_rows:
        return None

    # Check if we have volume data (6-element tuples)
    has_volume = len(ohlc_rows[0]) >= 6 if ohlc_rows else False
    
    if has_volume:
        fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(8, 9), facecolor="#121212",
                                          gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.05})
        ax_vol.set_facecolor("#121212")
    else:
        fig, ax = plt.subplots(figsize=(8, 8), facecolor="#121212")
        ax_vol = None
    
    ax.set_facecolor("#121212")

    times = [_timestamp_to_datetime(row[0]) for row in ohlc_rows]
    x_vals = mdates.date2num(times)
    widths = []
    if len(x_vals) > 1:
        delta = min(x_vals[i + 1] - x_vals[i] for i in range(len(x_vals) - 1))
        widths = [delta * 0.7] * len(x_vals)
    else:
        widths = [0.02] * len(x_vals)
        delta = 0.02

    lows = []
    highs = []
    volumes = []
    colors = []
    
    # Pre-calculate fractals
    fractals = _find_fractals(ohlc_rows)
    
    # Build sets of indices for swing coloring (only used in default mode)
    bullish_reversal_indices = set()
    bearish_reversal_indices = set()

    # Always include absolute high/low candles in coloring
    abs_high_idx = None
    abs_low_idx = None
    if ohlc_rows:
        abs_high_idx = max(range(len(ohlc_rows)), key=lambda i: ohlc_rows[i][2])
        abs_low_idx = min(range(len(ohlc_rows)), key=lambda i: ohlc_rows[i][3])

    if not use_gradient:
        for frac_idx, frac_type, frac_price in fractals:
            if frac_type == 'up':  # swing low = bullish reversal
                for off in range(0, 3):  # swing candle + 2 after = 3 total
                    if frac_idx + off < len(ohlc_rows):
                        bullish_reversal_indices.add(frac_idx + off)
            else:  # swing high = bearish reversal
                for off in range(0, 3):  # swing candle + 2 after = 3 total
                    if frac_idx + off < len(ohlc_rows):
                        bearish_reversal_indices.add(frac_idx + off)

        if abs_low_idx is not None:
            for off in range(0, 3):
                if abs_low_idx + off < len(ohlc_rows):
                    bullish_reversal_indices.add(abs_low_idx + off)
        if abs_high_idx is not None:
            for off in range(0, 3):
                if abs_high_idx + off < len(ohlc_rows):
                    bearish_reversal_indices.add(abs_high_idx + off)
    
    for idx, row in enumerate(ohlc_rows):
        if has_volume:
            _ts, open_price, high_price, low_price, close_price, volume = row
            volumes.append(volume)
        else:
            _ts, open_price, high_price, low_price, close_price = row[:5]
        
        is_bullish = close_price >= open_price
        x = x_vals[idx]
        width = widths[idx]
        lower = min(open_price, close_price)
        height = max(abs(close_price - open_price), 1e-9)
        
        if use_gradient:
            # Gradient mode: green gradient up, blue-purple gradient down
            wick_color = "#888888"
            border_color = "#000000"
            if is_bullish:
                color_top = "#84dc58"  # Bright green
                color_bottom = "#336d16"  # Dark green
            else:
                color_top = "#6c7ce4"  # Blue
                color_bottom = "#544996"  # Purple
            
            colors.append(color_top)
            wick = Line2D([x, x], [low_price, high_price], color=wick_color, linewidth=1.0, zorder=3)
            ax.add_line(wick)
            
            # Draw gradient candle body
            n_segments = 10
            segment_height = height / n_segments
            for seg in range(n_segments):
                t = seg / (n_segments - 1) if n_segments > 1 else 0
                r1, g1, b1 = int(color_bottom[1:3], 16), int(color_bottom[3:5], 16), int(color_bottom[5:7], 16)
                r2, g2, b2 = int(color_top[1:3], 16), int(color_top[3:5], 16), int(color_top[5:7], 16)
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                seg_color = f'#{r:02x}{g:02x}{b:02x}'
                seg_y = lower + seg * segment_height
                rect = Rectangle((x - width / 2, seg_y), width, segment_height, 
                                facecolor=seg_color, edgecolor='none', zorder=4)
                ax.add_patch(rect)
            border_rect = Rectangle((x - width / 2, lower), width, height, 
                                    facecolor='none', edgecolor=border_color, linewidth=0.5, zorder=5)
            ax.add_patch(border_rect)
        else:
            # Default mode: Grey + Cyan/Magenta for swings
            wick_color = "#808080"
            border_color = "#000000"
            up_normal = "#B0B0B0"
            down_normal = "#606060"
            up_reversal = "#00FFFF"
            down_reversal = "#FF00FF"
            
            if idx in bullish_reversal_indices:
                color = up_reversal
            elif idx in bearish_reversal_indices:
                color = down_reversal
            else:
                color = up_normal if is_bullish else down_normal
            
            colors.append(color)
            wick = Line2D([x, x], [low_price, high_price], color=wick_color, linewidth=1.0, zorder=3)
            ax.add_line(wick)
            rect = Rectangle((x - width / 2, lower), width, height, facecolor=color, edgecolor=border_color, linewidth=0.5, zorder=4)
            ax.add_patch(rect)
        
        lows.append(low_price)
        highs.append(high_price)

    # Draw fractals (already calculated above)
    price_range = max(highs) - min(lows) if highs and lows else 1
    offset = price_range * 0.02
    
    # Fractal colors based on mode
    frac_up_color = "#84dc58" if use_gradient else "#00FFFF"
    frac_down_color = "#6c7ce4" if use_gradient else "#FF00FF"
    
    for frac_idx, frac_type, frac_price in fractals:
        x = x_vals[frac_idx]
        if frac_type == 'down':  # bearish fractal - arrow down above high
            ax.plot(x, frac_price + offset * 0.5, marker='v', color=frac_down_color, markersize=6, zorder=5)
            ax.annotate(f'{frac_price:.2f}', xy=(x, frac_price + offset * 1.5),
                       fontsize=8, color='white', ha='center', va='bottom', zorder=6)
        else:  # bullish fractal - arrow up below low
            ax.plot(x, frac_price - offset * 0.5, marker='^', color=frac_up_color, markersize=6, zorder=5)
            ax.annotate(f'{frac_price:.2f}', xy=(x, frac_price - offset * 1.5),
                       fontsize=8, color='white', ha='center', va='top', zorder=6)

    # Always mark absolute high/low so at least one swing high/low is visible
    if highs and lows:
        abs_high_price = max(highs)
        abs_low_price = min(lows)
        abs_high_idx = highs.index(abs_high_price)
        abs_low_idx = lows.index(abs_low_price)

        abs_high_color = "#FFD54F"  # gold
        abs_low_color = "#90CAF9"   # light blue

        xh = x_vals[abs_high_idx]
        xl = x_vals[abs_low_idx]

        ax.plot(xh, abs_high_price + offset * 0.5, marker='v', color=abs_high_color, markersize=7, zorder=6)
        ax.annotate(f'{abs_high_price:.2f}', xy=(xh, abs_high_price + offset * 1.7),
                   fontsize=8, color='white', ha='center', va='bottom', zorder=7)

        ax.plot(xl, abs_low_price - offset * 0.5, marker='^', color=abs_low_color, markersize=7, zorder=6)
        ax.annotate(f'{abs_low_price:.2f}', xy=(xl, abs_low_price - offset * 1.7),
                   fontsize=8, color='white', ha='center', va='top', zorder=7)

    # Draw volume bars
    if has_volume and ax_vol and volumes:
        for idx, vol in enumerate(volumes):
            x = x_vals[idx]
            width = widths[idx]
            rect = Rectangle((x - width / 2, 0), width, vol, 
                            facecolor=colors[idx], edgecolor=colors[idx], alpha=0.7, zorder=3)
            ax_vol.add_patch(rect)
        
        ax_vol.set_xlim(min(x_vals) - delta, max(x_vals) + delta)
        ax_vol.set_ylim(0, max(volumes) * 1.1 if volumes else 1)
        ax_vol.set_ylabel("Volume", color="#8b949e", fontsize=9)
        ax_vol.tick_params(axis="x", colors="#8b949e")
        ax_vol.tick_params(axis="y", colors="#8b949e")
        for spine in ax_vol.spines.values():
            spine.set_color("#2a2f38")
        ax_vol.grid(True, linestyle="-", linewidth=0.6, color="#1f2630", alpha=0.8, zorder=1)
        
        # Format volume axis
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        ax_vol.xaxis.set_major_locator(locator)
        ax_vol.xaxis.set_major_formatter(formatter)
        ax.set_xticklabels([])  # Hide x labels on price chart
    
    ax.set_title(f"{symbol} last {label}", loc="center", fontsize=14, color="white", fontweight="bold", pad=12)
    if not has_volume:
        ax.set_xlabel("Time (UTC)", color="#8b949e")
    ax.set_ylabel(currency.upper(), color="#8b949e")

    ax.tick_params(axis="x", colors="#8b949e")
    ax.tick_params(axis="y", colors="#8b949e")
    for spine in ax.spines.values():
        spine.set_color("#2a2f38")

    ax.grid(True, linestyle="-", linewidth=0.6, color="#1f2630", alpha=0.8, zorder=1)

    if len(x_vals) > 1:
        ax.set_xlim(min(x_vals) - delta, max(x_vals) + delta)
    if lows and highs:
        min_y = min(lows)
        max_y = max(highs)
        pad = (max_y - min_y) * 0.08 if max_y > min_y else max_y * 0.01  # More padding for fractals
        ax.set_ylim(min_y - pad, max_y + pad)

    if not has_volume:
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(axis="x", labelrotation=0)

    # Highlight last price on Y-axis
    if ohlc_rows:
        last_close = ohlc_rows[-1][4]
        # Draw horizontal dashed line at last price
        ax.axhline(y=last_close, color='white', linestyle='--', linewidth=0.8, alpha=0.6)
        # Add price label on left side
        ax.annotate(f'{last_close:.2f}', xy=(ax.get_xlim()[0], last_close),
                   fontsize=9, color='white', fontweight='bold',
                   ha='right', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#0f141c', edgecolor='white', linewidth=1))

    ts = int(time.time())
    chart_path = f"/tmp/crypto_chart_{symbol}_{ts}.png"
    fig.tight_layout()
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    return chart_path


def _normalize_hl_symbol(symbol):
    sym = str(symbol or "").upper()
    # Strip common separators (e.g., BTC-USD, BTC/USDC)
    for sep in ("-", "/", "_"):
        if sep in sym:
            sym = sym.split(sep)[0]
            break
    # Strip common stablecoin suffixes (e.g., BTCUSDC)
    stable_suffixes = ("USDC", "USDH", "USDE", "USD", "USDT")
    for suf in stable_suffixes:
        if sym.endswith(suf) and len(sym) > len(suf):
            sym = sym[: -len(suf)]
            break
    return sym


def _hyperliquid_lookup(symbol):
    try:
        meta, ctxs = _get_hyperliquid_meta()
    except RuntimeError:
        return None, None
    universe = meta.get("universe", [])
    mapping = {}
    for idx, entry in enumerate(universe):
        name = str(entry.get("name", "")).upper()
        if name:
            mapping[name] = idx
    norm = _normalize_hl_symbol(symbol)
    idx = mapping.get(norm)
    if idx is None or idx >= len(ctxs):
        return None, None
    return universe[idx], ctxs[idx]


def main():
    if len(sys.argv) < 2:
        return _json_error("missing symbol", "Usage: get_price_chart.py <symbol>")

    raw_symbol = sys.argv[1].strip()
    if not raw_symbol:
        return _json_error("missing symbol", "Usage: get_price_chart.py <symbol>")

    symbol_upper = raw_symbol.upper()
    token_id = TOKEN_ID_MAP.get(symbol_upper)
    if token_id is None:
        token_id = raw_symbol.lower()

    total_minutes, label = _parse_duration(sys.argv[2:])
    # Check for gradient mode flag
    use_gradient = any(arg.lower() in ('gradient', 'grad', '-g', '--gradient') for arg in sys.argv[2:])
    hours = total_minutes / 60.0
    source = "coingecko"
    currency = "usdt"
    price_usdt = None
    hl_symbol = _normalize_hl_symbol(symbol_upper)
    hl_meta, hl_ctx = _hyperliquid_lookup(hl_symbol)
    if hl_ctx:
        source = "hyperliquid"
        currency = "usd"
        try:
            price_usdt = float(hl_ctx.get("markPx") or hl_ctx.get("midPx"))
        except (TypeError, ValueError):
            price_usdt = None
    if price_usdt is None:
        try:
            price_payload = _get_price(token_id, currency)
        except RuntimeError as exc:
            return _json_error("price lookup failed", str(exc))

        price_entry = price_payload.get(token_id, {})
        price_usdt = price_entry.get(currency)
        if price_usdt is None:
            currency = "usd"
            try:
                price_payload = _get_price(token_id, currency)
            except RuntimeError as exc:
                return _json_error("price lookup failed", str(exc))
            price_entry = price_payload.get(token_id, {})
            price_usdt = price_entry.get(currency)

        if price_usdt is None and token_id == raw_symbol.lower():
            try:
                searched_id = _search_token_id(symbol_upper)
            except RuntimeError as exc:
                return _json_error("token search failed", str(exc))
            if searched_id:
                token_id = searched_id
                currency = "usdt"
                try:
                    price_payload = _get_price(token_id, currency)
                except RuntimeError as exc:
                    return _json_error("price lookup failed", str(exc))
                price_entry = price_payload.get(token_id, {})
                price_usdt = price_entry.get(currency)
                if price_usdt is None:
                    currency = "usd"
                    try:
                        price_payload = _get_price(token_id, currency)
                    except RuntimeError as exc:
                        return _json_error("price lookup failed", str(exc))
                    price_entry = price_payload.get(token_id, {})
                    price_usdt = price_entry.get(currency)

    if price_usdt is None:
        return _json_error("token not found", f"CoinGecko id: {token_id}")

    candles = []
    candle_minutes = _pick_candle_minutes(total_minutes)
    if source == "hyperliquid":
        interval_minutes = _pick_hyperliquid_interval_minutes(total_minutes)
        candle_minutes = interval_minutes
        try:
            candles = _get_hyperliquid_candles(hl_symbol, total_minutes, interval_minutes)
        except RuntimeError:
            candles = []

    if not candles:
        try:
            days = max(1, int(math.ceil(total_minutes / 1440.0)))
            if days > 365:
                days = 365
            chart_payload = _get_market_chart(token_id, currency, days)
            price_points = chart_payload.get("prices", [])
            candles = _build_candles_from_prices(price_points, hours, candle_minutes)
        except RuntimeError:
            candles = []

    if not candles:
        candle_minutes = 30
        try:
            ohlc_payload = _get_ohlc(token_id, currency)
        except RuntimeError:
            ohlc_payload = []
        for row in ohlc_payload:
            if len(row) < 5:
                continue
            ts_ms, open_price, high_price, low_price, close_price = row
            candles.append((ts_ms, open_price, high_price, low_price, close_price))

    candles.sort(key=lambda item: item[0])
    if candles:
        target = max(2, int((hours * 60) / candle_minutes))
        target = int(target * 0.8)  # 20% fewer candles for breathing room
        last_points = candles[-target:]
    else:
        last_points = []

    change_period = None
    change_period_percent = None
    price_period_ago = None

    if len(last_points) >= 2:
        price_period_ago = last_points[0][4]
        if price_period_ago:
            change_period = price_usdt - price_period_ago
            change_period_percent = (change_period / price_period_ago) * 100
    chart_path = _build_chart(symbol_upper, last_points, currency, label, use_gradient)

    if change_period_percent is None:
        change_text = f"{label} n/a"
    else:
        if change_period_percent >= 0:
            emoji = "⬆️"
            sign = "+"
        else:
            emoji = "🔻"
            sign = ""
        change_text = f"{emoji} {sign}{change_period_percent:.2f}% over {label}"

    text = f"{symbol_upper}: ${_format_price(price_usdt)} {currency.upper()} {change_text}"
    text = text.replace("*", "")
    result = {
        "symbol": symbol_upper,
        "token_id": token_id,
        "source": source,
        "currency": currency.upper(),
        "hours": hours,
        "duration_label": label,
        "candle_minutes": candle_minutes,
        "price": price_usdt,
        "price_usdt": price_usdt,
        "change_12h": change_period,
        "change_12h_percent": change_period_percent,
        "change_period": change_period,
        "change_period_percent": change_period_percent,
        "chart_path": chart_path,
        "text": text,
        "text_plain": text,
    }
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
