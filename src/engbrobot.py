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
import detect
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
imageAI = detect.ImageObjects()


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        # message.json["from"] - info about user from whom message
        # message.json["text"] - actual text from user
        logging.info('start_message:From {}.Text:{}'.format(
            message.chat.id, message.json['text']))
        # get user_id
        userId = message.json['from']['id']
        # check if user already send me 'START' message
        if clients.find({'id': userId}).count() > 0:
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
            text_dict = {'message_id': message.json['message_id'], 'user_id': userId,
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
        logging.error('[Error]: {}. From {}.Text:{}'.format(ex,
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
    userId = message.json['from']['id']
    clients.update({'id': userId}, {"$set": {'send_notifies': 'false'}},
                   upsert=True)
    # send message to say goodbye
    bot.send_sticker(
        message.chat.id, botMessages.sticker_notify_goodbye)
    bot.send_message(
        message.chat.id, botMessages.notify_goodbye, reply_markup=kb.keyboard1)


@bot.message_handler(content_types=['photo'])
def send_media(message):
    try:
        currentDir = os.getcwd()
        inputImage = bot.get_file(message.photo[len(message.photo)-1].file_id)
        # name of input image
        photoName = "{}.jpg".format(message.chat.id)
        destinationInputPhotoPath = os.path.join(
            currentDir, "src", "objectDetection", "input", photoName)

        downloadedImage = bot.download_file(inputImage.file_path)

        with open(destinationInputPhotoPath, 'wb') as new_file:
            new_file.write(downloadedImage)

        logging.info('Saved photo to {}'.format(destinationInputPhotoPath))
        resultImage = imageAI.detect(photoName)
        logging.info('Sending photo to {} with photo from {}'.format(
            message.chat.id, resultImage))
        bot.send_photo(message.chat.id, photo=open(resultImage, "rb"))
    except Exception as ex:
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
                                  parse_mode=telegram.ParseMode.HTML,
                                  reply_markup=kb.rateKeyboard(True).to_json()
                                  )

        if 'no' in call.data:
            messages.update_one(filter={"user_id": call.message.chat.id}, update={
                                '$push': {'new_words': call.message.text}}, upsert=True)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=call.message.text,
                                  message_id=call.message.message_id,
                                  parse_mode=telegram.ParseMode.HTML,
                                  reply_markup=kb.rateKeyboard(
                                      False).to_json()
                                  )
        else:
            logging.info(
                "Get another message from inline mode: {}".format(call.data))
    except Exception as ex:
        print(ex)
        logging.error('[Handle_query]: Error {}.'.format(ex))


@bot.message_handler(content_types=['text'])
def send_text(message):
    api = wordAPI.engWord()
    userId = message.json['from']['id']
    if message.text == botMessages.keyboard_hello_row1:
        handlers.teachNewEnglishWord(api, userId, bot, clients)

    elif message.text == botMessages.keyboard_enable_noty_row3:
        # how to ask questions
        clients.update({'id': userId}, {"$set": {'send_notifies': 'true'}},
                       upsert=True)
        clients.update({'id': userId}, {"$set": {'counter': 1}},
                       upsert=True)
        # send message to congrat
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify, reply_markup=kb.keyboard2)
        bot.send_message(
            message.chat.id, botMessages.notify_agreement, reply_markup=kb.keyboard3)

    elif message.text == botMessages.keyboard_disable_noty_row3:

        clients.update({'id': userId}, {"$set": {'send_notifies': 'false'}},
                       upsert=True)
        # send message to say goodbye
        bot.send_sticker(
            message.chat.id, botMessages.sticker_notify_goodbye)
        bot.send_message(
            message.chat.id, botMessages.notify_goodbye, reply_markup=kb.keyboard1)

    elif message.text == botMessages.keyboard_current_topic:
        bot.send_sticker(message.chat.id, botMessages.sticker_current_topic)
        bot.send_message(
            message.chat.id, botMessages.topic_reply, reply_markup=kb.keyboard3)

    # region TOPIC
    elif message.text in botMessages.topics:
        clients.update({'id': userId}, {"$set": {'topic': message.text, 'counter': 1}},
                       upsert=True)
        if userId == int(key.adminKey):
            bot.send_message(userId, botMessages.success_set_topic +
                             message.text, reply_markup=kb.keyboard4)
        else:
            bot.send_message(userId, botMessages.success_set_topic +
                             message.text, reply_markup=kb.keyboard2)

    elif userId == int(key.adminKey) and message.text == botMessages.send_everybody:
        handlers.autoResendMessages(bot, clients)

    elif userId == int(key.adminKey) and message.text == botMessages.get_stats:
        for user in clients.find():
            for sms_stat in messages.find(filter={"user_id": user["id"]}):
                userInfo = handlers.getUsersInfo(user, sms_stat)
                bot.send_message(userId, userInfo)

    else:
        # translate text
        api = wordAPI.engWord()
        translation = html.unescape(api.getTranslation(message.json["text"]))
        bot.send_message(message.chat.id, translation)


updater = Updater(key.API_skipper, use_context=True)
# Get the dispatcher to register handlers
job = updater.job_queue


def callback_resender(context: telegram.ext.CallbackContext):
    hour = datetime.datetime.now().hour
    if hour < 20 and hour > 10:
        handlers.autoResendMessages(context.bot, clients)


job.run_repeating(
    callback_resender, interval=datetime.timedelta(hours=2), first=0)
job.start()
bot.infinity_polling()
