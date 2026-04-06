"""
Init DB script: create tables and seed data.
Usage: python -m scripts.init_db
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import User, Homework, Reward  # noqa: F401


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("Creating seed admin user...")
            admin = User(
                openid="admin_seed_openid",
                nick_name="管理员",
                role="admin",
            )
            db.add(admin)
            db.flush()

            # Create sample rewards
            rewards = [
                Reward(
                    name="小红花",
                    description="一朵漂亮的小红花",
                    points=10,
                    stock=100,
                    created_by=admin.id,
                ),
                Reward(
                    name="零食大礼包",
                    description="各种好吃的零食",
                    points=50,
                    stock=20,
                    created_by=admin.id,
                ),
                Reward(
                    name="游乐场门票",
                    description="周末游乐场一日门票",
                    points=200,
                    stock=5,
                    created_by=admin.id,
                ),
            ]
            db.add_all(rewards)
            db.commit()
            print("Seed data created.")
        else:
            print("Seed data already exists, skipping.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
