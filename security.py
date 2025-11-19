import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def mask_contact(contact: str) -> str:
    s = ''.join(ch for ch in contact if ch.isdigit())
    if len(s) >= 4:
        return "XXX-XXX-" + s[-4:]
    return "XXX-XXX-XXXX"

def anonymize_name(name: str) -> str:
    h = hashlib.sha256(name.encode()).hexdigest()[:6]
    return f"ANON_{h}"

