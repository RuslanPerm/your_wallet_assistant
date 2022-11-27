import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import sqlite3
import random
import datetime

# from modules_for_bot.hmmc import how_much_may_cost
# from modules_for_bot.hmis import how_much_is_spent
# from modules_for_bot.reg import registration
# from modules_for_bot.exp import expenses
# from modules_for_bot.bank import my_bank
# from modules_for_bot.data_of_user import about_me
# from modules_for_bot.utils import answer


# *****************************************UTILS***************************************************************
# *****************************************UTILS***************************************************************
# *****************************************UTILS***************************************************************
# *****************************************UTILS***************************************************************
# *****************************************UTILS***************************************************************
# функция, проверяющая тип, 2ой аргумент - название необходимого типа данных, а 3ий сообщение юзеру в случае ошибки
def check_type(event, need_type, if_error):
    user_mes = take_mes()

    if need_type == 'integer':
        try:
            user_mes = int(user_mes)
            return user_mes

        except ValueError:
            answer(event, if_error)
            answer(event, 'Попробуйте ещё раз')
            return check_type(event, need_type, if_error)

    elif need_type == 'float':
        try:
            user_mes = float(user_mes)
            return user_mes
        except ValueError:
            answer(event, if_error)
            answer(event, 'Попробуйте ещё раз')
            return check_type(event, need_type, if_error)


# функция обеспечивает последовательную отправку сообщений (возможно костыль)
def take_mes():
    vk_session = vk_api.VkApi(
        token='360c9391be9e818c234c23236b6d52a8fc95949d3fb7113bae23c1b8392fcbd0bcff35aa316fd95c90e5e')
    longpoll = VkBotLongPoll(vk_session, '212752190')
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            global vk
            vk = vk_session.get_api()
            return event.obj.message['text']


# обработчик ошибок с базой данных
def error_with_smt(event, error):
    print("Ошибка при работе с БД", error)
    answer(event, "Ошибка сервера, приносим свои извинения, устроняем проблему")


def answer(event, message):  # функция, посылающая сообщения пользователя
    vk.messages.send(user_id=event.obj['message']['from_id'],
                     message=message,
                     random_id=random.randint(0, 2 ** 64))


def does_user_exist(ev):
    try:  # так как программа устанавливает в userid только целочисленные значения,
        # то пробуем узнать айди пользователя, если выдаст ошибку, значит пользователя не существует
        user_id = int(ev.object.message['from_id'])

        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд
        cur.execute(f"SELECT * FROM users WHERE userid = {user_id}")
        if cur.fetchall():
            conn.commit()
            cur.close()
            return user_id
        else:
            conn.commit()
            cur.close()
            return False

    except TypeError:
        return False
# ****************************************************************************************************
# ****************************************************************************************************
# ****************************************************************************************************
# ****************************************************************************************************


# ***************************************RESET***************************************************************
# ***************************************RESET***************************************************************
# ***************************************RESET***************************************************************
# ***************************************RESET***************************************************************
def reset(event):
    user_id = does_user_exist(event)
    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'
    else:
        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        # берём накопления и прибавляем к ним оставшийся бюджет
        cur.execute(f'SELECT accumulation FROM users WHERE userid = {user_id}')
        acc = sum(cur.fetchone())
        cur.execute(f'SELECT budget FROM users WHERE userid = {user_id}')
        start_budget = sum(cur.fetchone())
        cur.execute(f'SELECT f_plan_c FROM users WHERE userid = {user_id}')
        f_plan_c = sum(cur.fetchone())
        cur.execute(f'SELECT costs budget FROM expenses WHERE userid = {user_id}')  # добавить чтоб только за месяц
        # архивную таблицу сделать

        exps = cur.fetchall()
        all_exps = 0
        for exp in exps:
            all_exps += sum(exp)

        acc += (start_budget - all_exps + start_budget * f_plan_c)
        cur.execute(f"UPDATE users SET accumulation = {acc} WHERE userid = {user_id}")

        answer(event, 'Ого, зарплата это всегда приятно, какой у Вас бюджет до следующей зарплаты?')
        new_budget = check_type(event, 'float', 'Не понимаю Вас, нужно количество рублей у вас до следующей зарплаты')
        cur.execute(f"UPDATE users SET budget = {new_budget} WHERE userid = {user_id}")

        answer(event, f'Хорошо, Ваш бюджет обновлён (теперь там {new_budget} рублей), а остаток от бюджета перенесён'
                      f' в накопления, теперь у вас в сбережениях {acc} рублей')

        answer(event, f'Помните, что я не имею контроля на Вашими счетами, потому для лучшей продуктивности '
                      f'использования меня, переносите все денежные средства между счетами сами (то есть на накопления'
                      f'на развлечения, на необходимое)')

        conn.commit()
        cur.close()
# ************************************************************************************************************
# ************************************************************************************************************
# ************************************************************************************************************
# ************************************************************************************************************


# ************************************************DATA OF USER********************************************
# ************************************************DATA OF USER********************************************
# ************************************************DATA OF USER********************************************
# ************************************************DATA OF USER********************************************
# ************************************************DATA OF USER********************************************

# изменяем данные о пользователе
def edit_data(event):
    user_id = does_user_exist(event)

    answer(event, 'Выберите какие данные хотите изменить:\n1. Имя\n2. Бюджет\n3. Финансовый план\n4. Пароль\n'
                  '5. Добавить деньги в сбережения\n6. Забрать деньги из сбережений\n7. Всё\n\n'
                  'Введите номер соответствующего пункта')

    user_answer = check_type(event, 'integer', 'Я Вас не понял, нужно ввести номер пункта, который Вы хотите изменить')

    conn = sqlite3.connect('database.db')  # подключение к бд
    cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

    if user_answer == 1:
        answer(event, 'Как мне к Вам теперь обращаться?')
        name = take_mes()

        cur.execute(f"UPDATE users SET name = {name} WHERE userid = {user_id}")  # обновляем имя
        answer(event, f'Отлично, теперь Ваше имя {name}')
        conn.commit()
        cur.close()

    elif user_answer == 2:
        answer(event, 'Если Вам пришла зарплата или иной доход следует написать мне "день зп", тогда я тоже обновлю'
                      'бюджет, но разница в том, что тогда остаток бюджета переведу в сбережения')
        answer(event, 'Записать как зарплату?')

        should_continue = take_mes().lower()
        if should_continue == 'да':
            reset(event)
            conn.commit()
            cur.close()
            return 0
        else:
            answer(event, 'Какой у Вас теперь бюджет?')
            new_budget = check_type(event, 'float', 'Не понимаю Вас, нужно написать сколько рублей в Вашем новом '
                                                    'бюджете')

            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд
            cur.execute(f"UPDATE users SET budget = {new_budget} WHERE userid = {user_id}")  # обновляем budget
            answer(event, f'Отлично, теперь Ваш бюджет {new_budget} рублей')
            conn.commit()
            cur.close()

    elif user_answer == 3:
        fin_plan = f_plan(event)

        cur.execute(f"UPDATE users SET f_plan_n = {fin_plan[0]} WHERE userid = {user_id}")  # обновляем f_plan_n
        cur.execute(f"UPDATE users SET f_plan_o = {fin_plan[1]} WHERE userid = {user_id}")  # обновляем f_plan_o
        cur.execute(f"UPDATE users SET f_plan_c = {fin_plan[2]} WHERE userid = {user_id}")  # обновляем f_plan_c
        answer(event, f'Отлично, теперь у Вас {fin_plan[0]*100} на небходимое, {fin_plan[1]*100} на другое, '
                      f'{fin_plan[2]*100} на накопления')
        conn.commit()
        cur.close()

    elif user_answer == 4:
        cur.execute(f"SELECT password FROM users WHERE userid = {user_id}")
        old_password = cur.fetchone()

        answer(event, 'Введите старый пароль')
        check_password = take_mes()
        if old_password == check_password:
            answer(event, 'Пароль верный, теперь придумайте новый')
            new_password = pass_word(event)
            cur.execute(f"UPDATE users SET password = {new_password} WHERE userid = {user_id}")  # обновляем пароль
            answer(event, "Новый пароль сохранён")
        else:
            answer(event, 'Пароль неверный')

    elif user_answer == 5:
        answer(event, 'Сколько добавить к накоплениям?')
        add_acc = check_type(event, 'float', 'Не понимаю Вас, скажите сколько рублей Вы хотите добавить к сбережениям')

        cur.execute(f"SELECT accumulation FROM users WHERE userid = {user_id}")  # берём старые накопления
        acc = cur.fetchone()
        new_acc = acc + add_acc

        cur.execute(f"UPDATE users SET name = {new_acc} WHERE userid = {user_id}")  # обновляем накопления
        answer(event, f'Отлично, у Вас было {acc} в копилке, теперь {new_acc}')
        conn.commit()
        cur.close()

    elif user_answer == 6:
        answer(event, 'Сколько вычесть из накоплений?')
        add_acc = check_type(event, 'float', 'Не понимаю Вас, скажите сколько рублей Вы хотите вычесть из сбережений')

        cur.execute(f"SELECT accumulation FROM users WHERE userid = {user_id} рублей")  # берём старые накопления
        acc = cur.fetchone()
        new_acc = acc - add_acc

        cur.execute(f"UPDATE users SET name = {new_acc} WHERE userid = {user_id}")  # обновляем накопления
        answer(event, f'Данные изменены, у Вас было {acc} в копилке, теперь {new_acc} рублей')
        conn.commit()
        cur.close()

    elif user_answer == 7:
        answer(event, 'Как мне к вам обращаться?')
        name = take_mes()

        answer(event, 'Ваш бюджет?')
        budget = check_type(event, 'float', 'Не понимаю Вас, нужно написать сколько рублей в Вашем бюджете?')

        fin_plan = f_plan(event)

        answer(event, 'Сколько у Вас накоплений?')
        acc = check_type(event, 'float', 'Не понимаю Вас, нужно написать сколько рублей у Вас в сбережениях')

        answer(event, 'Придумайте пароль')
        password = pass_word(event)

        cur.execute(f"UPDATE users SET name = {name} WHERE userid = {user_id}")  # обновляем имя
        cur.execute(f"UPDATE users SET budget = {budget} WHERE userid = {user_id}")  # обновляем budget
        cur.execute(f"UPDATE users SET f_plan_n = {fin_plan[0]} WHERE userid = {user_id}")  # обновляем f_plan_n
        cur.execute(f"UPDATE users SET f_plan_o = {fin_plan[1]} WHERE userid = {user_id}")  # обновляем f_plan_o
        cur.execute(f"UPDATE users SET f_plan_c = {fin_plan[2]} WHERE userid = {user_id}")  # обновляем f_plan_c
        cur.execute(f"UPDATE users SET password = {password} WHERE userid = {user_id}")  # обновляем пароль
        cur.execute(f"UPDATE users SET name = {acc} WHERE userid = {user_id}")  # обновляем накопления

        conn.commit()
        cur.close()

        answer(event, 'Отлично все данные изменены, а расходы сохранены!')

    else:
        answer(event, 'Не понимаю Вас, нужно выбрать один из предложенных пунктов и написать его номер мне')
        edit_data(event)


def about_me(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'
    else:
        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        cur.execute(f"SELECT * FROM users WHERE userid = '{user_id}'")
        # выбираем столбец с данными о пользователе

        #  берём записи о пользователе
        user_data = list(cur.fetchall()[0])
        # for elem in data:
        #     user_data.append(elem)

        print(user_data)
        answer(event, f'Ваше имя: {user_data[1]}\nВаш бюджет: {user_data[2]}\nИз них на необходимые траты: '
                      f'{user_data[3]*user_data[2]}\nна развлечения {user_data[4]*user_data[2]}\nна накопления '
                      f'{user_data[5]*user_data[2]}\nВсего накоплено: {user_data[7]}')
        answer(event, 'Хотите изменить какие-либо данные о себе?')
        if take_mes().lower() == 'да':
            edit_data(event)
        else:
            answer(event, 'Что ж, ответ не похож на "да", поэтому сохраню данные')

        conn.commit()
        cur.close()
# ******************************************************************************************************************
# ******************************************************************************************************************
# ******************************************************************************************************************
# ******************************************************************************************************************
# ******************************************************************************************************************


# ****************************************BANK***************************************************************
# ****************************************BANK***************************************************************
# ****************************************BANK***************************************************************
# ****************************************BANK***************************************************************
# ****************************************BANK***************************************************************
# функция, отвечающая сколько сбережений/накоплений у пользователя
def my_bank(event):
    user_id = does_user_exist(event)

    if not user_id:
        answer(event, 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"')
    else:
        try:
            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute(f"SELECT accumulation FROM users WHERE userid = '{user_id}'")
            # выбираем столбец сбережения где айди пользователя равен айди пользователя, который запрашивает

            user_acc = cur.fetchone()
            answer(event, user_acc[0])

            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            error_with_smt(event, error)
# ***********************************************************************************************************
# ***********************************************************************************************************
# ***********************************************************************************************************
# ***********************************************************************************************************


# **********************************************HMIS*******************************************************
# **********************************************HMIS*******************************************************
# **********************************************HMIS*******************************************************
# **********************************************HMIS*******************************************************
def how_much_is_spent(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'

    else:
        try:
            date = 1
            try:
                #  преобразование сообщения пользователя в формат даты SQL
                date = event.object.message['text'].split()[1::]  # отрезаем "за "
                lst = [date[i] + '-' for i in range(1, len(date))]
                lst.reverse()
                lst.append(date[0])
                date = ''.join(lst)
                print(date)

            except TypeError:
                #  берём сообщение, преобразуем в список, убираем первое слово, преобразуем в строку
                answer(event, f"Не припоминаю трат за {''.join(event.object.message['text'].split()[1::])}")

            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            if date == 1:
                answer(event, 'Не припоминаю Ваших трат за это число')

            cur.execute(f"SELECT category_name,costs,time,date FROM expenses WHERE userid = '{user_id}' AND '{date}'")
            # выбираем столбец бюджет где дата равна запрашиваемой

            #  берём записи о тратах из выбранной даты
            records = cur.fetchall()
            lst_of_expenses = []
            for exp in records:
                lst_of_expenses.append(exp)

            conn.commit()
            cur.close()

            answer(event, f"За {lst_of_expenses[0][3]} Вы потратили:")

            for exp in lst_of_expenses:
                answer(event, f"\n{exp[1]} рублей на {exp[0]}, время покупки: {exp[2]}")

            answer(event, "Это все траты, о которых Вы мне рассказали")

        except sqlite3.Error as error:
            error_with_smt(event, error)
# ********************************************************************************************
# ********************************************************************************************
# ********************************************************************************************
# ********************************************************************************************


# *****************************************HMMC**********************************************
# *****************************************HMMC**********************************************
# *****************************************HMMC**********************************************
# *****************************************HMMC**********************************************
# *****************************************HMMC**********************************************
def how_much_may_cost(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'

    else:
        try:
            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute(f"SELECT budget FROM users WHERE userid = '{user_id}'")  # выбираем столбец с бюджетом
            budget = cur.fetchone()[0]  # берём это значение

            cur.execute(f"SELECT f_plan_n FROM users WHERE userid = '{user_id}'")  # выбираем столбец ф-плана необх.
            necessary = budget * cur.fetchone()[0]  # берём это значение
            cur.execute(f"SELECT f_plan_n FROM users WHERE userid = '{user_id}'")  # выбираем столбец ф-плана развлеч.
            other = budget * cur.fetchone()[0]  # берём это значение
            conn.commit()
            cur.close()
            answer(event, f'Вы можете потратить:\n{necessary}рублей на необходимое\n{other}рублей на развлечения')

        except sqlite3.Error as error:
            error_with_smt(event, error)
# ****************************************************************************************************
# ****************************************************************************************************
# ****************************************************************************************************
# ****************************************************************************************************
# ****************************************************************************************************


# *****************************************EXPENSES*****************************************************
# *****************************************EXPENSES*****************************************************
# *****************************************EXPENSES*****************************************************
# *****************************************EXPENSES*****************************************************
# *****************************************EXPENSES*****************************************************
def exp_id():
    conn = sqlite3.connect('database.db')  # подключение к бд
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
                conn = sqlite3.connect('database.db')  # подключение к бд
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
# **************************************************************************************************
# **************************************************************************************************
# **************************************************************************************************
# **************************************************************************************************
# **************************************************************************************************


# **************************************REGISTRATION************************************************
# **************************************REGISTRATION************************************************
# **************************************REGISTRATION************************************************
# **************************************REGISTRATION************************************************
# **************************************REGISTRATION************************************************
def pass_word(event):
    password = take_mes()
    if password:
        if len(password) < 4:
            answer(event, 'Слишком короткий пароль, минимум 4 символа, попробуйте снова')
            pass_word(event)
        else:
            return password
    else:
        if len(password) < 4:
            answer(event, 'Слишком короткий пароль, минимум 4 символа, попробуйте снова')
            pass_word(event)


def f_plan(event):
    answer(event, 'Отправьте мне номер выделенного финансового плана.\nФинансовые планы:\n1 - экономный '
                  '(40% необходимое, 20% развлечения, 40% в сбережения)\n2 - стандартный (50% необходимое, '
                  '20% развлечения, 30% в сбережения)\n3 - "жизнь одним днём" (50% необходимое, 40% развлечения'
                  '10% в сбережения)\n4 - составить свой план')

    # возвращает уже приведённое к нужному типу значение, сама рекурсивно запрашивает у пользователя повтор ввода
    chose = check_type(event, 'integer', 'Необходимо чтобы Вы ввели целое число, номер финансового плана')

    if chose == 1:
        return [0.4, 0.2, 0.4]
    elif chose == 2:
        return [0.5, 0.2, 0.3]
    elif chose == 3:
        return [0.4, 0.4, 0.1]

    elif chose == 4:
        answer(event, 'Сколько в процентнах Вы хотите выделить на необходимые траты, '
                      'например: 50 (что будет воспринято как 50%)')
        necessary = check_type(event, 'float', 'Необходимо чтобы Вы ввели количество процентов '
                                               '(если дробное, то через ".", пример: 99.9)')
        answer(event, 'Сколько в процентнах Вы хотите выделить на развлечения и необходимые траты, '
                      'например: 50 (что будет воспринято как 50%)')
        other = check_type(event, 'float', 'Необходимо чтобы Вы ввели количество процентов '
                                           '(если дробное, то через ".", пример: 99.9)')
        capital = 100 - (necessary + other)
        answer(event, f'Отлично остальные {round(capital, 2)}% буду уходить в накопления')

        return [round(necessary/100, 2), round(other/100, 2), round(capital/100, 2)]
    else:
        answer(event, 'Не понимаю Вас, нужно ввести номер финансового плана или "4", в случае, '
                      'если Вы хотите составить свой собственный')
        f_plan(event)


def delete_info(event):
    try:
        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        deciding_of_user = take_mes().lower()
        if deciding_of_user == 'да':
            # удаляем строку с данными пользователя с данным id
            cur.execute(f"DELETE FROM users WHERE userid = {event.obj.message['from_id']}")
            cur.execute(f"DELETE FROM expenses WHERE userid = {event.obj.message['from_id']}")
            answer(event, 'Данные о пользователе и его тратах успешно удалены')
            conn.commit()
            cur.close()
            registration(event)

        elif deciding_of_user == 'нет':
            cur.execute(f"SELECT name FROM users WHERE userid = {event.obj.message['from_id']}")
            name = cur.fetchone()[0]
            answer(event, f"Хорошо, тогда рад новой встрече, {name}")
            conn.commit()
            cur.close()

        else:
            answer(event, 'Не понимаю Вас, если Вы хотите стереть информацию отправьте "да" иначе отправьте "нет"')
            delete_info(event)

    except sqlite3.Error as error:
        error_with_smt(event, error)


def registration(event):
    us_id = does_user_exist(event)
    if us_id:
        answer(event, 'Похоже с вашего аккаунта ВК уже был выполнен вход в YourWalletAssistant, '
                      'желаете стереть данные о нём или продолжить работу в этом пользователе?\n\n'
                      'Стереть данные о предыдущем пользователе? (да/нет)')

        delete_info(event)
    else:
        answer(event, 'Как мне к Вам обращаться?')
        user_id = event.object.message['from_id']  # id отправителя присваивается id пользователя в системе
        name = take_mes()

        answer(event, 'Ваш бюджет будет разделён на 3 основные категории: на необходимые траты, '
                      'на развлечения и непредвиденные траты и на сбережения (накопления)')

        fin_plan = f_plan(event)
        necessary = fin_plan[0]
        other = fin_plan[1]
        capital = fin_plan[2]

        answer(event, 'Установите пароль для входа в систему с приложения на компьютере')
        password = pass_word(event)

        # answer(event, 'Если у Вас фиксировано 1 раз в месяц выплата зарплаты, то когда у Вас день зарплаты?'
        #               '\n(Пример: 13\n[это будет значить, что каждый месяц 13ого числа Вам выплачивается заработная'
        #               ' плата и остаток прибавляется к сбережениям])\n\n'
        #               'Если у Вас бюджет пополняется с разной периодичностью, введите "0"')
        #
        # start_day = check_type(event, 'integer', 'Я Вас не понимаю, нужно ввести число месяца, когда выплачивается '
        #                                          'заработная плата')
        # if (start_day < 1) or (start_day > 28):
        #     start_day = None
        #     if start_day != 0:
        #         answer(event, 'По моим данным, ЗП в большинстве случаев выплачивают с 1ого по 28ое число каждого '
        #                       'месяца, поэтому Вам придётся вручную обновлять бюджет в день ЗП')

        answer(event, 'Какой у Вас бюджет до дня зарплаты?')
        budget = check_type(event, 'float', 'Я Вас не понимаю, нужно ввести количество денежных единиц, '
                                            'которые Вы можете потратить до дня зарплаты')

        answer(event, 'Скажите, у Вас есть какие либо сбережения уже (сколько у Вас отложено в копилке),'
                      ' если нет, введите 0')
        acc = check_type(event, 'float', 'Я Вас не понимаю, нужно ввести количество денежных единиц, '
                                         'которые сейчас лежат у вас накопленях')

        full_data = [user_id, name, budget, necessary, other, capital, str(password), acc]

        try:
            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute("INSERT INTO users (userid, name, budget, f_plan_n, f_plan_o, f_plan_c, password, "
                        "accumulation) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", full_data)
            answer(event, f'Приятно познакомиться, {name}, Вы успешно зарегистрированы!')
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            error_with_smt(event, error)
# **************************************************************************************************************
# **************************************************************************************************************
# **************************************************************************************************************
# **************************************************************************************************************


def main():
    vk_session = vk_api.VkApi(
        token='360c9391be9e818c234c23236b6d52a8fc95949d3fb7113bae23c1b8392fcbd0bcff35aa316fd95c90e5e')

    longpoll = VkBotLongPoll(vk_session, '212752190')

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            global vk
            vk = vk_session.get_api()

            if event.obj.message['text'].lower().startswith('привет') or \
                    event.obj.message['text'].lower().startswith('здравствуй'):
                mes = "Приветствую, я воспринимаю лишь следующие команды (Если я тебя не пойму, " \
                      "то соответственно не отвечу!):\n\n " \
                      "Если Вы зарегистрированы в системе 'Ваш финансовый помощник':\n\n" \
                      "1) '-<число> (пример: -999.99)'\n" \
                      "2) 'остаток'\n" \
                      "3) 'сколько за <дата>'\n" \
                      "4) 'сбережения'\n\n" \
                      "Если Вы не зарегистрированы:\n\n" \
                      "1) 'как зарегистрироваться?'\n" \
                      "2) 'зачем ты мне?\n" \
                      "3) 'что ты умеешь?'"
                answer(event, mes)

            elif event.obj.message['text'].lower().startswith('как зарегистрироваться'):
                answer(event, 'Чтобы зарегистрироваться введите: "?"')

            elif event.obj.message['text'].lower().startswith('?'):
                registration(event)

            elif event.obj.message['text'].lower().startswith('зачем ты мне'):
                answer(event, "Я помогу Вам усилить контроль над собственными финансами"
                              "и тем самым помочь правильно их распределять")

            elif event.obj.message['text'].lower().startswith('что ты умеешь'):
                answer(event, 'Мои возможности:\nЧтобы добавить трату отправьте мне: '
                              '"-<число> (пример: -999.99)"\n\n'
                              'Чтобы узнать сколько Вы можете потратить отправьте мне:\n'
                              '"остаток"\n'
                              'Чтобы узнать сколько Вы потратили за определённый день отправьте мне:\n'
                              '"за <дата> (пример: за 22 11 1970)"\n'
                              'Чтобы узнать сколько у Вас накоплений отправьте мне: '
                              '"сбережения"')

            elif event.obj.message['text'].lower().startswith('-'):
                expenses(event)

            elif event.obj.message['text'].lower().startswith('остаток'):
                how_much_may_cost(event)

            elif event.obj.message['text'].lower().startswith('сколько за'):
                how_much_is_spent(event)

            elif event.obj.message['text'].lower().startswith('сбережения'):
                my_bank(event)

            elif event.obj.message['text'].lower().startswith('обо мне'):
                about_me(event)

            elif event.obj.message['text'].lower().startswith('день зп'):
                reset(event)


if __name__ == '__main__':
    main()
