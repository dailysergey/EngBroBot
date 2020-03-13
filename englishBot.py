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
import schedule
import telegram.ext
from telegram.ext import Updater
import datetime
import html


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
# currentTopic
currentTopic = ''
Topic = botMessages.keyboard_current_topic + ' {}'.format(currentTopic)

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
                message.chat.id, botMessages.hello_text, reply_markup=keyboard1)
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


def AutoResendMessages():
    api = wordAPI.engWord()
    for x in clients.find(filter={'send_notifies': 'true'}):
        position = x["counter"]
        topic = x["topic"]
        generateEngWord(x["id"])
        api.getWordOnTopic(topic, position)
        position += 1
        clients.update({'id': x["id"]}, {"$set": {'counter': position}},
                       upsert=True)


@bot.message_handler(content_types=['text'])
def send_text(message):
    # get user_id
    api = wordAPI.engWord()
    user_id = message.json['from']['id']
    if message.text == botMessages.keyboard_hello_row1:
        for user in clients.find(filter={'id': user_id}):
            topic = user['topic']
            position = user['counter']
            nextWord = api.getWordOnTopic(topic, position)
        translation = api.getTranslation(nextWord)
        bot.send_message(user_id, nextWord)
        bot.send_message(user_id, translation)
            # update counter
            position += 1
            clients.update({'id': user_id}, {"$set": {'counter': position}},
                           upsert=True)

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
        # TODO instant dialog with user
        bot.send_message(
            message.chat.id, botMessages.topic_reply, reply_markup=keyboard3)
    # region TOPIC
    elif message.text == botMessages.topic_art:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_art}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_art, reply_markup=keyboard2)
    elif message.text == botMessages.topic_developer:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_developer}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_developer, reply_markup=keyboard2)
    elif message.text == botMessages.topic_education:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_education}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_education, reply_markup=keyboard2)
    elif message.text == botMessages.topic_economy:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_economy}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_economy, reply_markup=keyboard2)
    elif message.text == botMessages.topic_nature:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_nature}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_nature, reply_markup=keyboard2)
    elif message.text == botMessages.topic_politics:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_politics}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_politics, reply_markup=keyboard2)
    elif message.text == botMessages.topic_sport:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_sport}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_sport, reply_markup=keyboard2)
    elif message.text == botMessages.topic_science:
        clients.update({'id': user_id}, {"$set": {'topic': botMessages.topic_science}},
                       upsert=True)
        bot.send_message(user_id, botMessages.success_set_topic +
                         botMessages.topic_science, reply_markup=keyboard2)
    # endregion
    else:
        # TODO translate text
        api = wordAPI.engWord()
        translation = html.unescape(api.getTranslation(message.json["text"]))
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


job.run_daily(AutoResendMessages, datetime.time(8, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(11, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(10, 50, 0))
job.run_daily(AutoResendMessages, datetime.time(12, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(16, 0, 0))
job.run_daily(AutoResendMessages, datetime.time(20, 0, 0))

bot.polling()
