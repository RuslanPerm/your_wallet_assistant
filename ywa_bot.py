import sqlite3
import vk_api
import random
import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


def error_with_smt(event, error):
    print("Ошибка при работе с БД", error)
    answer(event, "Ошибка сервера, приносим свои извинения, устроняем проблему")


def answer(event, message):
    vk.messages.send(user_id=event.obj['message']['from_id'],
                     message=message,
                     random_id=random.randint(0, 2 ** 64))


def does_user_exist(ev):
    try:  # так как программа устанавливает в userid только целочисленные значения,
        # то пробуем узнать айди пользователя, если выдаст ошибку, значит пользователя не существует
        user_id = int(ev.object.message['from_id'])
        return user_id

    except TypeError:
        return 0.2


def my_bank(event):
    user_id = does_user_exist(event)

    if user_id == 0.2:
        return 'Похоже Вы не зарегистрированы в системе, что бы зарегистрироваться напишите мне ' \
               '"как зарегестрироваться?"'
    else:
        try:
            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute(f"SELECT accumulation FROM users WHERE userid = '{user_id}'")
            # выбираем столбец сбережения где айди пользователя равен айди пользователя, который запрашивает

            user_acc = cur.fetchone()

            answer(event, user_acc[0])

        except sqlite3.Error as error:
            error_with_smt(event, error)


def how_much_is_spent(event):
    user_id = does_user_exist(event)

    if user_id == 1:
        answer(event, 'Похоже Вы не зарегистрированы в системе, что бы зарегистрироваться напишите мне '
                      '"как зарегестрироваться?"')
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

    if user_id == 1:
        return 'Похоже Вы не зарегистрированы в системе, что бы зарегистрироваться напишите мне ' \
               '"как зарегестрироваться?"'
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
                return [necessary, other]

            elif f_plan == 2:
                necessary = balance * 0.5
                other = balance * 0.2
                return [necessary, other]

            elif f_plan == 3:
                necessary = balance * 0.5
                other = balance * 0.4
                return [necessary, other]

            else:
                error_with_smt(event, 'idk (ツ)')

        except sqlite3.Error as error:
            error_with_smt(event, error)


def expenses(event):
    user_id = does_user_exist(event)

    if user_id == 1:
        answer(event, 'Похоже Вы не зарегистрированы в системе, что бы зарегистрироваться напишите мне '
                      '"как зарегестрироваться?"')
    else:

        try:
            text = event.obj.message['text'].split()

            conn = sqlite3.connect('database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            # exp_data = [user_id, sub_category_id(text[3]), text[3], text[2], text[1],
            #             str(datetime.datetime.now())[:-10:]]

            exp_data = [user_id, text[3], text[2], text[1],
                        str(datetime.datetime.now())[:-16:], str(datetime.datetime.now())[10:-10:]]

            cur.execute("INSERT INTO expenses (userid, category_name, importance, costs, date, time) "
                        "VALUES(?, ?, ?, ?, ?, ?)", exp_data)

            # сделать чтобы вычитал из бюджета

            conn.commit()
            cur.close()
            answer(event, "Данные о трате успешно записаны!")

        except sqlite3.Error as error:
            error_with_smt(event, error)


# зацикливается если у последнего элз убрать условие, да и в таком виде багает

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


def registration(event):
    answer(event, 'Как мне к Вам обращаться?')
    user_id = event.object.message['from_id']  # id отправителя присваивается id пользователя в системе
    name = take_mes()

    answer(event, 'Выберите Ваш финансовый план и напишите мне его номер\n\n'
                  '1 - экономный: от Вашего бюджета 40% на необходимые вещи, 20% на другое 40% на сбережения\n\n'
                  '2 - стандартный: от Вашего бюджета 50% на необходимые вещи, 20% на другое 30% на сбережения\n\n'
                  '3 - "жизнь одним днём": от Вашего бюджета 50% на необходимые вещи, 20% на другое '
                  '30% на сбережения\n\n'
                  'К необходимым вещам относятся: оплата жилья, продуктов, ЖКХ, связь, образование, налоги и т.д.\n\n'
                  'К другому относятся: развлечение (кафе, доставка еды, аксессуары и т.д.)\n\n'
                  'Заостряю внимание, что я лишь подсказываю, реальное распределение трат '
                  'по важности исключительно Ваш выбор')
    f_plan = take_mes()
    answer(event, 'Установите пароль (более 8 символов) для входа в систему с приложения')
    password = take_mes()
    answer(event, 'Какой у вас бюджет на этот месяц?')
    budget = take_mes()
    answer(event, 'Скажите, у Вас есть какие либо сбережения уже (именно сбережения, а не бюджет), если нет, введите 0')
    acc = take_mes()
    full_data = [user_id, name, budget, f_plan, str(password), acc]

    try:
        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        try:
            cur.execute("INSERT INTO users (userid, name, budget, f_plan, password, accumulation) "
                        "VALUES(?, ?, ?, ?, ?, ?)", full_data)
        except sqlite3.IntegrityError:
            answer(event, 'Похоже с вашего аккаунта ВК уже был выполнен вход в YourWalletAssistant, '
                          'желаете стереть данные о нём или продолжить работу в этом пользователе?\n\n'
                          'Отправьте мне "стереть" если желаете стереть данные о нём\n'
                          'Отправьте мне "ладно" если желаете продолжить')
            if take_mes() == 'стереть':
                # удаляем строку с данными пользователя с данным id
                cur.execute(f"DELETE FROM users WHERE userid = {event.obj.message['from_id']}")
                answer(event, 'Данные успешно удалены')
                conn.commit()
                cur.close()
                return 0
            if take_mes() == 'ладно':
                print('тут норм')
                cur.execute(f'SELECT name FROM users WHERE userid = "{user_id}"')
                print('тут тоже')
                name = cur.fetchone()[0]
                answer(event, f"Хорошо, тогда рад новой встрече, {name}")
                conn.commit()
                cur.close()
                return 0
        finally:
            conn.commit()
            cur.close()
    except sqlite3.Error as error:
        error_with_smt(event, error)
    answer(event, f'Приятно познакомиться, {name}, Вы успешно зарегистрированы!')

    # try:
    #     u_d = event.obj.message['text'].split()  # user data данные о пользователе
    #     user_id = event.object.message['from_id']  # id отправителя
    #
    #     conn = sqlite3.connect('database.db')  # подключение к бд
    #     cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд
    #
    #     full_data = [user_id, u_d[1], u_d[2], u_d[3], u_d[4], u_d[5]]
    #     cur.execute("INSERT INTO users (userid, name, budget, f_plan, password, accumulation) "
    #                 "VALUES(?, ?, ?, ?, ?, ?)", full_data)
    #     conn.commit()
    #     cur.close()
    #
    #     answer(event, f"Приятно познакомиться, {u_d[1]}, первый этап регистрации Вы прошли!\n\n "
    #                   f"Небольшая рекомендация по использованию бота: периодически очищайте диалог с этим ботом для "
    #                   f"профилактики утечки данных")
    #
    # except TypeError or sqlite3.Error:
    #     answer(event, "Не могу понять Ваши данные, введите пожалуйста в виде доступных мне символов")


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
                      "1) 'потрачено <стоимость> <уровень важности (1 [необходимое] или 2 [другое])> " \
                      "<подкатегория (название траты)>'\n" \
                      "2) 'остаток?'\n" \
                      "3) 'за <дата>'\n" \
                      "4) 'сбережения?'\n\n" \
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
                              '"потрачено <стоимость> <категория> <подкатегория>"\n'
                              'Пример: "потрачено 100 1 продукты"\n\n'
                              'Чтобы узнать сколько Вы можете потратить отправьте мне:\n'
                              '"остаток"\n'
                              'Чтобы узнать сколько Вы потратили за определённый день отправьте мне:\n'
                              '"за <дата> (пример: за 22 11 1970)"\n'
                              'Чтобы узнать сколько у Вас накоплений отправьте мне: '
                              '"сбережения"')

            elif event.obj.message['text'].lower().startswith('потрачено'):
                expenses(event)

            elif event.obj.message['text'].lower().startswith('остаток'):
                vk.messages.send(user_id=event.obj['message']['from_id'],
                                 message=f'Вы можете потратить:\n{how_much_may_cost(event)[0]} на необходимые траты'
                                         f'\n{how_much_may_cost(event)[1]} на развлечения',
                                 random_id=random.randint(0, 2 ** 64))

            elif event.obj.message['text'].lower().startswith('за'):
                how_much_is_spent(event)

            elif event.obj.message['text'].lower().startswith('сбережения'):
                my_bank(event)

            # else:
            #     answer(event, "К сожалению, я могу лишь отвечать на установленные команды, "
            #                   "чтобы увидеть список моих команд отправьте мне 'что ты умеешь?'")


# is_reg_right_now = 0
if __name__ == '__main__':
    main()
