import re
import sys

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

    if(labels.startswith("-") and labels.endswith("-")):
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validator.py <email_address>")
        sys.exit(1)

input_email = sys.argv[1] 

if is_valid_email(input_email):
     print(f"true.")
else: 
    print(f"false")

