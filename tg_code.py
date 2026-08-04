import telebot

TOKEN = "8981090497:AAE0zadyaVESxezY8n7KeslBGbyM4PLM9go"
MY_TELEGRAM_ID = 8546808704  # Ваш личный числовой ID в Telegram

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == MY_TELEGRAM_ID:
        instruction = "👋 Привет, Босс! Я соберу шаблон для ТГ. Пришлите данные:\nИмя / Дата / Время / Мастер / Телефон мастера"
        bot.reply_to(message, instruction)

@bot.message_handler(func=lambda message: message.chat.id == MY_TELEGRAM_ID and "/" in message.text)
def generate_template(message):
    try:
        data = [item.strip() for item in message.text.split("/")]
        if len(data) != 5:
            bot.reply_to(message, "❌ Ошибка! Нужно 5 значений через косую черту:\nИмя / Дата / Время / Мастер / Телефон")
            return
        
        c_name, d_visit, t_visit, m_name, m_phone = data
        
        ready_message = (
            f"✨ **Здравствуйте, {c_name}!**\n\n"
            f"Выдано задание на монтаж системы отопления на Вашем объекте. 🔥\n\n"
            f"🗓 **Дата приезда:** {d_visit}\n"
            f"⏰ **Время приезда:** {t_visit}\n"
            f"👷‍♂️ **Ваш монтажник:** {m_name}\n"
            f"📞 **Телефон мастера:** {m_phone}\n\n"
            f"⚠️ _Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее._\n\n"
            f"С уважением, Ваша команда по отоплению! 👋"
        )
        
        bot.send_message(message.chat.id, ready_message, parse_mode="Markdown")
        bot.send_message(message.chat.id, "⬆️ Скопируйте текст выше и отправьте клиенту!")
    except Exception as e:
        bot.reply_to(message, f"🚨 Ошибка: {e}")

bot.infinity_polling()
