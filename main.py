import re
import time
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor
def is_valid(email: str) -> bool:
    email = normalize_email(email)
    if ("@" not in email):
        return False

    # .partition('@') split into: (before, '@', after)
    local, at_sign, domain = email.partition("@")

    # If there was no @ sign, or nothing after the @ sign, reject it
    if not at_sign or not domain:
        return False

    local = unicodedata.normalize("NFC", local)
    domain = normalize_domain(domain)
    email = local + "@" + domain

    if domain.startswith("[") and domain.endswith("]"):
        return bool(local) and is_valid_local(local) and is_valid_ip_literal(domain)

    if not is_valid_email(email) or not is_valid_RFC(email):
        return False

    return is_valid_idna(domain)
def normalize_domain(domain):
    for sep in ("\u3002", "\uff0e", "\uff61"):
        domain = domain.replace(sep, ".")
    return unicodedata.normalize("NFC", domain)

_IGNORE_CHARS = {"\u00ad", "\u200b", "\u2060", "\ufeff"} | {chr(c) for c in range(0xfe00, 0xfe10)}

def normalize_email(email):
    email = email.replace("\uff20", "@")
    out = []
    for c in email:
        if c in _IGNORE_CHARS:
            continue
        if unicodedata.category(c) == "Zs":
            out.append(" ")
        else:
            out.append(c)
    return "".join(out)

def _last_non_nsm(types):
    for t in reversed(types):
        if t != "NSM":
            return t
    return None

def _passes_bidi(label):
    if not label:
        return True
    types = [unicodedata.bidirectional(c) for c in label]
    first = types[0]
    if first in ("R", "AL"):
        allowed = {"R", "AL", "AN", "EN", "ES", "CS", "ET", "ON", "BN", "NSM"}
        if any(t not in allowed for t in types):
            return False
        if _last_non_nsm(types) not in ("R", "AL", "EN", "AN"):
            return False
        if "EN" in types and "AN" in types:
            return False
        return True
    if first == "L":
        allowed = {"L", "EN", "ES", "CS", "ET", "ON", "BN", "NSM"}
        if any(t not in allowed for t in types):
            return False
        if _last_non_nsm(types) not in ("L", "EN"):
            return False
        return True
    return False

def bidi_ok(domain):
    labels = []
    for lbl in domain.split("."):
        if lbl[:4].lower() == "xn--":
            decoded = punycode_decode(lbl[4:])
            labels.append(decoded if decoded else lbl)
        else:
            labels.append(lbl)
    has_rtl = any(unicodedata.bidirectional(c) in ("R", "AL", "AN") for lbl in labels for c in lbl)
    if not has_rtl:
        return True
    return all(_passes_bidi(lbl) for lbl in labels)
def _build_marks():
    out, start, prev = [], None, None
    for cp in range(0x300, 0x20000):
        if unicodedata.category(chr(cp))[0] == "M":
            if start is None:
                start = cp
            prev = cp
        elif start is not None:
            out.append((start, prev))
            start = None
    if start is not None:
        out.append((start, prev))
    return "".join("\\U%08x" % a if a == b else "\\U%08x-\\U%08x" % (a, b) for a, b in out)

_MARKS = _build_marks()
_LOCAL_CHARS = r"[\w!#$%&'*+/=?^_`{|}~" + _MARKS + "-]"
_QUOTED = r'"(?:[^"\\]|\\.)*"'
_UNQUOTED = _LOCAL_CHARS + r"+(?:\." + _LOCAL_CHARS + r"+)*"
_LOCAL_PART = r"(?:" + _UNQUOTED + r"|" + _QUOTED + r")"
_DCHAR = r"(?:[^\W_]|[" + _MARKS + r"])"
_TLDCHAR = r"(?:[^\W\d_]|[" + _MARKS + r"])"
_LABEL = _DCHAR + r"(?:(?:" + _DCHAR + r"|-)*" + _DCHAR + r")?"
_DOMAIN_PART = _LABEL + r"(?:\." + _LABEL + r")*\.(?:" + _TLDCHAR + r"{2,}|xn--[a-zA-Z0-9]{2,})"
_RFC_RE = re.compile(r"^" + _LOCAL_PART + r"@" + _DOMAIN_PART + r"$", re.UNICODE)
_LOCAL_RE = re.compile(r"^" + _LOCAL_PART + r"$", re.UNICODE)

def is_valid_RFC(email):
    return bool(_RFC_RE.match(email))
test_cases = {
    # Valid Cases
    "café@müller.de": True,
    "тест@почта.рф": True,
    "ユーザー@メール.クック": True,
    "user.name+tag@example.com": True,
    '"user..name"@example.com': True,
    "xn--4gbrim@xn--wgbh1c.xn--mgbaam7a8h": True,
    
    # Invalid Cases
    "user..name@example.com": False,
    "user@example.123": False,
    "user@exam_ple.com": False,
    "user@example.": False,
    "@example.com": False,
    "user@example.c": False
}
# Run tracking variables
passed_tests = 0
failed_tests = 0
print(" Starting Basic Test Suite Run...\n")
# Summary Blocks
print("\n=== Test Run Summary ===")
print(f"Total Tests Run: {len(test_cases)}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
# Exit protocol to mirror structural frameworks
if failed_tests > 0:
    print("\n Build Status: FAILED")
else:
    print("\n Build Status: SUCCESS")
def is_valid_email(email):
    local,domain = email.split('@',1)
    labels = domain.split('.')
    tld = labels[-1]
    if tld.isdigit():
        return False
    if ((len(local.encode('utf-8'))) <= 64 and (len(domain.encode('utf-8')) <= 255)):
        return True
    else:
        return False

def is_valid_local(local):
    if len(local.encode("utf-8")) > 64:
        return False
    return bool(_LOCAL_RE.match(local))

def is_valid_ip_literal(domain):
    inner = domain[1:-1]
    if inner[:5].lower() == "ipv6:":
        return is_valid_ipv6(inner[5:])
    return is_valid_ipv4(inner)

def is_valid_ipv4(text):
    parts = text.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if len(part) > 1 and part[0] == "0":
            return False
        if int(part) > 255:
            return False
    return True

def is_valid_ipv6(text):
    if "." in text:
        head, sep, tail = text.rpartition(":")
        if not sep or not is_valid_ipv4(tail):
            return False
        text = head + ":0:0"
    if text.count("::") > 1:
        return False
    groups = [g for g in text.split(":") if g != ""]
    for g in groups:
        if len(g) > 4 or any(c not in "0123456789abcdefABCDEF" for c in g):
            return False
    if "::" in text:
        return len(groups) <= 8
    return len(groups) == 8

def is_valid_idna(domain):
    if not bidi_ok(domain):
        return False
    for label in domain.split("."):
        if label == "":
            return False
        if label[:4].lower() == "xn--":
            decoded = punycode_decode(label[4:])
            if decoded is None or decoded == "":
                return False
            reencoded = punycode_encode(decoded)
            if reencoded is None or reencoded.lower() != label[4:].lower():
                return False
            if len(label) > 63:
                return False
        elif label.isascii():
            if len(label) > 63:
                return False
        else:
            encoded = punycode_encode(label)
            if encoded is None or len("xn--" + encoded) > 63:
                return False
    return True

def punycode_decode(s):
    try:
        return s.encode("ascii").decode("punycode")
    except Exception:
        return None

def punycode_encode(label):
    try:
        return label.encode("punycode").decode("ascii")
    except Exception:
        return None


class RateLimiter:
    def __init__(self, max_calls=5, period=1.0):
        self.max_calls = max_calls
        self.period = period
        self.rate = max_calls / period
        self._buckets = {}
        self._lock = threading.Lock()

    def allow(self, key):
        now = time.monotonic()
        with self._lock:
            tokens, last = self._buckets.get(key, (self.max_calls, now))
            tokens = min(self.max_calls, tokens + (now - last) * self.rate)
            if tokens >= 1:
                self._buckets[key] = (tokens - 1, now)
                return True
            self._buckets[key] = (tokens, now)
            return False


rate_limiter = RateLimiter()


def validate(email, user="global"):
    if not rate_limiter.allow(user):
        return None
    return is_valid(email)


def validate_many(items, max_workers=8):
    def work(item):
        if isinstance(item, tuple):
            return validate(item[1], item[0])
        return is_valid(item)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(work, items))
if __name__ == "__main__":
    test_cases = [
        ("test@example.com", True),
        ("user@domain.co.uk", True),
        ("plain_text_no_at_sign", False),  # Will now safely return False instead of crashing
        ("@no_username.com", True),
    ]
    print("--- Starting Tests ---")
    for email, expected in test_cases:
        result = is_valid(email)
        status = "PASSED" if result == expected else "FAILED"
        print(f"Input: '{email:<25}' -> Result: {str(result):<5} (Expected: {str(expected):<5}) [{status}]")
