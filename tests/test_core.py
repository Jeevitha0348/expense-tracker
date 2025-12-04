python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Expense, CategoryBudget
from datetime import date

def test_basic_db_operations(tmp_path):
    dbfile = tmp_path / "test.db"
    url = f"sqlite:///{dbfile}"
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    s = Session()
    u = User(name="T1", email=None)
    s.add(u)
    s.commit()
    assert u.id is not None
    e = Expense(user_id=u.id, amount=20.0, category="Food", date=date(2025,10,2))
    s.add(e)
    cb = CategoryBudget(user_id=u.id, category="Food", year=2025, month=10, budget=100)
    s.add(cb)
    s.commit()
    total = s.query(Expense).filter_by(user_id=u.id).count()
    assert total == 1
    s.close()
