import sqlite3

import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


def registration(event):
    try:
        u_d = event.obj.message['text'].split()  # user data данные о пользователе
        user_id = event.object.message['from_id']  # id отправителя

        conn = sqlite3.connect('database.db')  # подключение к бд
        cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

        full_data = [user_id, u_d[1], u_d[2], u_d[3], u_d[4], u_d[5]]
        cur.execute("INSERT INTO users (userid, name, budget, f_plan, password, accumulation) "
                    "VALUES(?, ?, ?, ?, ?, ?)", full_data)
        conn.commit()
        cur.close()

        return f"Приятно познакомиться, {u_d[1]}, первый этап регистрации Вы прошли!\n\n" \
               f"Небольшая рекомендация по использованию бота: периодически очищайте диалог с этим ботом для " \
               f"профилактики утечки данных"

    except TypeError:
        return "Не могу понять Ваши данные, введите пожалуйста в виде доступных мне символов"


def hi(event):
    vk.messages.send(user_id=event.obj['message']['from_id'],
                     message=f"Приветствую, я воспринимаю лишь следующие команды:\n\n"
                             f"Если Вы зарегистрированы в системе 'Ваш финансовый помощник':\n\n"
                             f"1) 'потрачено <стоимость> <категория> <подкатегория> <стоимость>'\n"
                             f"2) 'сколько я могу потратить?'\n"
                             f"3) 'сколько потрачено за <дата>?'\n"
                             f"4) 'сколько у меня сбережений?'\n\n"
                             f"Если Вы не зарегистрированы:\n\n"
                             f"1) 'как зарегистрироваться?'\n"
                             f"2) 'зачем ты мне?"
                             f"3) 'что ты умеешь?'",
                     random_id=random.randint(0, 2 ** 64))


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
                hi(event)

            elif event.obj.message['text'].lower().startswith('как зарегистрироваться'):
                vk.messages.send(user_id=event.obj['message']['from_id'],
                                 message="Чтобы зарегистрироваться введите сообщение аналогично данному примеру:\n"
                                         "?ИМЯ БЮДЖЕТ №_ФИН_ПЛАНА_(1/2/3) ПАРОЛЬ НАКОПЛЕНО",
                                 random_id=random.randint(0, 2 ** 64))

            elif event.obj.message['text'].lower().startswith('?'):
                vk.messages.send(user_id=event.obj['message']['from_id'],
                                 message=registration(event),
                                 random_id=random.randint(0, 2 ** 64))

            elif event.obj.message['text'].lower().startswith('зачем ты мне?'):
                vk.messages.send(user_id=event.obj['message']['from_id'],
                                 message="Я помогу Вам усилить контроль над собственными финансами"
                                         "и тем самым помочь правильно их распределять",
                                 random_id=random.randint(0, 2 ** 64))

            elif event.obj.message['text'].lower().startswith('что ты умеешь?'):
                vk.messages.send(user_id=event.obj['message']['from_id'],
                                 message='Мои возможности:\nЧтобы добавить трату отправьте мне: '
                                         '"потрачено <стоимость> <категория> <подкатегория> <стоимость>"\n'
                                         'Чтобы узнать сколько Вы можете потратить отправьте мне: '
                                         '"сколько я могу потратить?"\n'
                                         'Чтобы узнать сколько Вы потратили за определённый день отправьте мне: '
                                         '"сколько потрачено <дата>?"\n'
                                         'Чтобы узнать сколько у Вас накоплений отправьте мне: '
                                         '"сколько у меня сбережений?"',
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()


