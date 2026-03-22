from app.core.security import get_password_hash


def test_password_hashing() -> None:
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    assert hashed != password