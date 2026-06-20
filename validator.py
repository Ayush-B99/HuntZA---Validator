import re

def is_valid_email(email):
    # determine whether invalid start of string (.. is illegal)
    no_dot_chars = r'[\w_%+-]'
    unquoted_local =  rf'{no_dot_chars}+(?:\.{no_dot_chars}+)*'
    
    # if wrapped in "" not as strict by RFC but it must end in " or it is illegal
    quoted_content = r'(?:[^"\\]|\\.)*'
    quoted_local = rf'"{quoted_content}"'

    # or for if "" or not
    local_part = rf'(?:{unquoted_local}|{quoted_local})'

    # characters only no numbers or underscores etc
    domain_label = r"[\w](?:[\w-]*[\w])?"
    tld = r"[^\W\d_]{2,}"

    domain_part = rf"{domain_label}(?:\.{domain_label})*\.{tld}"

    pattern = rf'^{local_part}@{domain_part}$'

    if re.match(pattern, email, re.UNICODE):
        return True
    return False


