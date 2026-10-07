"""Optional product-photo search. No model calls, downloads, or browser credentials."""
import os
import re
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from threading import Thread
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from modules.utilities.performance import memoized


def configuration():
    return {"configured": bool(os.getenv("UNSPLASH_ACCESS_KEY", "").strip()), "provider": "Unsplash"}


def _allowed_url(url, host):
    return isinstance(url, str) and urlsplit(url).scheme == "https" and urlsplit(url).hostname == host


def _credit_url(url):
    parts = urlsplit(url)
    params = dict(parse_qsl(parts.query))
    params.update(utm_source="jinie", utm_medium="referral")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), ""))


def _search(query):
    response = httpx.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 5, "content_filter": "high", "order_by": "relevant"},
        headers={"Authorization": "Client-ID " + os.environ["UNSPLASH_ACCESS_KEY"], "Accept-Version": "v1"},
        timeout=httpx.Timeout(2.0, connect=0.75),
    )
    response.raise_for_status()
    return response.json().get("results", [])


@memoized(maxsize=32, ttl=600)
def _search_batch(queries, credential_digest):
    # Independent searches run together. Exceptions aren't retained in the cache.
    with ThreadPoolExecutor(max_workers=4) as pool:
        return dict(zip(queries, pool.map(_search, queries)))


def _track(download_urls):
    def track(url):
        try:
            httpx.get(url, headers={"Authorization": "Client-ID " + os.environ["UNSPLASH_ACCESS_KEY"]}, timeout=1.0).raise_for_status()
        except (httpx.HTTPError, KeyError):
            pass
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(track, download_urls))


# Product photography: searches short product labels, saves stable URLs and credits, and retains existing photos if search fails.
def assign_product_images(spec):
    """Save one stable selection per product, retaining original images on failure."""
    catalog = spec.get("products", [])
    result = {"provider": "existing catalog", "matched": 0, "fallback": len(catalog)}
    key = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
    if not key or not catalog:
        return result
    # Search only short product labels, never the customer's full/private brief.
    def query(item):
        words = re.findall(r"[\w-]+", str(item.get("name", "")) + " " + str(item.get("category", "")))
        return " ".join(words[:16])
    queries = list(dict.fromkeys(query(item) for item in catalog if query(item)))[:4]
    try:
        matches = _search_batch(tuple(queries), sha256(key.encode()).hexdigest())
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        result["status"] = "Search unavailable; existing photos retained."
        return result
    used, downloads = set(), []
    for item in catalog:
        for photo in matches.get(query(item), []):
            url = photo.get("urls", {}).get("small", "")
            user = photo.get("user", {})
            profile = user.get("links", {}).get("html", "")
            page = photo.get("links", {}).get("html", "")
            download = photo.get("links", {}).get("download_location", "")
            if photo.get("id") in used or not (
                _allowed_url(url, "images.unsplash.com") and _allowed_url(profile, "unsplash.com")
                and _allowed_url(page, "unsplash.com") and _allowed_url(download, "api.unsplash.com")
                and user.get("name")
            ):
                continue
            item["image_url"] = url  # Preserve Unsplash's tracking parameters.
            item["image_credit"] = {"name": user["name"], "url": _credit_url(profile), "source_url": _credit_url(page)}
            used.add(photo.get("id"))
            downloads.append(download)
            result["matched"] += 1
            break
    result.update(provider="Unsplash", fallback=len(catalog) - result["matched"])
    if downloads:
        Thread(target=_track, args=(downloads,), daemon=True, name="jinie-photo-tracking").start()
    return result
