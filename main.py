import telebot
import deps
from commands import *

bot = telebot.TeleBot(deps.TOKEN)
commands_register(bot)

@bot.message_handler(content_types=["text"])
def check_id(message):
    bot.send_message(message.chat.id, message)

if __name__ == '__main__':
    bot.infinity_polling()