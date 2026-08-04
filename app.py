import os
import telebot
import http.client
import urllib.parse
import json

TOKEN = os.getenv("TG_TOKEN")
MY_TELEGRAM_ID_STR = os.getenv("MY_TELEGRAM_ID")
SMS_TOKEN = os.getenv("SMS_TOKEN")

if TOKEN and MY_TELEGRAM_ID_STR:
    MY_TELEGRAM_ID = int(MY_TELEGRAM_ID_STR)
    bot = telebot.TeleBot(TOKEN)
    print("🚀 СМС-Бот со смайликами для клиентов запущен на сервере Amvera...")

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.chat.id == MY_TELEGRAM_ID:
            instruction = (
                "👋 **Приветствую, Босс!**\n\n"
                "Я готов собрать шаблон со смайликами и отправить СМС на телефон.\n\n"
                "Пришлите мне данные строго через косую черту (всего 7 значений):\n"
                "👉 `Имя / Дата / Время / Мастер / Телефон мастера / Телефон клиента / АДРЕС ОБЪЕКТА`"
            )
            bot.send_message(message.chat.id, instruction, parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.chat.id == MY_TELEGRAM_ID and "/" in message.text)
    def generate_and_send_sms(message):
        try:
            data = [item.strip() for item in message.text.split("/")]
            if len(data) != 7:
                error_msg = (
                    "❌ **Ошибка формата!**\n\n"
                    "Вы ввели не все данные. Напишите строго 7 значений через косую черту:\n"
                    "`Имя / Дата / Время / Мастер / Телефон мастера / Телефон клиента / АДРЕС ОБЪЕКТА`"
                )
                bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
                return
            
            client_name, date_visit, time_visit, master_name, master_phone, client_phone, object_address = data
            
            # Очищаем номер клиента от лишних знаков
            clean_phone = "".join(filter(str.isdigit, client_phone))
            if clean_phone.startswith("8"):
                clean_phone = "7" + clean_phone[1:]
            elif clean_phone.startswith("9"):
                clean_phone = "7" + clean_phone
                
            # ТЕКСТ СМС ДЛЯ КЛИЕНТА (Теперь полностью со всеми красивыми эмодзи!)
            sms_text = (
                f"✨ Здравствуйте, {client_name}!\n\n"
                f"Вам назначен монтаж:\n\n"
                f"🗓 Дата приезда: {date_visit}\n"
                f"⏰ Время приезда: {time_visit}\n"
                f"🏠 Адрес объекта: {object_address}\n"
                f"👷‍♂️ Ваш монтажник: {master_name}\n"
                f"📞 Телефон мастера: {master_phone}\n\n"
                f"⚠️ Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее.\n\n"
                f"С уважением, Ваша Азбука тепла ☎️ - 287 88 47"
            )
            
            # КРАСИВАЯ ПРЕВЬЮ-ВЕРСИЯ В ЧАТ ДЛЯ ВАС (С жирным шрифтом Markdown)
            preview_message = (
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
            bot.send_message(message.chat.id, f"📝 **Шаблон сообщения собран:**\n\n{preview_message}", parse_mode="Markdown")
            
            if SMS_TOKEN and len(SMS_TOKEN) > 5:
                encoded_msg = urllib.parse.quote(sms_text)
                path_url = f"/sms/send?api_id={SMS_TOKEN}&to={clean_phone}&msg={encoded_msg}&json=1"
                
                try:
                    conn = http.client.HTTPSConnection("sms.ru", timeout=10)
                    conn.request("GET", path_url, headers={"User-Agent": "Mozilla/5.0"})
                    response = conn.getresponse()
                    
                    if response.status == 200:
                        html_data = response.read().decode('utf-8')
                        sms_res = json.loads(html_data)
                        
                        if sms_res.get("status") == "OK":
                            phone_status = sms_res.get("sms", {}).get(clean_phone, {})
                            if phone_status.get("status") == "OK":
                                confirm_text = f"✅ **Успешно!** Запрос принят шлюзом. СМС со смайликами отправлено клиенту {client_name} на номер +{clean_phone}."
                            else:
                                status_text = phone_status.get("status_text", "Ошибка лимитов сети")
                                confirm_text = f"❌ **Оператор отклонил СМС:** {status_text}"
                        else:
                            status_text = sms_res.get("status_text", "Ошибка баланса")
                            confirm_text = f"❌ **Ошибка СМС-сервиса:** {status_text}"
                    else:
                        confirm_text = f"❌ **Сбой сотового шлюза.** Код: {response.status}"
                    conn.close()
                except Exception as net_err:
                    confirm_text = f"❌ **Ошибка сокета:** {net_err}."
            else:
                confirm_text = "⚠️ **СМС не отправлено!** В переменных Amvera не задан ключ `SMS_TOKEN`."
            
            bot.send_message(message.chat.id, confirm_text, parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"🚨 Ошибка при обработке: {e}")

    bot.infinity_polling()
else:
    print("⚠️ Критическая ошибка: В Amvera отсутствуют главные переменные TG_TOKEN или MY_TELEGRAM_ID.")
