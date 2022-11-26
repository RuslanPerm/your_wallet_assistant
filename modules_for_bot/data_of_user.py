import sqlite3
from utils import does_user_exist, answer, take_mes


def edit_data():
    pass


def about_me(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'
    else:
        conn = sqlite3.connect('../database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        cur.execute(f"SELECT FROM users WHERE userid = '{user_id}'")
        # выбираем столбец с данными о пользователе

        #  берём записи о пользователе
        data = cur.fetchall()
        user_data = []
        for elem in data:
            user_data.append(elem)

        answer(event, f'Ваше имя: {user_data[1]}\nВаш бюджет: {user_data[2]}\nИз них на необходимые траты: '
                      f'{user_data[3]*user_data[2]}, на развлечения {user_data[4]*user_data[2]}, на накопления '
                      f'{user_data[5]*user_data[2]}\nВсего накоплено: {user_data[6]}\nДень зарплаты: {user_data[7]}')
        answer(event, 'Хотите изменить какие-либо данные о себе?')
        if take_mes().lower() == 'да':
            edit_data()
        else:
            answer(event, 'Что ж, ответ не похож на "да", поэтому сохраню данные')

        conn.commit()
        cur.close()
