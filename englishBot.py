import telebot
import wordAPI
import key
import json
from pprint import pprint
import tgClient
# Initialize
bot = telebot.TeleBot(key.API_skipper)

keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard1.row('Давай New English word')


# -1. Добавить логирование
# 0. Обрамить try catch
# 1. Найти API для получения английского слова - done
# 2. Выдавать новое слово по запросу пользователя
# 3. Отправлять пользователю уведомления на экран
# 4. Хранить chat_id
# 5. Если уже пользователь вводил /start, говорить ему об этом


@bot.message_handler(commands=['start'])
def start_message(message):
    # TODO Start store history with user here to mongo
    # message.json["from"] - info about user from whom message
    # message.json["text"] - actual text from user
    db = tgClient.MongoEntity().connect
    clients = db['clients']
    messages = db['message']
    user_id = message.json['from']['id']

    if clients.find({'id': user_id}).count() > 0:
        bot.send_message(
            message.chat.id, 'Дорогой, ты уже это мне писал ', reply_markup=keyboard1)
    else:
        clients.insert_one(message.json['from'])
        text_dict = {'message_id': message.json['message_id'], 'user_id': user_id,
                     'date': message.json['date'], 'text': message.json['text']}
        messages.insert_one(text_dict)
        bot.send_message(
            message.chat.id, 'Привет, ты написал мне /start', reply_markup=keyboard1)
# TODO create func with norm deserialize from tg_object


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'word':
        generateEngWord(message)

# Refactored func with one transaction of word


def generateEngWord(message):
    api = wordAPI.engWord()
    resultEngWord = api.getRandomWord()
    data = json.loads(resultEngWord)

    engWord = data['word']
    translation = api.getTranslation(engWord)

    bot.send_message(message.chat.id, engWord)
    bot.send_message(message.chat.id, translation)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


bot.polling()
