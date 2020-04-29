from telebot import types
import botMessages
import wordAPI
import tgClient
import key
import telegram.ext
from gtts import gTTS
import os

# TODO find all users where send_notifies=true and send on timer messages


def autoResendMessages(bot, clients):
    api = wordAPI.engWord()
    for x in clients.find(filter={'send_notifies': 'true'}):
        user_id = x["id"]
        if user_id == int(key.adminKey):
            continue
        teachNewEnglishWord(api, user_id, bot, clients)


# Creates dynamic keyboard after sending user new eng word
def rateKeyboard(state=None):
    markup = types.InlineKeyboardMarkup()
    if state == None:
        markup.add(types.InlineKeyboardButton(text=botMessages.rate_default_one, callback_data='yes'),
                   types.InlineKeyboardButton(text=botMessages.rate_default_two, callback_data='no'))
    if state == True:
        markup.add(types.InlineKeyboardButton(
            text=botMessages.rateYes, callback_data='yes'))
    elif state == False:
        markup.add(types.InlineKeyboardButton(
            text=botMessages.rateNo, callback_data='no'))
    return markup


# Forming message for user
def teachNewEnglishWord(api, user_id, bot, clients):
    for user in clients.find(filter={'id': user_id}):
        topic = user['topic']
        position = user['counter']
        transcription, nextWord = api.getWordOnTopic(topic, position)
        if nextWord is None:
            return

        translation = api.getTranslation(nextWord)
        newWord = '<b>{}</b> - {} - <b>{}</b>'.format(nextWord,
                                                      transcription, translation)
        reply_markup = rateKeyboard()
        bot.send_message(
            user_id, newWord, parse_mode=telegram.ParseMode.HTML, reply_markup=reply_markup)
        sendTextToSpeech(bot, nextWord, user_id)

        # update counter
        position += 1
        reply_markup = None
        clients.update({'id': user_id}, {"$set": {'counter': position}},
                       upsert=True)


def sendTextToSpeech(bot, word, user_id):
    out_file = "{}.mp3".format(word)
    textToSpeech(word, out_file)
    bot.send_audio(user_id, audio=open(out_file, "rb"))
    os.remove(out_file)


def textToSpeech(word, out_file):
    tts = gTTS(word, lang="en")
    tts.save(out_file)

# Get info about users (for admins)


def getUsersInfo(user, message):
    userInfo = ""
    if "id" in user:
        id = user["id"]
        userInfo += "User ID:{};".format(id)
    if "first_name" in user:
        first_name = user["first_name"]
        userInfo += " First Name:{}; ".format(first_name)
    if "send_notifies" in user:
        notify = user["send_notifies"]
        userInfo += " Send notifies:{}; ".format(notify)
    if "new_words" in message:
        new_words = message["new_words"]
        userInfo += "New words:{};".format(new_words)
    if "known_words" in message:
        known_words = message["known_words"]
        userInfo += " Known words:{}; ".format(known_words)
    if "topic" in user:
        topic = user["topic"]
        userInfo += " Topic:{}; ".format(topic)
    if "counter" in user:
        counter = user["counter"]
        userInfo += "Counter:{};".format(counter)
    return userInfo
