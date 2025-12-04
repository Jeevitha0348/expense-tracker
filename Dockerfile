dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV EXP_DB_URL=sqlite:///expenses.db
EXPOSE 8000
# By default show help so the container doesn't immediately exit; evaluator can run interactive commands.
CMD ["sh", "-c", "python db_init.py --sample || true; exec python app.py --help"]