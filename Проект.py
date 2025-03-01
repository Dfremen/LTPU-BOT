import telebot
from datetime import date, timedelta

BOT_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}


def create_duty_schedule(n, start_date):
    if n < 2:
        raise ValueError("Количество учеников должно быть не менее 2.")

    schedule = {}
    current_date = start_date + timedelta(days=(7 - start_date.weekday()) % 7)
    group1_size = n // 2
    group2_size = n - group1_size

    for week in range(1, max(group1_size, group2_size) + 1):
        duty1 = week if week <= group1_size else None
        duty2 = group1_size + week if week <= group2_size else None
        schedule[current_date] = (duty1, duty2)
        current_date += timedelta(weeks=1)

    return schedule


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот, который поможет составить график дежурств. Используйте /schedule, чтобы начать.')


@bot.message_handler(commands=['schedule'])
def schedule_command(message):
    bot.send_message(message.chat.id, 'Введите количество учеников в классе.')
    user_data[message.chat.id] = {'step': 'get_students'}


@bot.message_handler(func=lambda message: message.chat.id in user_data)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    data = user_data[chat_id]

    if data['step'] == 'get_students':
        try:
            n = int(text)
            if n < 2:
                bot.send_message(chat_id, "Количество учеников должно быть не менее 2.")
                return
            data['n'] = n
            bot.send_message(chat_id, 'Введите год начала (например, 2024):')
            data['step'] = 'get_year'
        except ValueError:
            bot.send_message(chat_id, "Пожалуйста, введите целое число.")

    elif data['step'] == 'get_year':
        try:
            data['year'] = int(text)
            bot.send_message(chat_id, 'Введите месяц начала (например, 9 для сентября):')
            data['step'] = 'get_month'
        except ValueError:
            bot.send_message(chat_id, "Введите год в виде целого числа.")

    elif data['step'] == 'get_month':
        try:
            data['month'] = int(text)
            bot.send_message(chat_id, 'Введите день начала (например, 1):')
            data['step'] = 'get_day'
        except ValueError:
            bot.send_message(chat_id, "Введите месяц в виде целого числа.")

    elif data['step'] == 'get_day':
        try:
            data['day'] = int(text)
            bot.send_message(chat_id, 'Введите год окончания (например, 2025):')
            data['step'] = 'get_end_year'
        except ValueError:
            bot.send_message(chat_id, "Введите день в виде целого числа.")

    elif data['step'] == 'get_end_year':
        try:
            data['end_year'] = int(text)
            bot.send_message(chat_id, 'Введите месяц окончания (например, 3 для марта):')
            data['step'] = 'get_end_month'
        except ValueError:
            bot.send_message(chat_id, "Введите год окончания в виде целого числа.")

    elif data['step'] == 'get_end_month':
        try:
            data['end_month'] = int(text)
            bot.send_message(chat_id, 'Введите день окончания (например, 1):')
            data['step'] = 'get_end_day'
        except ValueError:
            bot.send_message(chat_id, "Введите месяц окончания в виде целого числа.")

    elif data['step'] == 'get_end_day':
        try:
            data['end_day'] = int(text)
            start_date = date(data['year'], data['month'], data['day'])
            end_date = date(data['end_year'], data['end_month'], data['end_day'])
            n = data['n']

            all_schedules = {}
            current_start_date = start_date

            while current_start_date <= end_date:
                schedule = create_duty_schedule(n, current_start_date)
                all_schedules.update(schedule)
                current_start_date += timedelta(weeks=n)

            data['schedule'] = all_schedules
            bot.send_message(chat_id,
                             'Расписание готово! Введите дату в формате дд.мм.гггг, чтобы узнать, кто дежурит.')
            data['step'] = 'schedule_ready'
        except ValueError:
            bot.send_message(chat_id, "Введите день окончания в виде целого числа.")

    elif data['step'] == 'schedule_ready':
        try:
            day, month, year = map(int, text.split("."))
            target_date = date(year, month, day)
            schedule = data['schedule']

            if target_date in schedule:
                duty1, duty2 = schedule[target_date]
                date_str = target_date.strftime("%d.%m.%Y")
                bot.send_message(chat_id, f"Дежурство на {date_str}: Подгруппа 1 - {duty1}, Подгруппа 2 - {duty2}")
            else:
                bot.send_message(chat_id, "На эту дату график дежурства не найден.")
        except (ValueError, IndexError):
            bot.send_message(chat_id, "Неверный формат даты, введите 'дд.мм.гггг'.")


if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True)

