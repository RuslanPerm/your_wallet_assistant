import sqlite3
from utils import does_user_exist, answer, error_with_smt


def how_much_may_cost(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'

    else:
        try:
            conn = sqlite3.connect('../database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute(f"SELECT budget FROM users WHERE userid = '{user_id}'")  # выбираем столбец бюджет где айди
            # равен айди написавшего пользователя
            balance = cur.fetchone()[0]  # берём это значение

            cur.execute(f"SELECT f_plan FROM users WHERE userid = '{user_id}'")  # выбираем столбец ф-план где айди
            f_plan = cur.fetchone()[0]  # берём это значение
            conn.commit()
            cur.close()

            if f_plan == 1:
                necessary = balance * 0.4
                other = balance * 0.2
                answer(event, f'Вы можете потратить:\n{necessary} на необходимые траты\n{other} на другое')

            elif f_plan == 2:
                necessary = balance * 0.5
                other = balance * 0.2
                answer(event, f'Вы можете потратить:\n{necessary} на необходимые траты\n{other} на другое')

            elif f_plan == 3:
                necessary = balance * 0.5
                other = balance * 0.4
                answer(event, f'Вы можете потратить:\n{necessary} на необходимые траты\n{other} на другое')
            else:
                error_with_smt(event, 'idk (ツ)')

        except sqlite3.Error as error:
            error_with_smt(event, error)
