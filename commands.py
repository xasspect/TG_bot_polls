import deps
import text, pupils_list
from telebot import *

from pupils_list import Status

poll_closure_minutes = 1
admin_to_send_to = deps.admins['oleja']

trusted = u'\u2705'
not_trusted = u'\u274C'

def commands_register(bot):

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, text.greetings_message)

    @bot.message_handler(commands=['get_chat_id'])
    def get_chat_id(message):
        bot.send_message(message.chat.id, message.chat.id)

    def get_id(name):
        try:
            name = ' '.join(name.split()[1:])
            return pupils_list.pupils_by_name[name]
        except Exception as e:
            print(f'хуйня какая-то {e}')

    @bot.message_handler(commands=['entrust'])
    def entrust_user(message):
        if not check_rights(message):
            bot.reply_to(message.chat.id, 'Недостаточно прав')
            return 0
        pupils_list.pupils[get_id(message.text)][2] = Status.TRUSTED
        bot.reply_to(message, f"{message.text} entrusted!")

    @bot.message_handler(commands=['distrust'])
    def entrust_user(message):
        if not check_rights(message):
            bot.reply_to(message.chat.id, 'Недостаточно прав')
            return 0
        pupils_list.pupils[get_id(message.text)][2] = Status.NOT_TRUSTED
        bot.reply_to(message, f"{message.text} not trusted anymore!")

    @bot.message_handler(commands=['get_trust_levels'])
    def get_trust_levels(message):
        if not check_rights(message): return 0
        trusted = [pupils_list.pupils[pupil][0] for pupil in pupils_list.pupils.keys() if
                   pupils_list.pupils[pupil][2] == Status.TRUSTED]
        not_trusted = [pupils_list.pupils[pupil][0] for pupil in pupils_list.pupils.keys() if
                       pupils_list.pupils[pupil][2] == Status.NOT_TRUSTED]
        response = ""
        for list, name in [[trusted, "Trusted:"], [not_trusted, "Not Trusted:"]]:
            response += name + '\n'
            for pupil in list:
                response += '- ' + pupil + "\n"
            response += "\n"
        bot.send_message(message.chat.id, "Отправил!")
        bot.send_message(admin_to_send_to, response)

    def get_id_distrusted():
        response = ""
        for pupil in pupils_list.pupils:
            if pupils_list.pupils[pupil][2] == Status.NOT_TRUSTED:
                response += pupils_list.pupils[pupil][0] + ": " + "NOT_TRUSTED" + "\n"
        if response == "": response = "No distrusteed!"
        return response

    @bot.message_handler(commands=['help'])
    def start(message):
        bot.send_message(message.chat.id, text.help_message)

    def check_rights(message):
        print(message.from_user.id)
        if message.from_user.id in deps.admins.values():
            return True
        else:
            bot.reply_to(message, 'Недостаточно прав')
            return False

    def close_poll_later(chat_id, message_id, delay_minutes):
        time.sleep(delay_minutes * 60)
        bot.stop_poll(chat_id, message_id)
        show_stats()

    def get_username_by_id(user_id):
        try:
            chat = bot.get_chat(user_id)
            return chat.username
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    @bot.message_handler(commands=['make_poll'])
    def create_poll_command(message):
        if not check_rights(message): return 0
        create_poll(message)

    def create_poll(message):
        try:
            date = datetime.now()
            update_pupils_list()
            poll_message = bot.send_poll(
                chat_id=message.chat.id,
                question=f"Придете ли вы {date.day}/{date.month}/{date.year}?",
                options=[
                    "Да",
                    "Нет",
                    "Свой вариант (проспал, заболел)",
                    "Для ники <3"
                ],
                is_anonymous=False,
                allows_multiple_answers=False,
                type='regular'
            )
            bot.send_message(message.chat.id, "Опрос закрывается в течении полутора часов!")
            close_poll_later(message.chat.id, poll_message.id, poll_closure_minutes)
        except Exception as e:
            bot.reply_to(message, f"Ошибка при создании опроса: {e}")

    poll_statistics = pupils_list.pupils

    @bot.poll_answer_handler()
    def handle_poll_answer(poll):
        poll_id = poll.poll_id
        user_id = poll.user.id
        if not poll.option_ids: return 0
        selected_option = poll.option_ids[0]
        if selected_option == 3: return 0
        poll_statistics[f"{user_id}"][1] = pupils_list.Status(selected_option)
        print(f"Статистика опроса {poll_id}: {poll_statistics[f"{user_id}"][0]}, {pupils_list.Status(selected_option)}")

    @bot.message_handler(commands=['show_stats'])
    def show_stats_by_command(message):
        if not check_rights(message):
            bot.reply_to(message, "Недостаточно прав")
            return 0
        show_stats()


    def show_stats():
        if poll_statistics:
            present = [people for people in poll_statistics if poll_statistics[people][1] == Status.PRESENT]
            not_present = [people for people in poll_statistics if poll_statistics[people][1] == Status.NOT_PRESENT]
            missing = [people for people in poll_statistics if poll_statistics[people][1] == Status.MISSING]
            problems = [people for people in poll_statistics if poll_statistics[people][1] == Status.PROBLEMS]
            print(present)
            PR_list = [f"{pupils_list.pupils[person][0] +(trusted if pupils_list.pupils[person][2] == Status.TRUSTED else not_trusted)}\n" for person in present]
            NPR_list = [f"{pupils_list.pupils[person][0]+(trusted if pupils_list.pupils[person][2] == Status.TRUSTED else not_trusted)}\n" for person in not_present]
            MS_list = [f"{pupils_list.pupils[person][0]+(trusted if pupils_list.pupils[person][2] == Status.TRUSTED else not_trusted)}\n" for person in missing]
            PRB = [f"{pupils_list.pupils[person][0]+(trusted if pupils_list.pupils[person][2] == Status.TRUSTED else not_trusted)}\n" for person in problems]
            response = ''
            for list, name in [[PR_list, 'Присутствует:'], [NPR_list, "Не присутствует:"], [PRB, "По причине:"], [MS_list, "Не ответил:"]]:
                response += name + '\n'
                for pupil in list:
                    response += '- ' + pupil
                response += "\n"
            bot.send_message(admin_to_send_to, response)
            bot.send_message(admin_to_send_to, get_id_distrusted())
        else:
            bot.send_message(admin_to_send_to, "Нет данных по опросам")

    def update_pupils_list():
        for person in pupils_list.pupils.keys():
            pupils_list.pupils[person][1] = Status.MISSING

