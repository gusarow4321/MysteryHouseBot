import telebot
import config
import database

bot = telebot.TeleBot(config.token)

users = dict()


def create_markup(t):
    m = telebot.types.InlineKeyboardMarkup()
    for b in t:
        m.add(telebot.types.InlineKeyboardButton(b[0], callback_data=b[1]))
    return m


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

    if call.message.content_type == 'text':
        bot.edit_message_text(call.message.text, user_id, call.message.message_id)
    elif call.message.content_type == 'photo':
        bot.edit_message_caption(call.message.caption, user_id, call.message.message_id)

    if data == "start game":
        room, events = database.add_player(user_id, call.from_user.first_name)
        users[user_id] = [room, events]
        send_mes(user_id, config.events[room], room)
        return
    elif data == "about":
        ab_markup = telebot.types.InlineKeyboardMarkup()
        ab_markup.add(telebot.types.InlineKeyboardButton("🎮 Начать игру", callback_data="start game"))
        bot.send_message(user_id, config.about, reply_markup=ab_markup)
        return
    else:
        if data in users[user_id][1]:
            data = 'not ' + data
        to_send = config.events[data]
        users[user_id][0] = data
        if 'command' in to_send:
            command = to_send['command'].split(' ')
            if 'add' in command:
                users[user_id][1] += command[1] + ' '
                database.update_user(user_id, users[user_id][0], users[user_id][1])
            elif 'fire' in command:
                if 'fire' not in users[user_id][1] and 'pitcher' in users[user_id][1]:
                    users[user_id][1] += 'fire '
                    send_mes(user_id, config.events['fire'], 'fire')
                    return
            elif 'end_of_game' in command:
                database.delete_user(user_id)

        send_mes(user_id, to_send, data)

    print(users[user_id])


if __name__ == "__main__":
    bot.polling(none_stop=True)
