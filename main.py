import sqlite3
import sys
import requests


# принимаем данные о затратах от пользователя
def get_new_data(user_id):
    cat_exp_name = input("Выберите категорию трат: необходимое или развлечение?: ")
    sub_cat_exp_name = input("Введите подкатегорию трат: ")
    expenses = input("Сколько Вы потратили: ")
    try:
        expenses = float(expenses)
    except TypeError:
        print('Вы неправильно ввели затраченную сумму, попробуйте ещё раз')
        get_new_data(user_id)

    conn = sqlite3.connect('database.db')  # создали базу данных (после первого запуска подключает к ней)
    cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

    # реализовать замену данных: достаём данные, увеличиваем, перезаписываем

    full_data = (user_id, cat_exp_name, sub_cat_exp_name, expenses)
    cur.execute("INSERT INTO expenses (userid, expenses_category, category_costs, expenses_subcategory, "
                "subcategory_costs) VALUES(?, ?, ?, ?, ?)", full_data)
    conn.commit()
    cur.close()

    return 'Данные успешно введены!'


# запрашиваем с парсера курс валют, возвращает словарь {название: отношение к рублю}
def exchange_rates():
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()  # парсинг катировок ЦБ
    usd = data['Valute']['USD']['Value']
    eur = data['Valute']['EUR']['Value']

    return {data['Valute']['USD']['Name']: usd, data['Valute']['EUR']['Name']: eur}


# вход в систему, проверка пароля + сделать шифрования пароля
def login():
    username = input("Введите Ваше имя: ")
    password = input("Введите пароль: ")

    conn = sqlite3.connect('database.db')  # создали базу данных (после первого запуска подключает к ней)
    cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

    cur.execute(f"SELECT name, password FROM users WHERE name = '{username}' AND password = '{password}'")
    id = cur.execute(f"SELECT name, password FROM users WHERE name = '{username}' AND password = '{password}'")
    conn.commit()

    cur.close()

    if not cur.fetchone():
        print("Неверный логин или пароль")
        should_continue = input("Похоже Вас нет в нашей системе, желаете зарегистрироваться?"
                                "\nВведите '1' если да")
        if should_continue == '1':
            authorization()
        else:
            sys.exit()

    else:
        print('Добро пожаловать!')
        return


# регистрация
def data_to_base(data_of_user, data_of_budget):  # ф-ия заносит данные в бд: имя, ф-план, распределение и размер бюджета
    cur.execute('SELECT userid FROM users')  # достаём файлы из колонки userid таблицы users

    try:
        id_number = cur.fetchall()[-1][0] + 1  # берём последний элемент(картеж) списка и первый элемент картежа
    except IndexError:
        id_number = 1  # если таблица пустая, то индексу устанавливается значение 1
    full_data = (id_number, str(data_of_user[0]), float(data_of_budget[1]), int(data_of_user[1]), str(data_of_user[2]))
    cur.execute("INSERT INTO users (userid, name, budget, f_plan, password) VALUES(?, ?, ?, ?, ?)", full_data)
    conn.commit()
    return 0


# распределяет финансы по 3-м основным категориям
def budget_ratio(f_plan, capital):
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


# запрашивает информацию о бюджете пользователя
def data_input(user_data):
    try:
        budget = float(input("Введите Ваш бюджет на последующий месяц в рублях: "))
        ratio = budget_ratio(user_data[1], budget)
        return [ratio, budget]
        # возвращает список, в к-м словарь с распределением бюджета по 3-м основным категориям и бюджет

    except ValueError:
        print("Не могу Вас понять, нужно ввести число (можно вещественное), равное Вашему бюджету в "
              "денежных единицах")
        return data_input(user_data)


def password():
    user_password = input("Придумайте пароль: ")
    if len(user_password) < 8:
        password_alert = input("Пароль ненадёжный, пароль надёжный если в нём больше 8 символов"
                               "\nВведите '1' чтобы придумать другой, либо '2' чтобы продолжить регистрацию")
        if password_alert == '1':
            return password()

    return user_password


def authorization():  # функция авторизации, вводит никнейм и выбирает финансовый план
    name = input("Как к Вам обращаться? Введите имя: ")
    password_of_user = password()
    print(password_of_user)
    try:
        finance_plan = int(input("Выберите Ваш финансовый план:\n"
                                 "Введите '1', если желаете сберегательный план\n"
                                 "Введите '2', если желаете стандартный план\n"
                                 "Введите '3', если желаете план 'жизнь одним днём':\n"))
        if 4 > finance_plan > 0:
            return [name, finance_plan, password_of_user]  # возвращаем список из ника, номера плана и пароля
        else:
            print("Не могу Вас понять, нужно ввести цифру, соответствующую номеру выбранного Вами"
                  "финансового плана")
            return authorization()

    except ValueError:
        print("Не могу Вас понять, нужно ввести цифру, соответствующую номеру выбранного Вами"
              "финансового плана")
        return authorization()


def hello():
    are_you_exist = input("Введите '1' чтобы войти или введите '2' чтобы зарегистрироваться ")

    if are_you_exist == '1':
        return login()

    elif are_you_exist == '2':
        user = authorization()
        main_data = data_input(user)
        data_to_base(user, main_data)  # ф-ия заносит данные в бд: имя, ф-план, распределение и размер бюджета
        print('Поздравляю, Вы успешно зарегистрировались!')
        # return должен возвращать userid

    else:
        print("не могу понять Вас, введите '1' чтобы войти или введите '2' чтобы зарегистрироваться")
        return hello()


# Работа с БД
conn = sqlite3.connect('database.db')  # создали базу данных (после первого запуска подключает к ней)
cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    userid INT PRIMARY KEY,
    name TEXT,
    budget REAL,
    f_plan INTEGER,
    password TEXT)
""")  # генерируем таблицу c данными о пользователе: номер в системе, имя, бюджет, финансовый план, пароль
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
    userid INT PRIMARY KEY,
    expenses_category TEXT,
    category_costs REAL,
    expenses_subcategory TEXT,
    subcategory_costs REAL)
""")
conn.commit()
cur.close()
# генерируем таблицу расходов: номер пользователя в системе, категория трат, затрачено на категорию,
# подкатегория трат, затрачено на подкатегорию

# ###################################

id_of_user = hello()
get_new_data(id_of_user)
