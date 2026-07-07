from werkzeug.security import generate_password_hash
import os

from app.db.session import get_db
from app.db.model import User
from app import create_app


def create_admin():
    app = create_app()
    with app.app_context():
        db = get_db()
        data_password = os.getenv("ADMIN_PASSWORD")

        user = db.query(User).filter_by(
            username="admin"
        ).first()
        if user is not None:
            return "The administrator had already been created"

        try:
            admin = User(
                first_name = "admin",
                last_name = "admin",
                username = "admin",
                email = "storeadmin@g.com",
                password = generate_password_hash(data_password),
                role = "admin"
            )
            db.add(admin)
            db.commit()
            return "The administrator was created"
        except Exception as e:
            db.rollback()
            return f"Error {e}"


if __name__ == "__main__":
    print(create_admin())
