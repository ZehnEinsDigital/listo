"""Redirect the engine's Amazon SP-API calls to the Listo CLOUD gateway (W6-T1).

In Richtung B the engine runs on the CUSTOMER's machine, but Amazon credentials and
every SP-API call MUST stay server-side. This shim makes that transparent: when
``LISTO_GATEWAY=true`` (see the sibling ``sitecustomize.py``), it monkeypatches the
engine's ``core.amazon_api.AmazonAPI`` so each method calls the Listo cloud over HTTP
instead of Amazon — so the engine needs NO local ``AMAZON_SP_*`` creds at all.

It MUST be self-contained (stdlib only — HTTP via ``urllib.request``, no hard
``requests`` dependency) so it works in a subprocess whose ``sys.path`` is just the
shim dir + site-packages, and it MUST NEVER raise at import time (``sitecustomize``
failing would break the interpreter). All failures happen inside ``activate()`` or the
patched methods, never at import.

Mirrors the proven pattern in ``runner/runner/_dryrun_shim/dryrun_guard.py``:
never-raise-at-import, idempotent monkeypatch, plus a ``requests.Session.send``
backstop. That backstop refuses any direct Amazon egress made through ``requests`` —
which is how the engine performs every SP-API / LWA call, so the engine's own egress is
blocked. It does NOT catch a hand-rolled ``urllib`` / ``http.client`` call straight to
SP-API (those bypass ``requests.Session.send`` entirely) — the same known limitation as
the dry-run shim. The primary protection is the method monkeypatch; the backstop is a
defence-in-depth net for the engine's ``requests`` traffic.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

VALIDATION_PREVIEW = "VALIDATION_PREVIEW"
_DEFAULT_API_URL = "https://api.listo.app"
_DEFAULT_MARKETPLACE = "DE"
_TIMEOUT = 60

# Resolved once, then cached for the life of the process (avoids a /v1/credentials
# round-trip on every patched call).
_credential_id: str | None = None


# ---- Listo cloud config (read lazily, never at import) ----------------------


def _api_url() -> str:
    return (os.environ.get("LISTO_API_URL") or _DEFAULT_API_URL).rstrip("/")


def _api_key() -> str:
    return os.environ.get("LISTO_API_KEY", "")


def _marketplace() -> str:
    return os.environ.get("LISTO_MARKETPLACE") or _DEFAULT_MARKETPLACE


# ---- error mapping ----------------------------------------------------------
# Preserve the engine's catch contract: engine code does ``except AmazonAPIError`` /
# ``except AmazonAuthError`` around SP-API calls, so gateway failures must raise THOSE
# types to flow through the engine's existing error handling. If the engine isn't
# importable (e.g. in tests), fall back to RuntimeError.


def _engine_exc(auth: bool):  # noqa: ANN201
    """Return the engine's exception class to raise (or RuntimeError as a fallback).

    ``auth=True`` -> ``AmazonAuthError`` (401/403); else ``AmazonAPIError``.
    """
    try:
        import importlib

        module = importlib.import_module("core.amazon_api")
        name = "AmazonAuthError" if auth else "AmazonAPIError"
        exc = getattr(module, name, None)
        if isinstance(exc, type) and issubclass(exc, Exception):
            return exc
    except Exception:
        pass
    return RuntimeError


# ---- HTTP helpers (stdlib urllib only) --------------------------------------


def _request(method: str, path: str, *, params: dict | None = None, body: dict | None = None):
    """Call the Listo cloud and return the decoded-JSON response.

    ``Authorization: Bearer {LISTO_API_KEY}`` is sent on every request. JSON bodies
    are POSTed; query params are URL-encoded onto the path.

    Error handling (never leaks the LISTO_API_KEY):
    - HTTP 4xx/5xx -> read the cloud's response body, surface its JSON ``detail``;
      402 gets a "reactivate your plan" hint; 401/403 raise ``AmazonAuthError``,
      everything else raises ``AmazonAPIError`` (engine catch contract preserved).
    - Network/DNS failure -> a clear "could not reach the Listo cloud" error.
    """
    url = _api_url() + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = None
    headers = {"Authorization": f"Bearer {_api_key()}", "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise _http_error(e) from None
    except urllib.error.URLError as e:
        # Network / DNS down — the cloud was never reached.
        reason = getattr(e, "reason", e)
        raise _engine_exc(auth=False)(
            f"Listo gateway: could not reach the Listo cloud ({reason})."
        ) from None
    return json.loads(raw.decode("utf-8")) if raw else None


def _http_error(e: urllib.error.HTTPError) -> Exception:
    """Build a clear, key-free exception from an HTTPError, surfacing the cloud detail.

    The cloud returns errors as JSON ``{"detail": "..."}``; we read and include that so
    the user sees the actual reason instead of a bare ``HTTP 4xx``. 402 (subscription
    inactive) gets a reactivation hint. The exception TYPE follows the engine's catch
    contract: 401/403 -> AmazonAuthError, else AmazonAPIError.
    """
    status = e.code
    detail = ""
    try:
        payload = json.loads(e.read().decode("utf-8"))
        if isinstance(payload, dict):
            detail = str(payload.get("detail") or "")
    except Exception:
        detail = ""

    if status == 402:
        msg = (
            "Your Listo subscription is inactive — reactivate your plan to keep using "
            "Listo."
        )
        if detail:
            msg += f" ({detail})"
    elif status in (401, 403):
        msg = "Listo gateway: authentication failed (HTTP %d)" % status
        msg += f": {detail}" if detail else " — check your Listo API key."
    else:
        msg = f"Listo gateway: cloud returned HTTP {status}"
        if detail:
            msg += f": {detail}"

    return _engine_exc(auth=status in (401, 403))(msg)


def _resolve_credential_id() -> str:
    """Find the Amazon credential id stored in the Listo vault, cached after first call.

    Lists ``/v1/credentials`` and picks the entry whose ``marketplace == "amazon"``.
    Raises a clear ``RuntimeError`` if none exists (the user must store Amazon creds
    in the Listo vault first).
    """
    global _credential_id
    if _credential_id is not None:
        return _credential_id
    creds = _request("GET", "/v1/credentials") or []
    for entry in creds:
        if isinstance(entry, dict) and entry.get("marketplace") == "amazon":
            _credential_id = str(entry["id"])
            return _credential_id
    raise RuntimeError(
        "No Amazon credential found in the Listo vault. Store your Amazon SP-API "
        "credentials in Listo (marketplace 'amazon') before running the engine via "
        "the gateway."
    )


# ---- redirected method implementations --------------------------------------
# Signatures mirror engine/core/amazon_api.py exactly. ``self`` is the bare engine
# instance (unused — every call is redirected to the Listo cloud).


def _search_product_types(self, marketplace_id=None, keywords=None, force_refresh=False):  # noqa: ANN001
    params = {"credential_id": _resolve_credential_id(), "marketplace": _marketplace()}
    if keywords:
        params["keywords"] = ",".join(keywords)
    out = _request("GET", "/v1/amazon/product-types", params=params)
    return (out or {}).get("product_types", [])  # engine contract: List[str]


def _get_product_type_definition(self, product_type, marketplace_id=None, force_refresh=False):  # noqa: ANN001
    params = {"credential_id": _resolve_credential_id(), "marketplace": _marketplace()}
    quoted = urllib.parse.quote(str(product_type), safe="")
    return _request("GET", f"/v1/amazon/product-type/{quoted}", params=params)


def _get_listings_item(self, seller_id, sku, marketplace_ids, included_data=None):  # noqa: ANN001
    # CONTRACT NARROWING: the real engine method supports the full Listings Items
    # GET (summaries/attributes/issues/offers via ``included_data``). The current
    # gateway only exposes the ISSUES subset (``/v1/amazon/listings/{sku}/issues``),
    # so ``included_data`` is intentionally IGNORED and we always return issues only.
    # Richer included_data would require a new gateway endpoint — NOT built here.
    params = {"credential_id": _resolve_credential_id(), "marketplace": _marketplace()}
    quoted = urllib.parse.quote(str(sku), safe="")
    return _request("GET", f"/v1/amazon/listings/{quoted}/issues", params=params)


def _write(op: str, sku, body, mode=None):  # noqa: ANN001
    """Shared put/patch/delete writer. VALIDATION_PREVIEW -> /validate, else /submit."""
    payload = {
        "credential_id": _resolve_credential_id(),
        "marketplace": _marketplace(),
        "sku": sku,
        "op": op,
    }
    if body is not None:
        payload["body"] = body
    path = "/v1/amazon/validate" if (mode or "").upper() == VALIDATION_PREVIEW else "/v1/amazon/submit"
    return _request("POST", path, body=payload)


def _put_listings_item(self, seller_id, sku, marketplace_ids, body, mode=None):  # noqa: ANN001
    return _write("put", sku, body, mode=mode)


def _patch_listings_item(self, seller_id, sku, marketplace_ids, body, mode=None):  # noqa: ANN001
    return _write("patch", sku, body, mode=mode)


def _delete_listings_item(self, seller_id, sku, marketplace_ids):  # noqa: ANN001
    return _write("delete", sku, None, mode=None)


_METHODS = {
    "search_product_types": _search_product_types,
    "get_product_type_definition": _get_product_type_definition,
    "get_listings_item": _get_listings_item,
    "put_listings_item": _put_listings_item,
    "patch_listings_item": _patch_listings_item,
    "delete_listings_item": _delete_listings_item,
}


# ---- activation --------------------------------------------------------------


def _patch_engine_amazon_api() -> bool:
    """Patch ``core.amazon_api.AmazonAPI`` methods + ``from_instance`` in place.

    Best-effort: if the engine isn't importable yet the requests backstop still
    protects egress. Returns True if the class was patched. Idempotent.
    """
    import importlib

    module = importlib.import_module("core.amazon_api")
    cls = getattr(module, "AmazonAPI", None)
    if cls is None:
        return False
    if getattr(cls, "_listo_gateway_patched", False):
        return True

    for name, fn in _METHODS.items():
        setattr(cls, name, fn)

    # from_instance must return an instance EVEN WHEN AMAZON_SP_* are missing (the real
    # engine raises AmazonAuthError there). Creds are unused — every method is redirected.
    # Signature matches the engine's classmethod: (cls, instance_config, **kwargs).
    def _from_instance(klass, instance_config, **kwargs):  # noqa: ANN001
        return klass.__new__(klass)

    cls.from_instance = classmethod(_from_instance)
    cls._listo_gateway_patched = True
    return True


def _install_requests_backstop() -> bool:
    """Patch ``requests.Session.send`` to REFUSE any direct Amazon SP-API / LWA egress.

    Best-effort and guarded: if ``requests`` isn't importable, skip gracefully. Mirrors
    the dry-run shim's single-chokepoint backstop so a hand-rolled HTTP call can't bypass
    the gateway. Idempotent.
    """
    try:
        import functools

        import requests.sessions as _sessions
    except Exception:
        return False

    if getattr(_sessions.Session, "_listo_gateway_guarded", False):
        return True
    original_send = _sessions.Session.send

    @functools.wraps(original_send)
    def guarded_send(self, request, **kwargs):  # noqa: ANN001
        url = getattr(request, "url", "") or ""
        host = urllib.parse.urlparse(url).netloc.lower()
        if "sellingpartnerapi" in host or "api.amazon.com/auth" in url.lower():
            raise RuntimeError(
                "Listo gateway: direct Amazon SP-API is not allowed; use the Listo "
                f"gateway (refused {request.method} {url})."
            )
        return original_send(self, request, **kwargs)

    _sessions.Session.send = guarded_send
    _sessions.Session._listo_gateway_guarded = True
    return True


def activate() -> list[str]:
    """Install the gateway redirect + egress backstop. Returns which layers installed.

    Safe to call more than once. Each layer is independently guarded so a failure in
    one (e.g. the engine not importable yet) never blocks the other.
    """
    installed: list[str] = []
    try:
        if _patch_engine_amazon_api():
            installed.append("engine")
    except Exception:
        pass
    try:
        if _install_requests_backstop():
            installed.append("requests")
    except Exception:
        pass
    return installed
