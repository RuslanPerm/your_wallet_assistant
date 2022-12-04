import sqlite3

# Работа с БД
conn = sqlite3.connect('database.db')  # создали базу данных (после первого запуска подключает к ней)
cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    userid INT PRIMARY KEY, 
    name TEXT,
    budget REAL,
    f_plan_n REAL,
    f_plan_o REAL,
    f_plan_c REAL,
    password TEXT,
    accumulation REAL,
    pay_day TEXT,
    pay_time TEXT)
""")  # генерируем таблицу c данными о пользователе
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
    exp_id INT PRIMARY KEY,
    userid INT,
    category_name TEXT,
    importance INT,
    costs REAL,
    date TEXT,
    time TEXT)
""")  # importance: 1 - необходимое, 2 - развлечение | # генерируем таблицу расходов

conn.commit()
