import logging.handlers
import logging
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
score = db['score']

# Keyboard after first /Start
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard1.row('🇬🇧Give New English word🇬🇧')
keyboard1.row('⏰Set daily notifies⏰')


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        # message.json["from"] - info about user from whom message
        # message.json["text"] - actual text from user
        glogger.info('start_message:From {}.Text:{}'.format(
            message.chat.id, message.json['text']))
        # get user_id
        user_id = message.json['from']['id']
        # check if user already send me 'START' message
        if clients.find({'id': user_id}).count() > 0:
            glogger.info('start_message: Hello again block')

            bot.send_sticker(
                message.chat.id, botMessages.sticker_hello_again)
            bot.send_message(
                message.chat.id, botMessages.hello_again, reply_markup=keyboard1)
        # else: save user to my db and send congrats to join
        else:
            # save user
            clients.insert_one(message.json['from'])
            # form message from user
            text_dict = {'message_id': message.json['message_id'], 'user_id': user_id,
                         'date': message.json['date'], 'text': message.json['text']}
            # store messages from user
            messages.insert_one(text_dict)
            # send hello sticker
            bot.send_sticker(
                message.chat.id, botMessages.sticker_hello_text)
            # send message hello
            bot.send_message(
                message.chat.id, botMessages.hello_text, reply_markup=keyboard1)
    except Exception as ex:
        print(ex)

# TODO create func with norm deserialize from tg_object
# TODO check if generated word is translatable
# TODO if user send more then 10 the same messages
# TODO TurnOn and turn off notification | set from and to TimeStamp |
#
# add field in user for TASK TO SEND NOTIFIES


def checkSpamAndFlood(user_id):

    return


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'word' or message.text == '🇬🇧Give New English word🇬🇧':
        generateEngWord(message)
    if message.text == '⏰Set daily notifies⏰':
        # while No CancelationToken
        # Ask time from to
        pass
# Refactored func with one transaction of word

# TODO hide to wordApi.py


def generateEngWord(message):
    api = wordAPI.engWord()
    resultEngWord = api.getRandomWord()
    data = json.loads(resultEngWord)

    engWord = data['word']
    # TODO Add here api for transcription generated english word
    translation = api.getTranslation(engWord)

    bot.send_message(message.chat.id, engWord)
    bot.send_message(message.chat.id, translation)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


bot.polling()
