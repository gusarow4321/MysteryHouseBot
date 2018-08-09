import telebot
import config
import database

bot = telebot.TeleBot(config.token)

users = dict()  # словарь пользователей с их прогрессом (название комнаты) и строкой событий (собранные предметы и т.п.)

# создание кнопок
def create_markup(t):
    m = telebot.types.InlineKeyboardMarkup()
    for b in t:
        m.add(telebot.types.InlineKeyboardButton(b[0], callback_data=b[1]))
    return m

# отправка сообщения. Если имя изображения есть в папке img - отправит картинку с подписью, а если нет, то отправит просто текст
def send_mes(user_id, to_send, img_name):
    try:
        with open("img\\" + img_name + ".png", 'rb') as photo:
            bot.send_photo(user_id, photo, to_send["text"], reply_markup=create_markup(to_send["markup"]))
    except FileNotFoundError:
        bot.send_message(user_id, to_send["text"], reply_markup=create_markup(to_send["markup"]))


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    start_game = telebot.types.InlineKeyboardButton("🎮 Начать игру", callback_data="start game")
    about_game = telebot.types.InlineKeyboardButton("❔ Информация об игре", callback_data="about")
    markup.add(start_game, about_game)
    bot.send_message(message.from_user.id, config.start_mes, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    user_id = call.from_user.id
    # Проверяет тип предыдущего сообщ. и изменяет его (убирает кнопки)
    if call.message.content_type == 'text':
        bot.edit_message_text(call.message.text, user_id, call.message.message_id)
    elif call.message.content_type == 'photo':
        bot.edit_message_caption(call.message.caption, user_id, call.message.message_id)

    if data == "start game":
        room, events = database.add_player(user_id, call.from_user.first_name)  # Выбирает из бд данные о пользователе
        users[user_id] = [room, events]  # записывает в словарь
        send_mes(user_id, config.events[room], room)  # и отправляет нужное сообщение
        return
    elif data == "about":
        ab_markup = telebot.types.InlineKeyboardMarkup()
        ab_markup.add(telebot.types.InlineKeyboardButton("🎮 Начать игру", callback_data="start game"))
        bot.send_message(user_id, config.about, reply_markup=ab_markup)
        return
    else:
        if data in users[user_id][1]:  # проверяет случалось ли событие. И если да, то изменяет data
            data = 'not ' + data
        to_send = config.events[data]  # выборка из events 
        users[user_id][0] = data  # запись прогресса
        if 'command' in to_send:  # особые команды, такие как добавить событие или конец игры
            command = to_send['command'].split(' ')
            if 'add' in command:
                users[user_id][1] += command[1] + ' '  # добавление событий в строку через пробел
                database.update_user(user_id, users[user_id][0], users[user_id][1])  # запись в бд
            elif 'fire' in command:  # пожар в столовой
                # если условия верны (то есть у игрока есть кувшин с водой и пожар не случался ранее)
                if 'fire' not in users[user_id][1] and 'pitcher' in users[user_id][1]:
                    users[user_id][1] += 'fire '  # добавление событий в строку через пробел
                    send_mes(user_id, config.events['fire'], 'fire')  # отправляет особое сообщ. о пожаре
                    return
            elif 'end_of_game' in command:
                users[user_id][1] = ''  # теперь если игрок погибает, то обнуляется его список событий 
                database.update_user(user_id, 'yard', '')  # а следующим ходом он попадает на yard, то есть в самую первую локацию

        send_mes(user_id, to_send, data)  # в конце отправляет сообщение


if __name__ == "__main__":
    bot.polling(none_stop=True)
