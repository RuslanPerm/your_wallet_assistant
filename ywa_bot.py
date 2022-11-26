import sqlite3
import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from modules_for_bot.h_m_m_c import how_much_may_cost
from modules_for_bot.h_m_i_s import how_much_is_spent
from modules_for_bot.reg import registration
from modules_for_bot.exp import expenses
from modules_for_bot.bank import my_bank


# функция, проверяющая тип, 2ой аргумент - название необходимого типа данных, а 3ий сообщение юзеру в случае ошибки
def check_type(event, need_type, if_error):
    user_mes = take_mes()

    if need_type == 'integer':
        try:
            user_mes = int(user_mes)
            return user_mes
        except TypeError:
            answer(event, if_error)
    elif need_type == 'float':
        try:
            user_mes = float(user_mes)
            return user_mes
        except TypeError:
            answer(event, if_error)
            answer(event, 'Попробуйте ещё раз')
            check_type(event, need_type, if_error)


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
