python
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, User, Expense, CategoryBudget
from datetime import date

def test_low_budget_and_exceed(tmp_path):
    dbfile = tmp_path / "test2.db"
    url = f"sqlite:///{dbfile}"
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    s = Session()
    u = User(name="T2", email=None)
    s.add(u)
    s.commit()
    cb = CategoryBudget(user_id=u.id, category="Food", year=2025, month=12, budget=100, custom_alert_percent=20)
    s.add(cb)
    s.commit()
    e1 = Expense(user_id=u.id, amount=75.0, category="Food", date=date(2025,12,5))
    s.add(e1)
    s.commit()
    total = s.query(func.sum(Expense.amount)).filter(Expense.user_id==u.id).scalar() or 0.0
    assert total == 75.0
    e2 = Expense(user_id=u.id, amount=40.0, category="Food", date=date(2025,12,10))
    s.add(e2)
    s.commit()
    total = s.query(func.sum(Expense.amount)).filter(Expense.user_id==u.id).scalar() or 0.0
    assert total == 115.0
    s.close()
