import sqlite3


def data_to_base(data_of_user, data_of_budget):  # ф-ия заносит данные в бд: имя, ф-план, распределение и размер бюджета
    cur.execute('SELECT userid FROM users')  # достаём файлы из колонки userid таблицы users
    id_number = cur.fetchall()[-1][0] + 1  # берём последний элемент(картеж) списка и первый элемент картежа
    full_data = (id_number, str(data_of_user[0]), float(data_of_budget[1]), int(data_of_user[1]))
    cur.execute("INSERT INTO users (userid, name, budget, f_plan) VALUES(?, ?, ?, ?)", full_data)
    conn.commit()
    return 0


def budget_ratio(f_plan, capital):  # распределяет финансы по 3-м основным категориям
    if f_plan == 1:
        necessary = 0.4 * capital
        other = 0.2 * capital
        savings = 0.4 * capital
        return {"необходимое": necessary, "развлечения": other, "накопления": savings}

    if f_plan == 2:
        necessary = 0.5 * capital
        other = 0.2 * capital
        savings = 0.3 * capital
        return {"необходимое": necessary, "развлечения": other, "накопления": savings}

    if f_plan == 3:
        necessary = 0.5 * capital
        other = 0.4 * capital
        savings = 0.1 * capital
        return {"необходимое": necessary, "развлечения": other, "накопления": savings}

    return 0


def data_input(user_data):  # запрашивает информацию о бюджете пользователя
    try:
        budget = float(input("Введите Ваш бюджет на последующий месяц в рублях: "))
        ratio = budget_ratio(user_data[1], budget)
        return [ratio, budget]
        # возвращает список, в к-м словарь с распределением бюджета по 3-м основным категориям и бюджет

    except ValueError:
        print("Не могу Вас понять, нужно ввести число (можно вещественное), равное Вашему бюджету в "
              "денежных единицах")
        return data_input(user_data)


def authorization():  # функция авторизации, вводит никнейм и выбирает финансовый план
    name = input("Как к Вам обращаться? Введите имя: ")
    try:
        finance_plan = int(input("Выберите Ваш финансовый план:\n"
                                 "Введите '1', если желаете сберегательный план\n"
                                 "Введите '2', если желаете стандартный план\n"
                                 "Введите '3', если желаете план 'жизнь одним днём':\n"))
        if 4 > finance_plan > 0:
            return [name, finance_plan]  # возвращаем список из ника и номера плана
        else:
            print("Не могу Вас понять, нужно ввести цифру, соответствующую номеру выбранного Вами"
                  "финансового плана")
            return authorization()

    except ValueError:
        print("Не могу Вас понять, нужно ввести цифру, соответствующую номеру выбранного Вами"
              "финансового плана")
        return authorization()


# Работа с БД
conn = sqlite3.connect('database.db')  # создали базу данных (после первого запуска подключает к ней)
cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    userid INT PRIMARY KEY,
    name TEXT,
    budget REAL,
    f_plan INTEGER)
""")  # генерируем таблицу c данными о пользователе и создаём 4 колонки
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
    userid INT PRIMARY KEY,
    name_of_expenses TEXT,
    part_of_budget REAL,
    how_much INTEGER)
""")  # генерируем таблицу расходов по 3-м основным категориям
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
    userid INT PRIMARY KEY,
    name_of_expenses TEXT,
    part_of_budget REAL,
    how_much INTEGER)
""")  # генерируем таблицу подкатегорий категории "необходимость"
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
    userid INT PRIMARY KEY,
    name_of_expenses TEXT,
    part_of_budget REAL,
    how_much INTEGER)
""")  # генерируем таблицу подкатегорий категории "развлечения"
conn.commit()

# ###################################


user = authorization()
main_data = data_input(user)
data_to_base(user, main_data)  # ф-ия заносит данные в бд: имя, ф-план, распределение и размер бюджета
