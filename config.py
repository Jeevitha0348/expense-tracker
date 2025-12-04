python
import os

# Database URL (default: local sqlite file)
DATABASE_URL = os.getenv("EXP_DB_URL", "sqlite:///expenses.db")

# Email / SMTP configuration (optional)
EMAIL_NOTIF = {
    "SMTP_HOST": os.getenv("SMTP_HOST", ""),
    "SMTP_PORT": int(os.getenv("SMTP_PORT") or 0),
    "SMTP_USER": os.getenv("SMTP_USER", ""),
    "SMTP_PASS": os.getenv("SMTP_PASS", ""),
    "FROM_EMAIL": os.getenv("FROM_EMAIL", ""),
}

# Default percentage of budget remaining at which to send a low-budget notice.
# Example: 10 means notify when remaining <= 10% of budget.
DEFAULT_LOW_BUDGET_PERCENT = int(os.getenv("LOW_BUDGET_PERCENT", "10"))
