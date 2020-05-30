import quiz
import botMessages
import wordAPI
import tgClient
import key
import kb
import telegram.ext
from gtts import gTTS
import os
from telebot import types
import json
import threading
import logging
import re
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def autoResendMessages(bot, clients):
    try:
        api = wordAPI.engWord()
        for client in clients.find(filter={'send_notifies': 'true'}):
            userId = client["id"]
            task = threading.Thread(
                target=teachNewEnglishWord, args=(api, userId, bot, clients))
            task.start()
    except Exception as ex:
        logging.error(ex)


def autoReminder(bot, clients):
    try:
        for client in clients.find(filter={'send_notifies': 'false'}):
            messageReminder = botMessages.reminder_ru if client[
                'language_code'] == 'ru' else botMessages.reminder_en
            bot.send_message(client['id'], messageReminder,
                             reply_markup=kb.keyboard1)
    except Exception as ex:
        logging.error(ex)

def autoQuizSender(bot, clients):
    try:
        for client in clients.find(filter={'send_notifies': 'true'}):
            userId = client["id"]
            task = threading.Thread(
                target=sendQuizPoll, args=(userId, bot))
            task.start()
    except Exception as ex:
        logging.error(ex)

def sendQuizPoll(userId, bot):
    quizQuestion = quiz.getAnotherQuiz()
    bot.send_poll(userId, question=quizQuestion[0], options=quizQuestion[1],
                              type='quiz', correct_option_id=quizQuestion[2], is_closed=False)
# Forming message for user

def teachNewEnglishWord(api, user_id, bot, clients):
    for user in clients.find(filter={'id': user_id}):
        topic = user['topic']
        position = user['counter']
        transcription, nextWord = api.getWordOnTopic(topic, position)
        if nextWord is None:
            return

        translation = api.getTranslation(nextWord)

        synonyms = api.getSynonym(nextWord, position)

        logging.info('Synonyms:{}'.format(synonyms))
        newWord = '{} - {} - {}'.format(nextWord, transcription, translation) if synonyms is None else '{} - {} - {}\nSynonyms: {}'.format(
            nextWord, transcription, translation, ', '.join(synonyms))
        #keyBoard = kb.rateKeyboard()
        try:
            bot.send_message(
                user_id, newWord, parse_mode=telegram.ParseMode.HTML, reply_markup=kb.rateKeyboard().to_json())
        except Exception as ex:
            logging.error(ex)
            bot.send_message(
                user_id, newWord, parse_mode=telegram.ParseMode.HTML)
        sendTextToSpeech(bot, nextWord, user_id)
        # update counter
        position += 1
        clients.update({'id': user_id}, {"$set": {'counter': position}},
                       upsert=True)


def sendTextToSpeech(bot, word, user_id):
    text = (re.split(r"(\b[\w']+\b)(?:.+|$)", word)[1])
    logging.info('text:{}'.format(text))
    outputFile = "{}.mp3".format(text)
    textToSpeech(word, outputFile)
    bot.send_audio(user_id, audio=open(outputFile, "rb"))
    os.remove(outputFile)


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
