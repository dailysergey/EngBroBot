import telebot
import wordAPI
import key
import json
from pprint import pprint
import tgClient
import botMessages

# region Use syslog to log from python
import syslog
syslog.openlog("TgEngBot")
syslog.syslog(syslog.LOG_ALERT, 'Start logging USING SYSLog')
# endregion

# region Attempt to use logging pkg
# Logging
glogger = logging.getLogger('tg_logger')
glogger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
glogger.addHandler(handler)
# endregion

# Initialize
bot = telebot.TeleBot(key.API_skipper)
# Global Connect to MONGO
db = tgClient.MongoEntity().connect
clients = db['clients']
messages = db['message']

# Keyboard after first /Start
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard1.row('🇬🇧Give New English word🇬🇧')
keyboard1.row('⏰Set daily notifies⏰')

# -1. Добавить логирование

# 3. Отправлять пользователю уведомления на экран


@bot.message_handler(commands=['start'])
def start_message(message):
    # message.json["from"] - info about user from whom message
    # message.json["text"] - actual text from user
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
# TODO if user send more then 10 the same messages


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'word' or message.text == 'Давай New English word':
        generateEngWord(message)

# Refactored func with one transaction of word


def generateEngWord(message):
    api = wordAPI.engWord()
    resultEngWord = api.getRandomWord()
    data = json.loads(resultEngWord)

    engWord = data['word']
    # TODO Add here api for generated english word
    translation = api.getTranslation(engWord)

    bot.send_message(message.chat.id, engWord)
    bot.send_message(message.chat.id, translation)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


bot.polling()
