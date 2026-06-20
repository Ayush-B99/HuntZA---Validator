import re
import ipaddress
import dns.resolver
from validator import is_valid_email 
from validator import is_valid_RFC

def is_valid(email: str) -> bool:

    if ("@" not in email):
        return False
    
    # 1. Run your imported validation checks
    if not is_valid_email(email) or not is_valid_RFC(email):
        return False

    # 2. Extract the domain safely without risking an IndexError
    # .partition('@') split into: (before, '@', after)
    _, at_sign, domain = email.partition("@")
    
    # If there was no @ sign, or nothing after the @ sign, reject it
    if not at_sign or not domain:
        return False

    # 3. Check DNS configuration
    if not has_valid_dns(domain):
        return False

    return True


def has_valid_dns(domain: str) -> bool:  # Fixed type hint from list to bool
    try:
        dns.resolver.resolve(domain, 'MX', lifetime=3.0)
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        try:
            dns.resolver.resolve(domain, 'A', lifetime=3.0)
            return True
        except Exception:
            return False
    except Exception:
        return False


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