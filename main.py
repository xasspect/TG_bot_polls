import telebot
import deps
from commands import *

bot = telebot.TeleBot(deps.TOKEN)
commands_register(bot)

if __name__ == '__main__':
    bot.infinity_polling()