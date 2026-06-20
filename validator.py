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

    # characters only no numbers or underscores etc
    domain_char = r'[^\W_]'
    domain_label = rf"{domain_char}(?:[\w-]*{domain_char})?"

    tld = r"(?:[^\W\d_]{2,}|xn--[a-zA-Z0-9]{2,})"

    domain_part = rf"{domain_label}(?:\.{domain_label})*\.{tld}"

    pattern = rf'^{local_part}@{domain_part}$'

    if re.match(pattern, email, re.UNICODE):
        return True
    return False


