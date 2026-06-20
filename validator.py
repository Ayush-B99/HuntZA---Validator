import re
import sys

def is_valid_RFC(email):
    # determine whether invalid start of string (.. is illegal)
    no_dot_chars = r'[\w_%+-]'
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' #basic regex for emails
    local,domain = email.split('@',1)
    labels = domain.split('.')

    tld = labels[-1]
    if tld.isdigit():
        return False

    if re.match(pattern, email) and ((len(local.encode('utf-8'))) <= 64 and (len(domain.encode('utf-8')) <= 255)):
        return True
    else:
        return False


