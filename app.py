import os
import telebot

TOKEN = os.getenv("TG_TOKEN")
MY_TELEGRAM_ID_STR = os.getenv("MY_TELEGRAM_ID")

if TOKEN and MY_TELEGRAM_ID_STR:
    MY_TELEGRAM_ID = int(MY_TELEGRAM_ID_STR)
    bot = telebot.TeleBot(TOKEN)
    print("🚀 Telegram-бот успешно запущен на сервере Amvera...")

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.id == MY_TELEGRAM_ID:
            instruction = (
                "👋 **Приветствую, Босс!**\n\n"
                "Я помогу моментально собрать красивое сообщение для клиента.\n\n"
                "Пришлите мне данные строго в таком формате через косую черту:\n"
                "👉 `Имя клиента / Дата / Время / Имя мастера / Номер телефона мастера`"
            )
            bot.send_message(message.chat.id, instruction, parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.chat.id == MY_TELEGRAM_ID and "/" in message.text)
    def generate_template(message):
        try:
            data = [item.strip() for item in message.text.split("/")]
            if len(data) != 5:
                error_msg = (
                    "❌ **Ошибка формата!**\n\n"
                    "Вы ввели не все данные. Напишите строго 5 значений через косую черту:\n"
                    "`Имя / Дата / Время / Мастер / Телефон`"
                )
                bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
                return
            
            client_name, date_visit, time_visit, master_name, master_phone = data
            
            # ИДЕАЛЬНО ЧИСТЫЙ ТЕКСТ ПОДПИСИ БЕЗ ЛИШНИХ СИМВОЛОВ И ПАЛОЧЕК //
            ready_message = (
                f"✨ **Здравствуйте, {client_name}!**\n\n"
                f"Вам назначен монтаж:\n\n"
                f"🗓 **Дата приезда:** {date_visit}\n"
                f"⏰ **Время приезда:** {time_visit}\n"
                f"👷‍♂️ **Ваш монтажник:** {master_name}\n"
                f"📞 **Телефон мастера:** {master_phone}\n\n"
                f"⚠️ _Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее._\n\n"
                f"С уважением, Ваша Азбука тепла ☎️ - 287 88 47"
            )
            
            bot.send_message(message.chat.id, ready_message, parse_mode="Markdown")
            bot.send_message(message.chat.id, "⬆️ **Готово!** Зажмите сообщение выше, нажмите **Копировать** и отправьте клиенту.")
        except Exception as e:
            bot.reply_to(message, f"🚨 Ошибка при сборке: {e}")

    bot.infinity_polling()
else:
    print("⚠️ Ошибка: Настройки для Telegram не заданы в Переменных Amvera.")
