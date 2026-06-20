import re
import ipaddress
import dns.resolver

def is_valid(email: str) -> bool:

    domain = email.split("@", 1)[1]

    if (has_valid_dns(domain) == False):
        return False

    return True


def has_valid_dns(domain: str) -> list:
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
    # Test cases: (Input string, Expected result)
    test_cases = [
        ("test@example.com", True),
        ("user@domain.co.uk", True),
        ("plain_text_no_at_sign", False),  # CRASHES current code: IndexError
        ("@no_username.com", True),
    ]

    print("--- Starting Tests ---")
    for email, expected in test_cases:
        try:
            result = is_valid(email)
            print(f"Input: '{email}' -> Result: {result} (Expected: {expected})")
        except IndexError:
            print(f"Input: '{email}' -> CRASHED with IndexError!")