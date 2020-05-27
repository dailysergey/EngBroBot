from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
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
from telebot import types
import urllib
import quiz
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize
bot = telebot.TeleBot(key.API_skipper)

updater = Updater(key.API_skipper, use_context=True)


# Global Connect to MONGO
db = tgClient.MongoEntity().connect
clients = db['clients']
messages = db['message']
score = db['score']
topic = db['topic']
imageAI = detect.ImageObjects()


def start_message(update, context):
    try:
        message = update.message
        logging.info('start_message:From {}.Text:{}'.format(
            message.chat.id, message.text))
        # get user_id
        userId = message.from_user.id

        foundUser = clients.find({'id': userId})
        for fuser in foundUser:
            language_code = fuser['language_code']
        if foundUser.count() > 0:
            logging.info('start_message: Hello again block')
            keyBrd = kb.keyboard2 if fuser['send_notifies'] == 'true' else kb.keyboard1
            helloAgainMessage = botMessages.hello_again_ru if language_code == 'ru' else botMessages.hello_again_en
            bot.send_sticker(
                message.chat.id, botMessages.sticker_hello_again)
            bot.send_message(
                message.chat.id, helloAgainMessage, reply_markup=keyBrd)

        # else: save NEW user to my db and send congrats to join
        else:
            lc = message.from_user.language_code
            # save user
            user = message.from_user
            user['send_notifies'] = 'true'
            clients.insert_one(user)
            # form message from user
            textDict = {'message_id': message.message_id, 'user_id': userId,
                        'date': message.date, 'text': message.text}
            # store messages from user
            messages.insert_one(textDict)
            # send hello sticker
            bot.send_sticker(
                message.chat.id, botMessages.sticker_hello_text)
            helloMessage = botMessages.hello_text_ru if lc == 'ru' else botMessages.hello_text_en
            # send message hello
            bot.send_message(
                message.chat.id, helloMessage, reply_markup=kb.keyboard3)
    except Exception as ex:
        logging.error('[Error]: {}. From {}.Text:{}'.format(ex,
                                                            message.chat.id, message.text))


def help_message(update, context):
    message = update.message
    bot.send_sticker(
        message.chat.id, botMessages.sticker_help)
    bot.send_message(
        message.chat.id, "Выберите язык / Choose language", reply_markup=kb.RuEnKeyboard().to_json())


def stop_message(update, context):
    message = update.message
    userId = message.from_user.id
    clients.update({'id': userId}, {"$set": {'send_notifies': 'false'}},
                   upsert=True)
    # send message to say goodbye
    bot.send_sticker(
        message.chat.id, botMessages.sticker_notify_goodbye)
    bot.send_message(
        message.chat.id, botMessages.notify_goodbye, reply_markup=kb.keyboard1)


def send_media(update, context):
    try:
        currentDir = os.getcwd()
        message = update.message
        inputImage = bot.get_file(
            message.photo[len(message.photo)-1].file_id)
        # name of input image
        photoName = "{}.jpg".format(message.chat.id)
        destinationInputPhotoPath = os.path.join(
            currentDir, "objectDetection", "input", photoName)

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
def handle_query(update, context):
    try:
        call = update.callback_query
        data = call.data
        if 'yes' in data:
            messages.update_one(filter={"user_id": call.message.chat.id}, update={
                                '$push': {'known_words': call.message.text}}, upsert=True)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=call.message.text,
                                  message_id=call.message.message_id,
                                  parse_mode=telegram.ParseMode.HTML,
                                  reply_markup=kb.rateKeyboard(True).to_json()
                                  )

        if 'no' in data:
            messages.update_one(filter={"user_id": call.message.chat.id}, update={
                                '$push': {'new_words': call.message.text}}, upsert=True)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=call.message.text,
                                  message_id=call.message.message_id,
                                  parse_mode=telegram.ParseMode.HTML,
                                  reply_markup=kb.rateKeyboard(
                                      False).to_json()
                                  )
        if 'Ru' in data:
            bot.send_message(chat_id=call.message.chat.id,
                             text=botMessages.help_message_ru,
                             reply_markup=kb.keyboard2.to_json()
                             )
        if 'En' in data:
            bot.send_message(chat_id=call.message.chat.id,
                             text=botMessages.help_message_en,
                             reply_markup=kb.keyboard2.to_json()
                             )
        else:
            logging.info(
                "Get another message from inline mode: {}".format(data))
    except Exception as ex:
        logging.error('[Handle_query]: Error {}.'.format(ex))


def suggest_topic(update, context):
    try:
        message = update.message
        suggestedTopic = message.text.split(' ')
        value = {'id': message.from_user.id, 'topic': suggestedTopic[1]}
        topic.insert_one(value)
        bot.send_message(
            message.chat.id, 'Тема принята, спасибо! / Topic accepted, thanks!')
    except Exception as ex:
        lc = message.from_user.language_code
        logging.error(ex)
        messageError = botMessages.errorTopicRu if lc == 'ru' else botMessages.errorTopicEn
        bot.send_message(message.chat.id, messageError)


def send_text(update, context):
    api = wordAPI.engWord()
    message = update.message
    userId = message.from_user.id
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
    elif message.text == botMessages.keyboard_test_row4:
        poll = telegram.Poll(
            1, quiz.question1, options=quiz.variants1, total_voter_count=1, is_closed=False, correct_option_id=quiz.answer1, is_anonymous=True, allows_multiple_answers=False, type='quiz')
        bot.send_poll(userId, poll)
    else:
        # translate text
        api = wordAPI.engWord()

        translation = html.unescape(
            api.getTranslation(message.text))
        resultLang = api.ResultLang
        textToSpeech = message.text if resultLang == 'ru' else translation
        handlers.sendTextToSpeech(bot, textToSpeech, userId)
        bot.send_message(message.chat.id, translation)


# Get the dispatcher to register handlers
job = updater.job_queue


def callback_resender(context: telegram.ext.CallbackContext):
    hour = datetime.datetime.now().hour
    if hour > 10 and hour < 22:
        handlers.autoResendMessages(context.bot, clients)
    else:
        logging.info('Current time is {}'.format(datetime.datetime.now()))


def callback_reminder(context: telegram.ext.CallbackContext):
    handlers.autoReminder(context.bot, clients)


def error(update, context):
    logging.warning('update "%s" caused error "%s"', update, context.error)


job.run_repeating(
    callback_resender, interval=datetime.timedelta(hours=2), first=0)
# remind clients about myself
job.run_repeating(callback_reminder,
                  interval=datetime.timedelta(days=7), first=10800)
job.start()
# add handlers
updater = Updater(key.API_skipper, use_context=True)
dp = updater.dispatcher
try:
    dp = updater.dispatcher
    dp.add_handler(handler=CommandHandler("start", start_message))
    dp.add_handler(handler=CommandHandler("help", help_message))
    dp.add_handler(handler=CommandHandler("topic", suggest_topic))
    dp.add_handler(handler=CommandHandler("stop", stop_message))
    dp.add_handler(handler=MessageHandler(Filters.text, send_text))
    dp.add_handler(handler=MessageHandler(Filters.photo, send_media))
    dp.add_handler(handler=CallbackQueryHandler(handle_query))
    dp.add_error_handler(error)
    certssl = os.path.join(os.getcwd(), 'ssl', 'cert.pem')
    keyssl = os.path.join(os.getcwd(), 'ssl', 'private.key')
    updater.start_webhook(listen='0.0.0.0', port=key.hookPort,
                          url_path=key.API_skipper)
    updater.bot.set_webhook(url='https://{}/{}/'.format(key.HOST,
                                                        key.API_skipper), certificate=open(certssl, 'rb'))
    updater.idle()
except Exception as ex:
    logging.error('Entered error in the end on engbrobot.py: {}'.format(ex))
