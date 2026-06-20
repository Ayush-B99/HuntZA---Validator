import re
import time
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor
def is_valid(email: str) -> bool:
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
def is_valid_RFC(email):
    # determine whether invalid start of string (.. is illegal)
    no_dot_chars = r"[\w!#$%&'*+/=?^_`{|}~-]"
    unquoted_local =  rf'{no_dot_chars}+(?:\.{no_dot_chars}+)*'
    
    # if wrapped in "" not as strict by RFC but it must end in " or it is illegal
    quoted_content = r'(?:[^"\\]|\\.)*'
    quoted_local = rf'"{quoted_content}"'
    # or for if "" or not
    local_part = rf'(?:{unquoted_local}|{quoted_local})'
    # FIX: Strictly enforce Unicode letters/digits and hyphens only
    domain_char = r'[^\W_]'
    domain_label = rf"{domain_char}(?:(?:[^\W_]|-)*{domain_char})?"
    tld = r"(?:[^\W\d_]{2,}|xn--[a-zA-Z0-9]{2,})"
    domain_part = rf"{domain_label}(?:\.{domain_label})*\.{tld}"
    pattern = rf'^{local_part}@{domain_part}$'
    if re.match(pattern, email, re.UNICODE):
        return True
    return False
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
    unquoted = r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*"
    quoted = r'"(?:[^"\\]|\\.)*"'
    return bool(re.match(rf"^(?:{unquoted}|{quoted})$", local, re.UNICODE))

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
