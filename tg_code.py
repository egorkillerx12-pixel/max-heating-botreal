import telebot

# НАСТРОЙКА КЛЮЧЕЙ TELEGRAM
TOKEN = "8981090497:AAE0zadyaVESxezY8n7KeslBGbyM4PLM9go"
MY_TELEGRAM_ID = 8546808704  # Ваш личный числовой ID в Telegram

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == MY_TELEGRAM_ID:
        bot.reply_to(message, "👋 Привет, Босс! Формат для ТГ:\nИмя / Дата / Время / Мастер / ID_клиента_в_ТГ")

@bot.message_handler(func=lambda message: message.chat.id == MY_TELEGRAM_ID and "/" in message.text)
def send_client_info(message):
    try:
        data = [item.strip() for item in message.text.split("/")]
        if len(data) != 5:
            bot.reply_to(message, "❌ Ошибка! Нужно 5 значений через /")
            return
        c_name, d_visit, t_visit, m_name, t_id = data
        msg = f"Здравствуйте, {c_name}!\n\nМонтаж отопления назначен.\n🗓 Дата: {d_visit}\n⏰ Время: {t_visit}\n👷‍♂️ Мастер: {m_name}"
        bot.send_message(int(t_id), msg)
        bot.reply_to(message, f"✅ Отправлено в ТГ для {c_name}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка ТГ: {e}")

bot.infinity_polling()
