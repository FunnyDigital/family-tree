"""Change an admin password.

Run it against the database the app is using:

    python -m app.set_password              # prompts (recommended)
    python -m app.set_password admin        # picks the user, still prompts

Inside a container:

    docker exec -it <backend-container> python -m app.set_password

If stdin is not a terminal it reads one line from stdin, so it can be scripted:

    echo "my new password" | python -m app.set_password
"""

import getpass
import sys

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import User


def read_password(prompt: str) -> str:
    if sys.stdin.isatty():
        return getpass.getpass(prompt)
    line = sys.stdin.readline()
    print(f"{prompt}(read from stdin)")
    return line.strip()


def main() -> int:
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id).all()
        if not users:
            print("There are no admin users yet.")
            print("Start the app once so it can create the account, then run this again.")
            return 1

        username = sys.argv[1] if len(sys.argv) > 1 else users[0].username
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            print(f"No user named {username!r}.")
            print("Existing accounts: " + ", ".join(u.username for u in users))
            return 1

        password = read_password(f"New password for {username}: ")
        if not password:
            print("Empty password — nothing changed.")
            return 1

        confirm = read_password("Repeat it: ")
        if password != confirm:
            print("The two passwords did not match — nothing changed.")
            return 1

        user.hashed_password = get_password_hash(password)
        db.commit()
        print(f"Done. Password updated for {username!r}.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
