"""Password hashing for Campus Customs accounts.

Matches the seeded db format `pbkdf2_sha256$<salt>$<hex digest>` (verified
against the seeded test user, whose password is "password"): PBKDF2-HMAC-SHA256
over the UTF-8 password with a per-user random salt, 120,000 iterations.
"""
import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS)
    return f"{ALGORITHM}${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, hex_digest = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS)
    return hmac.compare_digest(candidate.hex(), hex_digest)
