sql
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');
INSERT INTO category_budgets (user_id, category, year, month, budget, custom_alert_percent)
VALUES (1, 'Food', 2025, 10, 300, 10);
INSERT INTO expenses (user_id, date, amount, category, note, shared)
VALUES (1, '2025-10-05', 45.0, 'Food', 'Lunch', 0);
