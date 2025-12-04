python
"""
CLI for the expense tracker.

Commands (short):
  - create-user       : add a user
  - set-budget        : set a monthly budget for a user's category
  - add-expense       : add an expense (optional: shared split)
  - report-monthly    : total spend for a user-month
  - compare-spending  : show spent vs budget per category for a user-month

Notes:
  - Dates are expected in YYYY-MM-DD format.
  - Shared expense splits: pass shares as 'Bob:10,Alice:5' (user:amount).
"""
import click
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import User, Expense, CategoryBudget, ExpenseShare
from config import DATABASE_URL, EMAIL_NOTIF, DEFAULT_LOW_BUDGET_PERCENT
from datetime import datetime, date as datecls
import smtplib
from email.mime.text import MIMEText

engine = create_engine(DATABASE_URL, future=True)
Session = sessionmaker(bind=engine, future=True)

def send_email(to_email, subject, body):
    """Simple SMTP email sender. Optional — will skip if config missing."""
    if not EMAIL_NOTIF.get("SMTP_HOST") or not EMAIL_NOTIF.get("FROM_EMAIL"):
        # Email not configured
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_NOTIF["FROM_EMAIL"]
    msg["To"] = to_email
    try:
        with smtplib.SMTP(EMAIL_NOTIF["SMTP_HOST"], EMAIL_NOTIF["SMTP_PORT"]) as s:
            if EMAIL_NOTIF.get("SMTP_USER"):
                s.login(EMAIL_NOTIF["SMTP_USER"], EMAIL_NOTIF["SMTP_PASS"])
            s.send_message(msg)
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False

def get_user(session, user_name):
    return session.query(User).filter_by(name=user_name).first()

@click.group()
def cli():
    pass

@cli.command('create-user')
@click.option('--name', required=True, help='User name (unique)')
@click.option('--email', required=False, help='Optional email for alerts')
def create_user(name, email):
    """Create a new user."""
    session = Session()
    existing = session.query(User).filter_by(name=name).first()
    if existing:
        click.echo("User exists.")
        session.close()
        return
    u = User(name=name, email=email)
    session.add(u)
    session.commit()
    click.echo(f"User '{name}' created with id={u.id}.")
    session.close()

@cli.command('set-budget')
@click.option('--user', required=True)
@click.option('--category', required=True)
@click.option('--year', required=True, type=int)
@click.option('--month', required=True, type=int)
@click.option('--budget', required=True, type=float)
@click.option('--alert', required=False, type=int, help='Alert percent (e.g., 10 for 10%)')
def set_budget(user, category, year, month, budget, alert):
    """Set monthly budget for a category for a user."""
    session = Session()
    u = get_user(session, user)
    if not u:
        click.echo("User not found.")
        session.close()
        return
    if budget < 0:
        click.echo("Budget must be non-negative.")
        session.close()
        return
    cb = session.query(CategoryBudget).filter_by(user_id=u.id, category=category, year=year, month=month).first()
    if not cb:
        cb = CategoryBudget(user_id=u.id, category=category, year=year, month=month, budget=budget, custom_alert_percent=alert)
        session.add(cb)
    else:
        cb.budget = budget
        cb.custom_alert_percent = alert
    session.commit()
    click.echo("Budget set.")
    session.close()

@cli.command('add-expense')
@click.option('--user', required=True, help='User name')
@click.option('--amount', required=True, type=float)
@click.option('--category', required=True)
@click.option('--date', default=None, help='YYYY-MM-DD (defaults to today)')
@click.option('--note', default='', help='Optional note')
@click.option('--shared', is_flag=True, default=False, help='Mark as shared expense')
@click.option('--shares', default='', help="comma separated 'user:amount' for splitting, e.g., Bob:10,Alice:5")
def add_expense(user, amount, category, date, note, shared, shares):
    """Add an expense and check budgets/alerts."""
    session = Session()
    u = get_user(session, user)
    if not u:
        click.echo(f"User '{user}' not found. Create user first.")
        session.close()
        return
    if amount <= 0:
        click.echo("Amount must be positive.")
        session.close()
        return
    # parse date
    if date:
        try:
            exp_date = datetime.strptime(date, "%Y-%m-%d").date()
        except Exception:
            click.echo("Invalid date format. Use YYYY-MM-DD.")
            session.close()
            return
    else:
        exp_date = datecls.today()

    expense = Expense(user_id=u.id, amount=amount, category=category, note=note, date=exp_date, shared=shared)
    session.add(expense)
    session.commit()  # need id for shares

    # handle shares (safely ignore unknown users / malformed entries)
    if shared and shares:
        parts = [p.strip() for p in shares.split(",") if p.strip()]
        for p in parts:
            try:
                name, val = p.split(":", 1)
            except ValueError:
                continue
            share_user = session.query(User).filter_by(name=name.strip()).first()
            if not share_user:
                # unknown share recipient - ignore
                continue
            try:
                valf = float(val)
            except Exception:
                valf = 0.0
            sh = ExpenseShare(expense_id=expense.id, user_id=share_user.id, share_amount=valf)
            session.add(sh)
        session.commit()

    click.echo("Expense added.")

    # check budgets and alerts for the month/category
    year = expense.date.year
    month = expense.date.month

    # total spent in this category for this user/month (sum of amounts)
    total_spent = session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == u.id,
        func.strftime("%Y", Expense.date) == str(year),
        func.strftime("%m", Expense.date) == f"{month:02d}",
        Expense.category == category
    ).scalar() or 0.0

    # fetch budget
    budget = session.query(CategoryBudget).filter_by(user_id=u.id, category=category, year=year, month=month).first()
    if budget:
        if total_spent > budget.budget:
            msg = f"ALERT: You exceeded budget for {category} ({month}/{year}). Spent {total_spent:.2f}, budget {budget.budget:.2f}"
            click.echo(click.style(msg, fg="red"))
            if u.email:
                send_email(u.email, "Budget exceeded", msg)
        else:
            pct = budget.custom_alert_percent if budget.custom_alert_percent is not None else DEFAULT_LOW_BUDGET_PERCENT
            remaining = budget.budget - total_spent
            if remaining <= (budget.budget * pct / 100.0):
                msg = f"NOTICE: Only {remaining:.2f} left in budget for {category} ({month}/{year})"
                click.echo(click.style(msg, fg="yellow"))
                if u.email:
                    send_email(u.email, "Low budget notice", msg)
    session.close()

@cli.command('report-monthly')
@click.option('--user', required=True)
@click.option('--year', required=True, type=int)
@click.option('--month', required=True, type=int)
def report_monthly(user, year, month):
    """Show total spending for a month (all categories)."""
    session = Session()
    u = get_user(session, user)
    if not u:
        click.echo("User not found.")
        session.close()
        return
    total = session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == u.id,
        func.strftime("%Y", Expense.date) == str(year),
        func.strftime("%m", Expense.date) == f"{month:02d}"
    ).scalar() or 0.0
    click.echo(f"Total spending for {user} in {month}/{year}: {total:.2f}")
    session.close()

@cli.command('compare-spending')
@click.option('--user', required=True)
@click.option('--year', required=True, type=int)
@click.option('--month', required=True, type=int)
def compare_spending(user, year, month):
    """Compare spending vs budget per category for a month."""
    session = Session()
    u = get_user(session, user)
    if not u:
        click.echo("User not found.")
        session.close()
        return
    rows = session.query(
        Expense.category,
        func.sum(Expense.amount).label("spent")
    ).filter(
        Expense.user_id == u.id,
        func.strftime("%Y", Expense.date) == str(year),
        func.strftime("%m", Expense.date) == f"{month:02d}"
    ).group_by(Expense.category).all()
    click.echo("Category | Spent | Budget | Remaining")
    for cat, spent in rows:
        b = session.query(CategoryBudget).filter_by(user_id=u.id, category=cat, year=year, month=month).first()
        budget_amt = b.budget if b else 0.0
        remaining = budget_amt - (spent or 0.0)
        click.echo(f"{cat} | {spent:.2f} | {budget_amt:.2f} | {remaining:.2f}")
    session.close()

if __name__ == '__main__':
    cli()