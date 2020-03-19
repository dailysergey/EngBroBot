# Keyboard after first /Start
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
keyboard4.row(botMessages.send_everybody)
keyboard4.row(botMessages.get_stats)
