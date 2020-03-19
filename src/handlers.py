from telebot import types
import botMessages
import wordAPI
import tgClient
import key
import telegram.ext


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
        bot.send_message(
            user_id, newWord, parse_mode=telegram.ParseMode.HTML, reply_markup=rateKeyboard())

        # update counter
        position += 1
        clients.update({'id': user_id}, {"$set": {'counter': position}},
                       upsert=True)


# Get info about users (for admins)
def getUsersInfo(user, message):
	userInfo = ""
	if user["id"] is not None:
		id = user["id"]
		userInfo += "User ID:{};".format(id)
	if user["first_name"] is not None:
		first_name = user["first_name"]
		userInfo += " First Name:{}; ".format(first_name)
	if user["send_notifies"] is not None:
		notify = user["send_notifies"]
		userInfo += " Send notifies:{}; ".format(notify)
	if message["new_words"] is not None:
		new_words = message["new_words"]
		userInfo += "New words:{};".format(new_words)
	if message["known_words"] is not None:
		known_words = message["known_words"]
		userInfo += " Known words:{}; ".format(known_words)
	if user["topic"] is not None:
		topic = user["topic"]
		userInfo += " Topic:{}; ".format(topic)
	if user["counter"] is not None:
		topic = user["counter"]
		userInfo += "Counter:{};".format(counter)
    return userInfo
