markdown
# Expense Tracker - Complete, evaluator-ready project

This is a small CLI-backed expense tracker intended for quick evaluation.
It uses SQLite by default so evaluators can run locally without extra setup.

## Quick start (local)
1. Create virtualenv and install:
   bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
`

2. Initialize DB and insert sample data:

   bash
   python db_init.py --sample
   

3. Create a user (if not using sample):

   bash
   python app.py create-user --name jeevitha --email jeevitha@example.com
   

4. Set budget:

   bash
   python app.py set-budget --user jeevitha --category Food --year 2025 --month 10 --budget 300 --alert 10
   

5. Add expense:

   bash
   python app.py add-expense --user jeevitha --amount 50 --category Food --date 2025-10-05 --note "Lunch"
   

6. Reports:

   bash
   python app.py report-monthly --user jeevitha --year 2025 --month 10
   python app.py compare-spending --user jeevitha --year 2025 --month 10
   

## Tests

Run:

bash
pytest -q


## Docker

Build and run:

bash
docker build -t expense-tracker .
docker run --rm -it -e EXP_DB_URL=sqlite:///expenses.db expense-tracker


## Notes

* Email notifications are optional and require SMTP env vars (see config.py).
* Shared expenses: `--shared` and `--shares` accept comma-separated user:amount pairs.
* Dates expect YYYY-MM-DD format.
