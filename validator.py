import re

import re

def is_valid(email):
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

print("🚀 Starting Basic Test Suite Run...\n")

for email, expected in test_cases.items():
    actual_result = is_valid(email)
    
    if actual_result == expected:
        print(f"✅ PASS | '{email}' behaved as expected ({expected}).")
        passed_tests += 1
    else:
        print(f"❌ FAIL | '{email}' expected {expected}, but returned {actual_result}.")
        failed_tests += 1

# Summary Blocks
print("\n=== Test Run Summary ===")
print(f"Total Tests Run: {len(test_cases)}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")

# Exit protocol to mirror structural frameworks
if failed_tests > 0:
    print("\n🚨 Build Status: FAILED")
else:
    print("\n🎉 Build Status: SUCCESS")


