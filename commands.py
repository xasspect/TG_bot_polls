import text, pupils_list
from datetime import datetime, timedelta
from collections import defaultdict
from telebot import *

from pupils_list import Status

poll_closure_minutes = 90

def commands_register(bot):

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, text.greetings_message)

    @bot.message_handler(commands=['help'])
    def start(message):
        bot.send_message(message.chat.id, text.help_message)

    def close_poll_later(chat_id, message_id, delay_minutes):
        time.sleep(delay_minutes * 60)
        bot.stop_poll(chat_id, message_id)

    @bot.message_handler(commands=['make_poll'])
    def create_poll_command(message):
        try:
            date = datetime.now()
            poll_message = bot.send_poll(
                chat_id=message.chat.id,
                question=f"Придете ли вы {date.day}/{date.month}/{date.year}?",
                options=[
                    "Да",
                    "Нет",
                    "Свой вариант (проспал, заболел)"
                ],
                is_anonymous=False,
                allows_multiple_answers=False,
                type='regular'
            )
            bot.send_message(message.chat.id, "Опрос закрывается в течении полутора часов!")
            close_poll_later(message.chat.id, poll_message.id, 1)
        except Exception as e:
            bot.reply_to(message, f"Ошибка при создании опроса: {e}")

    poll_statistics = pupils_list.pupils

    @bot.poll_answer_handler()
    def handle_poll_answer(poll):
        poll_id = poll.poll_id
        user_id = poll.user.id
        selected_option = poll.option_ids[0]

        poll_statistics[f"{user_id}"][1] = pupils_list.Status(selected_option)
        print(f"Статистика опроса {poll_id}: {poll_statistics[f"{user_id}"][0]}, {pupils_list.Status(selected_option)}")
        print(poll_statistics)

    @bot.message_handler(commands=['stats'])
    def show_stats(message):
        if poll_statistics:
            last_poll_id = list(poll_statistics.keys())[-1]
            stats = poll_statistics[last_poll_id]
            response = "Статистика опроса:\n"
            for option_id, count in stats.items():
                response += f"Вариант {option_id}: {count} голосов\n"

            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Нет данных по опросам")