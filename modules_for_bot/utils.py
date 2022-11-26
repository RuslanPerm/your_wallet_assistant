import sqlite3
import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


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
