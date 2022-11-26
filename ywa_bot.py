import sqlite3
import vk_api
import random
import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


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


# функция, отвечающая сколько сбережений/накоплений у пользователя
def my_bank(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'
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

            cur.execute(f"SELECT category_name, costs, time, date FROM expenses WHERE userid = '{user_id}' AND '{date}'")
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


def how_much_may_cost(event):
    user_id = does_user_exist(event)

    if not user_id:
        return 'Похоже Вы не зарегистрированы в системе, чтобы зарегистрироваться введите: "?"'

    else:
        try:
            conn = sqlite3.connect('database.db')  # подключение к бд
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
                # сделать чтобы айди траты заносилось или генирировалось
                # сделать чтобы вычитал из бюджета

                conn.commit()
                cur.close()
                answer(event, "Данные о трате успешно записаны!")

            except TypeError:
                answer(event, 'Не понимаю, введите количество потраченных денежных единиц, введите ещё раз, пожалуйста')
        except sqlite3.Error as error:
            error_with_smt(event, error)


# зацикливается если у последнего элз убрать условие, да и в таком виде багает
def delete_info(event):
    try:
        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        deciding_of_user = take_mes()
        if deciding_of_user == 'стереть':
            # удаляем строку с данными пользователя с данным id
            cur.execute(f"DELETE FROM users WHERE userid = {event.obj.message['from_id']}")
            cur.execute(f"DELETE FROM expenses WHERE userid = {event.obj.message['from_id']}")
            answer(event, 'Данные о пользователе и его тратах успешно удалены')
            conn.commit()
            cur.close()

        elif deciding_of_user == 'ладно':
            cur.execute(f"SELECT name FROM users WHERE userid = {event.obj.message['from_id']}")
            name = cur.fetchone()[0]
            answer(event, f"Хорошо, тогда рад новой встрече, {name}")
            conn.commit()
            cur.close()

    except sqlite3.Error as error:
        error_with_smt(event, error)


def registration(event):
    us_id = does_user_exist(event)
    if us_id:
        answer(event, 'Похоже с вашего аккаунта ВК уже был выполнен вход в YourWalletAssistant, '
                      'желаете стереть данные о нём или продолжить работу в этом пользователе?\n\n'
                      'Отправьте мне "стереть" если желаете стереть данные о нём\n'
                      'Отправьте мне "ладно" если желаете продолжить')

        delete_info(event)
    else:
        answer(event, 'Как мне к Вам обращаться?')
        user_id = event.object.message['from_id']  # id отправителя присваивается id пользователя в системе
        name = take_mes()

        answer(event, 'Выберите Ваш финансовый план и напишите мне его номер\n\n'
                      '1 - экономный: от Вашего бюджета 40% на необходимые вещи, 20% на другое 40% на сбережения\n\n'
                      '2 - стандартный: от Вашего бюджета 50% на необходимые вещи, 20% на другое 30% на сбережения\n\n'
                      '3 - "жизнь одним днём": от Вашего бюджета 50% на необходимые вещи, 20% на другое '
                      '30% на сбережения\n\n'
                      'К необходимым вещам относятся: оплата жилья, продуктов, ЖКХ, связь, налоги и т.д.\n\n'
                      'К другому относятся: развлечение (кафе, доставка еды, аксессуары и т.д.)\n\n'
                      'Заостряю внимание, что я лишь подсказываю, реальное распределение трат '
                      'по важности исключительно Ваш выбор')

        f_plan = take_mes()
        answer(event, 'Установите пароль для входа в систему с приложения')
        password = take_mes()
        answer(event, 'Какой у Вас бюджет до дня зарплаты?')
        budget = take_mes()
        answer(event, 'Если у Вас фиксировано 1 раз в месяц выплата зарплаты, то когда у Вас день зарплаты?'
                      '\n(Пример:\n13 [это будет значить, что каждый месяц 13ого числа Вам выплачивается заработная'
                      ' плата и остаток прибавляется к сбережениям])\n\n'
                      'Если у Вас бюджет пополняется с разной периодичностью, введите "."')
        start_day = take_mes()
        if start_day == '.':
            start_day = None
        else:
            try:
                int(start_day)
            except TypeError:
                answer(event, 'Я Вас не понимаю, нужно ввести число месяца, когда платится заработная плата')

        answer(event, 'Скажите, у Вас есть какие либо сбережения уже (сколько у Вас отложено в копилке),'
                      ' если нет, введите 0')
        acc = take_mes()
        full_data = [user_id, name, budget, f_plan, str(password), acc, start_day]

        try:
            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute("INSERT INTO users (userid, name, budget, f_plan, password, accumulation, start_day) "
                        "VALUES(?, ?, ?, ?, ?, ?, ?)", full_data)
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            error_with_smt(event, error)
        answer(event, f'Приятно познакомиться, {name}, Вы успешно зарегистрированы!')


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
                      "3) 'за <дата>'\n" \
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

            elif event.obj.message['text'].lower().startswith('за'):
                how_much_is_spent(event)

            elif event.obj.message['text'].lower().startswith('сбережения'):
                my_bank(event)


if __name__ == '__main__':
    main()
