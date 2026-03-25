from cryptography.fernet import Fernet

from src.backend.config import settings

_fernet = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.NOTION_ENCRYPTION_KEY
        if not key:
            raise RuntimeError(
                "NOTION_ENCRYPTION_KEY is not set. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        _fernet = Fernet(key.encode())
    return _fernet


def encrypt_token(plain: str) -> str:
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_token(cipher: str) -> str:
    return _get_fernet().decrypt(cipher.encode()).decode()