"""Create an administrator account through a controlled local CLI."""

from getpass import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def main() -> None:
    full_name = input("Administrator full name: ").strip()
    email = input("Administrator email: ").strip().lower()
    password = getpass("Administrator password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")

    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            raise SystemExit("An account with this email already exists.")
        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )
        db.add(user)
        db.commit()
        print(f"Administrator account created for {email}.")


if __name__ == "__main__":
    main()
