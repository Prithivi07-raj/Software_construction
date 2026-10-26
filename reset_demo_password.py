from app import create_app
from models import db, User

app = create_app("development")

with app.app_context():
    user = User.query.filter_by(
        email="demo@cloudvault.local"
    ).first()

    if user is None:
        print("Demo user not found.")
    else:
        user.set_password("Password123!")
        db.session.commit()
        print("Demo password reset successfully.")
        print("Email: demo@cloudvault.local")
        print("Password: Password123!")
