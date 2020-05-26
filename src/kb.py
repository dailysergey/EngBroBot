# Keyboard after first /Start
from telebot import types
import botMessages
import telebot.types

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
keyboard4.row(botMessages.keyboard_test_row4)
keyboard4.row(botMessages.send_everybody)
keyboard4.row(botMessages.get_stats)


# Creates dynamic keyboard after sending user new eng word
def rateKeyboard(state=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if state == None:
        yesBtn = types.InlineKeyboardButton(
            text=botMessages.rate_default_one, callback_data='yes')
        noBtn = types.InlineKeyboardButton(
            text=botMessages.rate_default_two, callback_data='no')
        markup.add(yesBtn, noBtn)
    if state == True:
        markup.add(types.InlineKeyboardButton(
            text=botMessages.rate_yes, callback_data='yes'))
    elif state == False:
        markup.add(types.InlineKeyboardButton(
            text=botMessages.rate_no, callback_data='no'))

    return markup


def RuEnKeyboard():
    langKeyBoard = types.InlineKeyboardMarkup(row_width=2)
    btnRu = types.InlineKeyboardButton(text='🇷🇺', callback_data='Ru')
    btnEn = types.InlineKeyboardButton(text='🇺🇸', callback_data='En')
    langKeyBoard.add(btnRu, btnEn)
    return langKeyBoard
