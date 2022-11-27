import sqlite3
import datetime
from utils import does_user_exist, answer, take_mes, error_with_smt


def exp_id():
    conn = sqlite3.connect('../database.db')  # подключение к бд
    cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

    cur.execute(f"SELECT exp_id FROM expenses")
    try:
        id_number = cur.fetchall()[-1][0] + 1  # берём последний элемент(картеж) списка и первый элемент картежа
    except IndexError:
        id_number = 1  # если таблица пустая, то индексу устанавливается значение 1

    conn.commit()
    cur.close()
    return id_number


def expenses(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'

    else:
        try:
            try:
                cost = 0 - float(event.obj.message['text'])

                exp_data = [user_id]
                conn = sqlite3.connect('../database.db')  # подключение к бд
                cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

                answer(event, 'К какой категории хотите отнести эту трату?')
                cat = str(take_mes())
                exp_data.append(cat)

                answer(event, 'Какая важность у этой траты: 1 - необходимое, 2 - развлечение')
                try:
                    exp_data.append(int(take_mes()))
                except TypeError:
                    answer(event, "Не понимаю, введите 1 если трата необходимая иначе 2 (пример: 1), попробуем снова")
                    expenses(event)

                exp_data.append(cost)
                exp_data.append(str(datetime.datetime.now())[:-16:])  # записывает дату траты
                exp_data.append(str(datetime.datetime.now())[10:-10:])  # записывает время траты
                exp_data.append(exp_id())  # создаём новое айди

                cur.execute("INSERT INTO expenses (userid, category_name, importance, costs, date, time, exp_id) "
                            "VALUES(?, ?, ?, ?, ?, ?, ?)", exp_data)

                conn.commit()
                cur.close()
                answer(event, "Данные о трате успешно записаны!")

            except TypeError:
                answer(event, 'Не понимаю, введите количество потраченных денежных единиц, введите ещё раз, пожалуйста')
        except sqlite3.Error as error:
            error_with_smt(event, error)
