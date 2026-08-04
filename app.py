import os
import telebot
import requests

TOKEN = os.getenv("TG_TOKEN")
MY_TELEGRAM_ID_STR = os.getenv("MY_TELEGRAM_ID")
SMS_TOKEN = os.getenv("SMS_TOKEN")

if TOKEN and MY_TELEGRAM_ID_STR:
    MY_TELEGRAM_ID = int(MY_TELEGRAM_ID_STR)
    bot = telebot.TeleBot(TOKEN)
    print("🚀 Безопасный СМС-Бот успешно запущен на сервере Amvera...")

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.id == MY_TELEGRAM_ID:
            instruction = (
                "👋 **Приветствую, Босс!**\n\n"
                "Я полностью готов к работе и отправке СМС.\n\n"
                "Пришлите мне данные строго через косую черту:\n"
                "👉 `Имя клиента / Дата / Время / Имя мастера / Телефон мастера / ТЕЛЕФОН КЛИЕНТА`"
            )
            bot.send_message(message.chat.id, instruction, parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.chat.id == MY_TELEGRAM_ID and "/" in message.text)
    def generate_and_send_sms(message):
        try:
            data = [item.strip() for item in message.text.split("/")]
            if len(data) != 6:
                error_msg = (
                    "❌ **Ошибка формата!**\n\n"
                    "Напишите строго 6 значений через косую черту:\n"
                    "`Имя / Дата / Время / Мастер / Телефон мастера / Телефон КЛИЕНТА`"
                )
                bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
                return
            
            client_name, date_visit, time_visit, master_name, master_phone, client_phone = data
            
            # Очищаем номер клиента от лишних знаков
            clean_phone = "".join(filter(str.isdigit, client_phone))
            if clean_phone.startswith("8"):
                clean_phone = "7" + clean_phone[1:]
            elif clean_phone.startswith("9"):
                clean_phone = "7" + clean_phone
                
            # Текст сообщения без разметки Markdown, чтобы сотовые операторы его не ломали
            sms_text = (
                f"Здравствуйте, {client_name}!\n\n"
                f"Вам назначен монтаж:\n\n"
                f"Дата приезда: {date_visit}\n"
                f"Время приезда: {time_visit}\n"
                f"Ваш монтажник: {master_name}\n"
                f"Телефон мастера: {master_phone}\n\n"
                f"Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее.\n\n"
                f"С уважением, Ваша Азбука тепла ☎️ - 287 88 47"
            )
            
            # Сразу присылаем красивую версию вам в чат для контроля
            preview_message = (
                f"✨ **Здравствуйте, {client_name}!**\n\n"
                f"Вам назначен монтаж:\n\n"
                f"🗓 **Дата приезда:** {date_visit}\n"
                f"⏰ **Время приезда:** {time_visit}\n"
                f"👷‍♂️ **Ваш монтажник:** {master_name}\n"
                f"📞 **Телефон мастера:** {master_phone}\n\n"
                f"⚠️ _Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее._\n\n"
                f"С уважением, Ваша Азбука тепла ☎️ - 287 88 47"
            )
            bot.send_message(message.chat.id, f"📝 **Шаблон сообщения собран:**\n\n{preview_message}", parse_mode="Markdown")
            
            # Проверяем и отправляем СМС на SMS.ru
            if SMS_TOKEN and SMS_TOKEN != "скоро" and len(SMS_TOKEN) > 5:
                # Передаем параметры через словарь params для автоматического и безопасного кодирования текста
                sms_url = "https://sms.ru"
                payload = {
                    "api_id": SMS_TOKEN,
                    "to": clean_phone,
                    "msg": sms_text,
                    "json": 1
                }
                
                sms_res = requests.get(sms_url, params=payload, timeout=10).json()
                
                if sms_res.get("status") == "OK":
                    confirm_text = f"✅ **Успешно!** СМС отправлено клиенту {client_name} на номер +{clean_phone}."
                else:
                    status_text = sms_res.get("status_text", "Ошибка баланса или лимитов СМС-шлюза")
                    confirm_text = f"❌ **Ошибка СМС-сервиса:** {status_text}"
            else:
                confirm_text = "⚠️ **СМС не отправлено!** В переменных Amvera не задан или не заполнен ключ `SMS_TOKEN`. Но текст выше вы можете скопировать руками."
            
            bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"🚨 Ошибка при обработке: {e}")

    bot.infinity_polling()
else:
    print("⚠️ Критическая ошибка: В Amvera отсутствуют главные переменные TG_TOKEN или MY_TELEGRAM_ID.")
