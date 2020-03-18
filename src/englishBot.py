import logging.handlers
import logging
import telebot
import wordAPI
import key
import json
from pprint import pprint
import tgClient
import botMessages
import time
import threading
import telegram.ext
from telegram.ext import Updater
import datetime
import html
from telebot import types

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize
bot = telebot.TeleBot(key.API_skipper)
updater = Updater(key.API_skipper, use_context=True)
job = updater.job_queue

# Global Connect to MONGO
db = tgClient.MongoEntity().connect
clients = db['clients']
messages = db['message']
score = db['score']

# Keyboard after first /Start
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard1.row(botMessages.keyboard_hello_row1)
keyboard1.row(botMessages.keyboard_enable_noty_row3)

keyboard2 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard2.row(botMessages.keyboard_hello_row1)
keyboard2.row(botMessages.keyboard_current_topic)
keyboard2.row(botMessages.keyboard_disable_noty_row3)

keyboard3 = telebot.types.ReplyKeyboardMarkup(row_width=2)
keyboard3.row(botMessages.topic_art, botMessages.topic_developer)
keyboard3.row(botMessages.topic_education, botMessages.topic_economy)
keyboard3.row(botMessages.topic_nature, botMessages.topic_politics)
keyboard3.row(botMessages.topic_sport, botMessages.topic_science)

keyboard4 = telebot.types.ReplyKeyboardMarkup(row_width=1)
keyboard4.row(botMessages.keyboard_hello_row1)
keyboard4.row(botMessages.keyboard_current_topic)
keyboard4.row(botMessages.keyboard_disable_noty_row3)
keyboard4.row(botMessages.send_everybody)
keyboard4.row(botMessages.get_stats)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        # message.json["from"] - info about user from whom message
        # message.json["text"] - actual text from user
        logging.info('start_message:From {}.Text:{}'.format(
            message.chat.id, message.json['text']))
        # get user_id
        user_id = message.json['from']['id']
        # check if user already send me 'START' message
        if clients.find({'id': user_id}).count() > 0:
            logging.info('start_message: Hello again block')

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
                message.chat.id, botMessages.hello_text, reply_markup=keyboard3)
    except Exception as ex:
        print(ex)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_sticker(
        message.chat.id, botMessages.sticker_help, reply_markup=keyboard2)
    bot.send_message(
        message.chat.id, botMessages.help_message, reply_markup=keyboard2)


@bot.message_handler(commands=['stop'])
def stop_message(message):
    # TODO create column in table isStopped
    pass

# TODO find all users where send_notifies=true and send on timer messages


def autoResendMessages():
    api = wordAPI.engWord()
    for x in clients.find(filter={'send_notifies': 'true'}):
        user_id = x["id"]
        if user_id == int(key.adminKey):
            continue
        teachNewEnglishWord(api, user_id)


@bot.message_handler(content_types=['photo'])
def send_media(message):
    print(message)
    bot.send_photo(message.chat.id,
                   message.photo[len(message.photo)-1].file_id)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == '👍':
        messages.update_one(filter={"user_id": call.message.chat.id}, update={
                            '$push': {'new_words': call.message.text}}, upsert=True)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=call.message.text,
                              message_id=call.message.message_id,
                              reply_markup=rateKeyboard(True),
                              parse_mode='HTML')

    if call.data == '👎':
        messages.update_one(filter={"user_id": call.message.chat.id}, update={
                            '$push': {'known_words': call.message.text}}, upsert=True)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=call.message.text,
                              message_id=call.message.message_id,
                              reply_markup=rateKeyboard(False),
                              parse_mode='HTML')

#    bot.answer_callback_query(callback_query_id=call.id,
#                                show_alert=True,
#                                text="You Clicked {} ".format(call.data))


@bot.message_handler(content_types=['text'])
def send_text(message):
    # get user_id
    api = wordAPI.engWord()
    user_id = message.json['from']['id']
    if message.text == botMessages.keyboard_hello_row1:
        teachNewEnglishWord(api, user_id)
    elif message.text == botMessages.keyboard_enable_noty_row3:
        # how to ask questions
        clients.update({'id': user_id}, {"$set": {'send_notifies': 'true'}},
                       upsert=True)
        clients.update({'id': user_id}, {"$set": {'counter': 1}},
                       upsert=True)
        # send message to congrat
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify, reply_markup=keyboard2)
        bot.send_message(
            message.chat.id, botMessages.notify_agreement, reply_markup=keyboard3)

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
        bot.send_message(
            message.chat.id, botMessages.topic_reply, reply_markup=keyboard3)
    # region TOPIC
    elif message.text in botMessages.topics:
        clients.update({'id': user_id}, {"$set": {'topic': message.text, 'counter': 1}},
                       upsert=True)
        if user_id == int(key.adminKey):
            bot.send_message(user_id, botMessages.success_set_topic +
                             message.text, reply_markup=keyboard4)

        else:
            bot.send_message(user_id, botMessages.success_set_topic +
                             message.text, reply_markup=keyboard2)
    elif user_id == int(key.adminKey) and message.text == botMessages.send_everybody:
        autoResendMessages()
    elif user_id == int(key.adminKey) and message.text == botMessages.get_stats:
        for x in clients.find(filter={'send_notifies': 'true'}):
            userInfo = 'user_id:{};Name:{}'.format(x["id"], x["first_name"])

    else:
        # TODO translate text
        api = wordAPI.engWord()
        translation = html.unescape(api.getTranslation(message.json["text"]))
        bot.send_message(message.chat.id, translation)
        # Refactored func with one transaction of word


def getUsersInfo(user_id):
    clients


def rateKeyboard(state=None):
    markup = types.InlineKeyboardMarkup()
    if state == None:
        markup.add(types.InlineKeyboardButton(text='👍', callback_data='👍'),
                   types.InlineKeyboardButton(text='👎', callback_data='👎'))
    if state == True:
        markup.add(types.InlineKeyboardButton(
            text='❤️Your answer is very important for us❤️', callback_data='👍'))
    elif state == False:
        markup.add(types.InlineKeyboardButton(
            text='❤️Every day we get better with your help❤️', callback_data='👍'))
    return markup


def teachNewEnglishWord(api, user_id):
    for user in clients.find(filter={'id': user_id}):
        topic = user['topic']
        position = user['counter']
        transcription, nextWord = api.getWordOnTopic(topic, position)
        if nextWord is None:
            return

        translation = api.getTranslation(nextWord)
        newWord = '<b>{}</b> - {} - <b>{}</b>'.format(nextWord,
                                                      transcription, translation)
        bot.send_message(
            user_id, newWord, parse_mode=telegram.ParseMode.HTML, reply_markup=rateKeyboard())

        # update counter
        position += 1
        clients.update({'id': user_id}, {"$set": {'counter': position}},
                       upsert=True)


def generateEngWord(id):
    api = wordAPI.engWord()
    resultEngWord = api.getRandomWord()
    engWord, pronounce = resultEngWord

    bot.send_message(id, engWord)
    if pronounce is not None:
        bot.send_message(id, "[ "+pronounce+" ]")
    translation = api.getTranslation(engWord)
    bot.send_message(id, translation)


job.run_daily(autoResendMessages, datetime.time(8, 0, 0))
job.run_daily(autoResendMessages, datetime.time(11, 0, 0))
job.run_daily(autoResendMessages, datetime.time(10, 50, 0))
job.run_daily(autoResendMessages, datetime.time(12, 0, 0))
job.run_daily(autoResendMessages, datetime.time(16, 0, 0))
job.run_daily(autoResendMessages, datetime.time(20, 0, 0))

bot.polling()
