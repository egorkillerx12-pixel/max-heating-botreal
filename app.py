import os
import telebot
import requests

# Включаем официальное российское зеркало для Telegram
from telebot import apihelper
apihelper.API_URL = "https://tlgr.org{0}/{1}"

TOKEN = os.getenv("TG_TOKEN")
MY_TELEGRAM_ID_STR = os.getenv("MY_TELEGRAM_ID")
SMS_TOKEN = os.getenv("SMS_TOKEN")  # Ключ от SMS.ru

if TOKEN and MY_TELEGRAM_ID_STR:
    MY_TELEGRAM_ID = int(MY_TELEGRAM_ID_STR)
    bot = telebot.TeleBot(TOKEN)
    print("🚀 СМС-Бот успешно запущен на сервере Amvera...")

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.id == MY_TELEGRAM_ID:
            instruction = (
                "👋 **Приветствую, Босс!**\n\n"
                "Я умею автоматически отправлять СМС-уведомления клиентам.\n\n"
                "Пришлите мне данные строго в таком формате через косую черту:\n"
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
                    "Вы ввели не все данные. Напишите строго 6 значений через косую черту:\n"
                    "`Имя / Дата / Время / Мастер / Телефон мастера / Телефон КЛИЕНТА`"
                )
                bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
                return
            
            client_name, date_visit, time_visit, master_name, master_phone, client_phone = data
            
            # Автоматически очищаем номер телефона клиента от лишних символов
            clean_phone = "".join(filter(str.isdigit, client_phone))
            if clean_phone.startswith("8"):
                clean_phone = "7" + clean_phone[1:]
            elif clean_phone.startswith("9"):
                clean_phone = "7" + clean_phone
                
            # Собираем текст СМС (убираем лишние эмодзи для экономии длины СМС)
            sms_text = (
                f"Здравствуйте, {client_name}! Вам назначен монтаж. "
                f"Дата приезда: {date_visit}. Время: {time_visit}. "
                f"Ваш монтажник: {master_name}, тел: {master_phone}. "
                f"Если изменятся планы, сообщите заранее. Ваша Азбука тепла 287-88-47"
            )
            
            # Отправляем СМС через сервис SMS.ru
            if SMS_TOKEN:
                sms_url = f"https://sms.ru{SMS_TOKEN}&to={clean_phone}&msg={sms_text}&json=1"
                sms_res = requests.get(sms_url, timeout=10).json()
                
                if sms_res.get("status") == "OK":
                    confirm_text = f"✅ **Успешно!** СМС-сообщение отправлено клиенту {client_name} на номер +{clean_phone}."
                else:
                    status_text = sms_res.get("status_text", "Неизвестная ошибка")
                    confirm_text = f"❌ **Ошибка СМС-сервиса:** {status_text}"
            else:
                confirm_text = f"⚠️ Ключ SMS_TOKEN не задан в Переменных Amvera. СМС не отправлено."
            
            # Присылаем отчет и текст сообщения вам в чат
            bot.send_message(message.chat.id, f"📝 **Текст отправленного сообщения:**\n\n{sms_text}", parse_mode="Markdown")
            bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"🚨 Техническая ошибка при отправке: {e}")

    bot.infinity_polling()
else:
    print("⚠️ Ошибка: Настройки для Telegram не заданы в Переменных Amvera.")
