python
# Simple SQLAlchemy models for the expense-tracker
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    # relationships
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("GroupMembership", back_populates="user", cascade="all, delete-orphan")

class CategoryBudget(Base):
    __tablename__ = "category_budgets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    budget = Column(Float, nullable=False)
    custom_alert_percent = Column(Integer, nullable=True)  # e.g., 10 for 10%
    user = relationship("User")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    shared = Column(Boolean, default=False)
    user = relationship("User", back_populates="expenses")
    shares = relationship("ExpenseShare", back_populates="expense", cascade="all, delete-orphan")

class ExpenseShare(Base):
    __tablename__ = "expense_shares"
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    share_amount = Column(Float, nullable=False)
    expense = relationship("Expense", back_populates="shares")
    # user relationship omitted for brevity; can be added by the consumer

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    memberships = relationship("GroupMembership", back_populates="group", cascade="all, delete-orphan")

class GroupMembership(Base):
    __tablename__ = "group_memberships"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="groups")
