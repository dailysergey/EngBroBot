from telegram.ext import Updater, CommandHandler
import logging.handlers
import logging
import wordAPI
import key
import json
from pprint import pprint
import tgClient
import botMessages
import time
import threading
import datetime
import html
import handlers
import kb
import telebot
import telegram.ext
from telegram.ext import Updater
# from telebot import apihelper
# import detect
import os

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize
bot = telebot.TeleBot(key.API_skipper)


# Global Connect to MONGO
db = tgClient.MongoEntity().connect
clients = db['clients']
messages = db['message']
score = db['score']
# imageAI = detect.ImageObjects()


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
                message.chat.id, botMessages.hello_again, reply_markup=kb.keyboard1)
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
                message.chat.id, botMessages.hello_text, reply_markup=kb.keyboard3)
    except Exception as ex:
        print(ex)
        logging.error('start_message:From {}.Text:{}'.format(
            message.chat.id, message.json['text']))


@bot.message_handler(commands=['help'])
def help_message(message):
    logging.info('help_message:From {}.Text:{}'.format(
        message.chat.id, message.json['text']))
    bot.send_sticker(
        message.chat.id, botMessages.sticker_help, reply_markup=kb.keyboard2)
    bot.send_message(
        message.chat.id, botMessages.help_message, reply_markup=kb.keyboard2)


@bot.message_handler(commands=['stop'])
def stop_message(message):
    # TODO create column in table isStopped
    pass


@bot.message_handler(content_types=['photo'])
def send_media(message):
    try:
    execution_path = os.getcwd()
    # filepath = "./user_data/" + name
        image = bot.get_file(message.photo[len(message.photo)-1].file_id)
        photoName = "{}.jpg".format(message.chat.id)
        #largest_photo = message.photo[-1].get_file()
    photo_path = os.path.join(
        execution_path, "src", "objectDetection", "input", photoName)

        downloaded_image = bot.download_file(image.file_path)
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_image)
        # largest_photo.download(photo_path)
        resultImage = imageAI.detect(photoName)
    print(resultImage)
    bot.send_photo(message.chat.id, photo=open(resultImage, "rb"))
    except Exception as ex:
        print(ex)
        logging.error('[Send media(photo)]: Error {}.'.format(ex))


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        if 'yes' in call.data:
            messages.update_one(filter={"user_id": call.message.chat.id}, update={
                                '$push': {'known_words': call.message.text}}, upsert=True)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=call.message.text,
                                  message_id=call.message.message_id,
                                  reply_markup=handlers.rateKeyboard(True),
                                  parse_mode='HTML')

        if 'no' in call.data:
            messages.update_one(filter={"user_id": call.message.chat.id}, update={
                                '$push': {'new_words': call.message.text}}, upsert=True)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=call.message.text,
                                  message_id=call.message.message_id,
                                  reply_markup=handlers.rateKeyboard(False),
                                  parse_mode='HTML')
    except Exception as ex:
        print(ex)
        logging.error('[Handle_query]: Error {}.'.format(ex))

#    bot.answer_callback_query(callback_query_id=call.id,
#                                show_alert=True,
#                                text="You Clicked {} ".format(call.data))


@bot.message_handler(content_types=['text'])
def send_text(message):
    # get user_id
    api = wordAPI.engWord()
    user_id = message.json['from']['id']
    if message.text == botMessages.keyboard_hello_row1:
        handlers.teachNewEnglishWord(api, user_id, bot, clients)
    elif message.text == botMessages.keyboard_enable_noty_row3:
        # how to ask questions
        clients.update({'id': user_id}, {"$set": {'send_notifies': 'true'}},
                       upsert=True)
        clients.update({'id': user_id}, {"$set": {'counter': 1}},
                       upsert=True)
        # send message to congrat
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify, reply_markup=kb.keyboard2)
        bot.send_message(
            message.chat.id, botMessages.notify_agreement, reply_markup=kb.keyboard3)

    elif message.text == botMessages.keyboard_disable_noty_row3:

        clients.update({'id': user_id}, {"$set": {'send_notifies': 'false'}},
                       upsert=True)
        # send message to say goodbye
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify_goodbye)
        bot.send_message(
            message.chat.id, botMessages.notify_goodbye, reply_markup=kb.keyboard1)
    elif message.text == botMessages.keyboard_current_topic:
        # TODO Check if input word exist in english
        bot.send_sticker(message.chat.id, botMessages.sticker_current_topic)
        bot.send_message(
            message.chat.id, botMessages.topic_reply, reply_markup=kb.keyboard3)
    # region TOPIC
    elif message.text in botMessages.topics:
        clients.update({'id': user_id}, {"$set": {'topic': message.text, 'counter': 1}},
                       upsert=True)
        if user_id == int(key.adminKey):
            bot.send_message(user_id, botMessages.success_set_topic +
                             message.text, reply_markup=kb.keyboard4)
        else:
            bot.send_message(user_id, botMessages.success_set_topic +
                             message.text, reply_markup=kb.keyboard2)
    elif user_id == int(key.adminKey) and message.text == botMessages.send_everybody:
        handlers.autoResendMessages(bot, clients)
    elif user_id == int(key.adminKey) and message.text == botMessages.get_stats:
        for user in clients.find():
            for sms_stat in messages.find(filter={"user_id": user["id"]}):
                userInfo = handlers.getUsersInfo(user, sms_stat)
                bot.send_message(user_id, userInfo)

    else:
        # TODO translate text
        api = wordAPI.engWord()
        translation = html.unescape(api.getTranslation(message.json["text"]))
        bot.send_message(message.chat.id, translation)


# def callback_alarm(bot, job):
#     bot.send_message(chat_id=job.context, text='Wait for another 10 Seconds')


# def callback_timer(bot, update, job_queue):
#     bot.send_message(chat_id=update.message.chat_id,
#                      text='Wait for 10 seconds')
#     job_queue.run_repeating(callback_minute, 10,
#                             context=update.message.chat_id)
def callback_timer(bot, update, job_queue):
    bot.send_message(chat_id='161408126',
                     text='Wait for 10 seconds')
    job_queue.run_repeating(callback_minute, 10,
                            context='161408126')


def callback_minute(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='161408126',
                             text='A single message with 30s delay')
    # api = wordAPI.engWord()
    # for x in clients.find(filter={'send_notifies': 'true'}):
    #     user_id = x["id"]
    #     if user_id == int(key.adminKey):
    #         continue
    #     handlers.teachNewEnglishWord(api, user_id, context.bot, clients)


updater = Updater(key.API_skipper, use_context=True)
updater.dispatcher.add_handler(CommandHandler(
    'start', callback_timer, pass_job_queue=True))


# def Stop_timer(bot, update, job_queue):
#     bot.send_message(chat_id=update.message.chat_id,
#                       text='Soped!')
#     job_queue.stop()

# updater = Updater("YOUR_TOKEN")
# updater.dispatcher.add_handler(CommandHandler('start', callback_timer, pass_job_queue=True))
# updater.dispatcher.add_handler(CommandHandler('stop', Stop_timer, pass_job_queue=True))

# updater.start_polling()


bot.polling()
