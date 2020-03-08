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

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
keyboard1.row('⏰Enable daily notifies⏰')

keyboard2 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard2.row('🇬🇧Give New English word🇬🇧')
keyboard2.row('⏰Disable daily notifies⏰')


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
            user = message.json['from']
            user['send_notifies'] = 'false'
            clients.insert_one(user)
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

# TODO find all users where send_notifies=true and send on timer messages


def AutoResendMessages():
    for x in clients.find(filter={'send_notifies': 'true'}):
        generateEngWord(x["id"])


@bot.message_handler(content_types=['text'])
def send_text(message):
    # get user_id
    user_id = message.json['from']['id']
    if message.text == botMessages.keyboard_hello_row1 or message.text == botMessages.keyboard_hello_row1:
        generateEngWord(message.chat.id)
    elif message.text == botMessages.keyboard_enable_noty_row3:
        # how to ask questions
        clients.update({'id': user_id}, {"$set": {'send_notifies': 'true'}},
                       upsert=True)
        # send message to congrat
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify, reply_markup=keyboard2)
        bot.send_message(
            message.chat.id, botMessages.notify_agreement, reply_markup=keyboard2)

    elif message.text == botMessages.keyboard_disable_noty_row3:

        clients.update({'id': user_id}, {"$set": {'send_notifies': 'false'}},
                       upsert=True)
        # send message to say goodbye
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify_goodbye)
        bot.send_message(
            message.chat.id, botMessages.notify_goodbye, reply_markup=keyboard1)
    elif message.text == botMessages.keyboard_current_topic:
        # TODO Check if input word exist in english

        bot.send_sticker(message.chat.id, botMessages.sticker_current_topic)

    else:
        # TODO translate text
        api = wordAPI.engWord()
        translation = api.getTranslation(message.json["text"])
        #translation = translator.translate(message.json["text"])
        translation = html.unescape(translation)
        bot.send_message(message.chat.id, translation)
        # Refactored func with one transaction of word`


def generateEngWord(id):
    api = wordAPI.engWord()
    resultEngWord = api.getRandomWord()
    engWord, pronounce = resultEngWord

    bot.send_message(id, engWord)
    if pronounce is not None:
        bot.send_message(id, "[ "+pronounce+" ]")
    translation = api.getTranslation(engWord)
    bot.send_message(id, translation)


@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


job.run_daily(AutoResendMessages, datetime.time(8, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(11, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(10, 50, 0))
job.run_daily(AutoResendMessages, datetime.time(12, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(16, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(20, 0, 0))

bot.polling()
