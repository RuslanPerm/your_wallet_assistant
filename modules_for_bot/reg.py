import sqlite3
from utils import take_mes, answer, error_with_smt, does_user_exist, check_type


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
        answer(event, 'Сколько в процентнах Вы хотите выделить в сбережения, '
                      'например: 50 (что будет воспринято как 50%)')
        capital = check_type(event, 'float', 'Необходимо чтобы Вы ввели количество процентов '
                                             '(если дробное, то через ".", пример: 99.9)')
        return [necessary, other, capital]
    else:
        answer(event, 'Не понимаю Вас, нужно ввести номер финансового плана или "4", в случае, '
                      'если Вы хотите составить свой собственный')
        f_plan(event)


def delete_info(event):
    try:
        conn = sqlite3.connect('../database.db')  # подключение к бд
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

        answer(event, 'Ваш бюджет будет разделён на 3 основные категории: на необходимые траты, '
                      'на развлечения и непредвиденные траты и на сбережения (накопления)')

        fin_plan = f_plan(event)
        necessary = fin_plan[0]
        other = fin_plan[1]
        capital = fin_plan[2]

        answer(event, 'Установите пароль для входа в систему с приложения на компьютере')
        password = pass_word(event)

        answer(event, 'Если у Вас фиксировано 1 раз в месяц выплата зарплаты, то когда у Вас день зарплаты?'
                      '\n(Пример: 13\n[это будет значить, что каждый месяц 13ого числа Вам выплачивается заработная'
                      ' плата и остаток прибавляется к сбережениям])\n\n'
                      'Если у Вас бюджет пополняется с разной периодичностью, введите "."')
        start_day = take_mes()
        if start_day == '.':
            start_day = None
        else:
            start_day = check_type(event, 'integer', 'Я Вас не понимаю, нужно ввести число месяца, когда выплачивается '
                                                     'заработная плата')

        answer(event, 'Какой у Вас бюджет до дня зарплаты?')
        budget = check_type(event, 'float', 'Я Вас не понимаю, нужно ввести количество денежных единиц, '
                                            'которые Вы можете потратить до дня зарплаты')

        answer(event, 'Скажите, у Вас есть какие либо сбережения уже (сколько у Вас отложено в копилке),'
                      ' если нет, введите 0')
        acc = check_type(event, 'float', 'Я Вас не понимаю, нужно ввести количество денежных единиц, '
                                         'которые сейчас лежат у вас накопленях')

        full_data = [user_id, name, budget, necessary, other, capital, str(password), acc, start_day]

        try:
            conn = sqlite3.connect('../database.db')  # подключение к бд
            cur = conn.cursor()  # создаём объект соединения с бд, к-й позволяет делать запросы бд

            cur.execute("INSERT INTO users (userid, name, budget, f_plan_n, f_plan_o, f_plan_c, password, "
                        "accumulation, start_day) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", full_data)
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            error_with_smt(event, error)
        answer(event, f'Приятно познакомиться, {name}, Вы успешно зарегистрированы!')