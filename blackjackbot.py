import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import concurrent.futures
import time
import asyncio
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

token = "enter your token here"
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, "enter your group id here")


def send_message_with_keyboard(id, text, keyboard=None):
    vk_session.method(
        'messages.send',
        {
            'chat_id': id,
            'message': text,
            'random_id': 0,
            'keyboard': keyboard.get_keyboard() if keyboard else None,
        }
    )


def start_game_menu(keyboard=None):
    pass


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('+', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('-', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('go', color=VkKeyboardColor.PRIMARY)
    return keyboard


def create_start_keyboard():
    start_key_board = VkKeyboard(one_time=True)
    start_key_board.add_button('/start', color=VkKeyboardColor.POSITIVE)
    return start_key_board


def take_card(player: list, decka: list) -> None:
    try:
        elem = decka[0]
        decka.pop(0)
        if (len(player) == 2) and (sum(player) == 20) and (elem == 11):
            elem = 1
        player.append(elem)

    except Exception:
        print("Колода закончилась")


def send_message(id, text):
    vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})


def sen_message_private(user_id, text):
    vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': 0})


async def async_timer(second):
    while second > 0:
        print(f"Осталось {second} секунд")
        await asyncio.sleep(1)
        second -= 1
    print("Таймер завершился")


# send_message(25, 'Соси меня')


def event_worker(event):
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:
            chat_id = event.chat_id
            print(chat_id)
            message = event.message
            msg = event.object.message['text'].lower()
            print(msg)
            text = msg
            admin_id = message['from_id']
            ##########
            # vk = vk_session.get_api()
            # user_info = vk.users.get(user_ids=admin_id)
            # user_name = user_info[0]['first_name']
            # send_message(chat_id, user_name)
            ##########

            if '/start' in msg:
                king = 10
                queen = 10
                jack = 10
                ace = 11

                deck = [ace, 2, 3, 4, 5, 6, 7, 8, 9, 10, king, queen, jack] * 4
                random.shuffle(deck)
                players_num = 0
                id_list = list()
                timer = 10
                start_game_status = 0

                try:
                    # send_message(chat_id, 'Для участия введите +')
                    send_message_with_keyboard(chat_id, 'Для участия введите +', create_keyboard())
                    for event in longpoll.listen():
                        chat_id = event.chat_id
                        message = event.message
                        msg = event.object.message['text'].lower()
                        text = msg
                        user_id = message['from_id']
                        if '+' in msg and user_id not in id_list:
                            id_list.append(user_id)
                            players_num += 1
                            print(players_num, '\n', id_list)
                        send_message_with_keyboard(chat_id, f'Сейчас {players_num} игроков', create_keyboard())
                        if 'go' in msg:
                            send_message(chat_id, f'Всего игроков {players_num+1}')
                            diller_mudack = []
                            players = [[] for _ in range(players_num)]
                            players.append(diller_mudack)
                            id_list.append('')
                            counter_21 = 0
                            less_21_counter = 0
                            winner = None
                            inactive_players = []
                            while True:
                                for i_p in range(len(players)):
                                    if i_p != len(players) - 1 and (i_p not in inactive_players) and not (
                                            sum(players[i_p]) > 21):
                                        vk = vk_session.get_api()
                                        user_info = vk.users.get(user_ids=id_list[i_p])
                                        user_name = user_info[0]['first_name']
                                        send_message_with_keyboard(chat_id, f'{user_name} ваши действия ?(+-)', create_keyboard())
                                        for event in longpoll.listen():
                                            chat_id = event.chat_id
                                            message = event.message
                                            msg = event.object.message['text'].lower()
                                            text = msg
                                            user_id = message['from_id']
                                            if '+' in msg and user_id == id_list[i_p]:
                                                take_card(players[i_p], deck)
                                                vk = vk_session.get_api()
                                                user_info = vk.users.get(user_ids=id_list[i_p])
                                                user_name = user_info[0]['first_name']
                                                send_message(chat_id, f'{user_name} ваш счет: {sum(players[i_p])}')
                                                break
                                            elif '-' in msg and user_id == id_list[i_p]:
                                                inactive_players.append(i_p)
                                                break
                                            else:
                                                send_message(chat_id, 'Тебе нельзя ходить за других людей')
                                                send_message_with_keyboard(chat_id, f'{user_name} ваши действия ?(+-)',
                                                                           create_keyboard())

                                    else:
                                        if i_p not in inactive_players:
                                            if sum(diller_mudack) < 17:
                                                take_card(diller_mudack, deck)
                                                send_message(chat_id, f'Счет Шлёпы: {sum(diller_mudack)}')
                                            else:
                                                send_message(chat_id, f'Шлёпа пропускает ход ({sum(diller_mudack)})')
                                                inactive_players.append(i_p)
                                        else:
                                            pass

                                if len(inactive_players) == players_num + 1:
                                    for i_p in range(len(players)):
                                        if sum(players[i_p]) == 21:
                                            counter_21 += 1
                                            winner = i_p
                                    if counter_21 >= 2:
                                        send_message(chat_id, 'Победил Шлёпа\nЛадно, шутка, это ничья')
                                        send_message_with_keyboard(chat_id, 'Для начала напишите /start',
                                                                   create_start_keyboard())
                                    elif counter_21 == 1:

                                        vk = vk_session.get_api()
                                        user_info = vk.users.get(user_ids=id_list[winner])
                                        user_name = user_info[0]['first_name']

                                        send_message(chat_id, f"Победил {user_name}")
                                        send_message_with_keyboard(chat_id, 'Для начала напишите /start',
                                                                   create_start_keyboard())
                                        break
                                    else:
                                        for i_p in range(len(players)):
                                            if sum(players[i_p]) < 21:
                                                less_21_counter += 1
                                        if less_21_counter >= 1:
                                            max_score = 0
                                            winner = None
                                            for i_p in range(len(players)):
                                                if sum(players[i_p]) > 21:
                                                    pass
                                                else:
                                                    if sum(players[i_p]) > max_score:
                                                        winner = i_p + 1
                                                        max_score = sum(players[i_p])
                                                    elif sum(players[i_p]) == max_score:
                                                        winner = "Ничья"

                                                        break
                                            if winner == "Ничья":
                                                send_message(chat_id, "Победил Шлёпа\nЛадно, шутка, это ничья")
                                                send_message_with_keyboard(chat_id, 'Для начала напишите /start',
                                                                           create_start_keyboard())
                                                break
                                            else:

                                                vk = vk_session.get_api()
                                                user_info = vk.users.get(user_ids=id_list[winner-1])
                                                user_name = user_info[0]['first_name']
                                                if user_name == str(players_num+1):
                                                    send_message(chat_id, 'Победил Шлёпа')
                                                    send_message_with_keyboard(chat_id, 'Для начала напишите /start',
                                                                               create_start_keyboard())
                                                else:
                                                    send_message(chat_id, f"Победил {user_name}")
                                                    send_message_with_keyboard(chat_id, 'Для начала напишите /start',
                                                                               create_start_keyboard())
                                                break
                                        else:
                                            # min_score = 9999999
                                            # winner = None
                                            # for i_p in range(len(players)):
                                            #     if sum(players[i_p]) < min_score:
                                            send_message(chat_id, 'Проиграли вообще все')
                                            print("Проиграли вообще все")
                                            send_message_with_keyboard(chat_id, 'Для начала напишите /start',
                                                                       create_start_keyboard())
                                            break
                                    break
                            break

                except BaseException as e:
                    print(e)
                    send_message(chat_id, text='Победил Шлёпа')
                    send_message_with_keyboard(chat_id, 'Для начала напишите /start', create_start_keyboard())


        else:
            message = event.message
            msg = event.object.message['text'].lower()
            user_id = message['from_id']
            if msg == '/start':
                try:
                    print('Работаем')
                    pass
                except:
                    sen_message_private(user_id, text='Произошла ошибка, повторите запрос.')



while True:
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

            for event in longpoll.listen():
                executor.submit(event_worker, event)
    except Exception:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

            for event in longpoll.listen():
                executor.submit(event_worker, event)
