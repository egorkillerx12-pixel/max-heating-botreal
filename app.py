import os
import telebot

TOKEN = os.getenv("TG_TOKEN")
MY_TELEGRAM_ID_STR = os.getenv("MY_TELEGRAM_ID")

if TOKEN and MY_TELEGRAM_ID_STR:
    MY_TELEGRAM_ID = int(MY_TELEGRAM_ID_STR)
    bot = telebot.TeleBot(TOKEN)
    print("🚀 Бот-генератор шаблонов Азбука Тепла успешно запущен...")

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.id == MY_TELEGRAM_ID:
            instruction = (
                "👋 **Приветствую, Босс!**\n\n"
                "Я моментально соберу красивое сообщение для клиента.\n\n"
                "Пришлите мне данные, написав каждое значение **с новой строки** (всего 6 строк):\n\n"
                "👤 Имя клиента\n"
                "🗓 Дата\n"
                "⏰ Время\n"
                "👷‍♂️ Имя мастера\n"
                "📞 Телефон мастера\n"
                "🏠 АДРЕС ОБЪЕКТА"
            )
            bot.send_message(message.chat.id, instruction, parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.chat.id == MY_TELEGRAM_ID)
    def generate_template(message):
        try:
            # Разделяем текст по строкам (по нажатию Enter)
            data = [line.strip() for line in message.text.split('\n') if line.strip()]
            
            if len(data) != 6:
                error_msg = (
                    "❌ **Ошибка формата!**\n\n"
                    "Вы ввели не все данные. Напишите строго 6 значений, каждое **с новой строки**:\n"
                    "1. Имя\n2. Дата\n3. Время\n4. Мастер\n5. Телефон мастера\n6. АДРЕС ОБЪЕКТА"
                )
                bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
                return
            
            client_name, date_visit, time_visit, master_name, master_phone, object_address = data
            
            # ФИНАЛЬНЫЙ КРАСИВЫЙ ШАБЛОН КОМПАНИИ С АДРЕСОМ И СМАЙЛИКАМИ
            ready_message = (
                f"✨ **Здравствуйте, {client_name}!**\n\n"
                f"Вам назначен монтаж:\n\n"
                f"🗓 **Дата приезда:** {date_visit}\n"
                f"⏰ **Время приезда:** {time_visit}\n"
                f"🏠 **Адрес объекта:** {object_address}\n"
                f"👷‍♂️ **Ваш монтажник:** {master_name}\n"
                f"📞 **Телефон мастера:** {master_phone}\n\n"
                f"⚠️ _Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее._\n\n"
                f"С уважением, Ваша Азбука тепла ☎️ - 287 88 47"
            )
            
            bot.send_message(message.chat.id, ready_message, parse_mode="Markdown")
            bot.send_message(message.chat.id, "⬆️ **Готово!** Зажмите сообщение выше, нажмите **Копировать** и бесплатно отправьте клиенту в WhatsApp или СМС.")
        except Exception as e:
            bot.reply_to(message, f"🚨 Ошибка при сборке текста: {e}")

    bot.infinity_polling()
else:
    print("⚠️ Критическая ошибка: В Amvera отсутствуют переменные TG_TOKEN или MY_TELEGRAM_ID.")
