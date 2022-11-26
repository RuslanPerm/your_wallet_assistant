import sqlite3
from ywa_bot import does_user_exist, answer, error_with_smt


# функция, отвечающая сколько сбережений/накоплений у пользователя
def my_bank(event):
    user_id = does_user_exist(event)

    if not user_id:
        answer(event, 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"')
    else:
        try:
            conn = sqlite3.connect('../database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute(f"SELECT accumulation FROM users WHERE userid = '{user_id}'")
            # выбираем столбец сбережения где айди пользователя равен айди пользователя, который запрашивает

            user_acc = cur.fetchone()
            answer(event, user_acc[0])

            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            error_with_smt(event, error)
