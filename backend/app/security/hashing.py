import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches its hashed representation using native bcrypt.
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Generates a secure cryptographically hashed password using native bcrypt.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
