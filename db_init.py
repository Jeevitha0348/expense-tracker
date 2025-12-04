python
"""
Initialize the database and optionally add sample data.

Usage:
    python db_init.py        # creates DB file (if using sqlite) and tables
    python db_init.py --sample  # also inserts sample users and budgets
"""
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, CategoryBudget, Expense
from config import DATABASE_URL
from datetime import date

def init_db(drop=False):
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine

def create_sample(engine):
    Session = sessionmaker(bind=engine, future=True)
    s = Session()
    # Create sample users and a few records so evaluators can test quickly
    u1 = User(name="Alice", email="alice@example.com")
    u2 = User(name="Bob", email="bob@example.com")
    s.add_all([u1, u2])
    s.commit()

    # Budgets for Alice for Oct 2025 (example)
    b1 = CategoryBudget(user_id=u1.id, category="Food", year=2025, month=10, budget=300, custom_alert_percent=10)
    b2 = CategoryBudget(user_id=u1.id, category="Transport", year=2025, month=10, budget=120, custom_alert_percent=15)
    s.add_all([b1, b2])
    s.commit()

    # Example expense
    exp = Expense(user_id=u1.id, date=date(2025,10,5), amount=45.0, category="Food", note="Lunch", shared=False)
    s.add(exp)
    s.commit()
    s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Init DB for expense-tracker')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables before creating')
    parser.add_argument('--sample', action='store_true', help='Create sample data after init')
    args = parser.parse_args()

    engine = init_db(drop=args.drop)
    print("DB initialized.")
    if args.sample:
        create_sample(engine)
        print("Sample data inserted.")

