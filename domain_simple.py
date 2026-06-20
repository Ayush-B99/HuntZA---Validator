import re
import unicodedata


def label_check(label : str) -> bool:
    label_len = len(label.encode("utf-8"))
    if  (label_len < 1 or label_len > 63):
        return False
    if(label.startswith("-") or label.endswith("-")):
        return False
    return True

def domain_check(domain: str) -> bool:
    domain_len = len (domain)
    if (domain_len < 1 or domain_len> 255):
        return False
    
    labels = domain.split('.')
    labels_len = len(labels)
    if(labels_len < 2):
        return False 

    for label in labels:
        if not label_check(label):
            return False
    
    tld = labels[-1]

    if tld.isdigit():
        return False
    
    return True 

domains = ["example.com", "-example.com", "example-.com", "-example-.com-", ""]
for domain in domains:
    if domain_check(domain):
        print("pass")
    else:
        print ("failed")

 