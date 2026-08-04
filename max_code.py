import os
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Скрипт берет токен и ваш ID из секретных переменных сервера
TOKEN = os.getenv("MAX_TOKEN")
MY_MAX_ID_STR = os.getenv("MY_MAX_ID")

URL_BASE = "https://max.ru"

if TOKEN and MY_MAX_ID_STR:
    MY_MAX_ID = int(MY_MAX_ID_STR)
    HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    last_update_id = 0
    
    while True:
        try:
            response = requests.get(f"{URL_BASE}/updates?offset={last_update_id + 1}", headers=HEADERS, verify=False, timeout=10)
            if response.status_code == 200:
                for update in response.json().get("updates", []):
                    last_update_id = update.get("update_id", last_update_id)
                    message = update.get("message", {})
                    chat_id = message.get("chat_id")
                    text = message.get("text", "").strip()
                    
                    if chat_id == MY_MAX_ID:
                        if text.lower() in ["/start", "старт"]:
                            reply = "👋 Привет, Босс! Я соберу шаблон для MAX. Пришлите данные:\nИмя / Дата / Время / Мастер / Телефон мастера"
                            requests.post(f"{URL_BASE}/messages", json={"chat_id": MY_MAX_ID, "body": {"text": reply}}, headers=HEADERS, verify=False)
                        
                        elif "/" in text:
                            data = [item.strip() for item in text.split("/")]
                            if len(data) != 5:
                                requests.post(f"{URL_BASE}/messages", json={"chat_id": MY_MAX_ID, "body": {"text": "❌ Ошибка! Нужно 5 значений через косую черту:\nИмя / Дата / Время / Мастер / Телефон"}}, headers=HEADERS, verify=False)
                                continue
                            
                            c_name, d_visit, t_visit, m_name, m_phone = data
                            ready_message = (
                                f"✨ Здравствуйте, {c_name}!\n\n"
                                f"Выдано задание на монтаж системы отопления на Вашем объекте. 🔥\n\n"
                                f"🗓 Дата приезда: {d_visit}\n"
                                f"⏰ Время приезда: {t_visit}\n"
                                f"👷‍♂️ Ваш монтажник: {m_name}\n"
                                f"📞 Телефон мастера: {m_phone}\n\n"
                                f"⚠️ Пожалуйста, если у Вас изменятся планы или потребуется перенести визит, сообщите нам об этом заранее.\n\n"
                                f"С уважением, Ваша команда по отоплению! 👋"
                            )
                            requests.post(f"{URL_BASE}/messages", json={"chat_id": MY_MAX_ID, "body": {"text": ready_message}}, headers=HEADERS, verify=False)
                            requests.post(f"{URL_BASE}/messages", json={"chat_id": MY_MAX_ID, "body": {"text": "⬆️ Скопируйте текст выше и отправьте клиенту!"}}, headers=HEADERS, verify=False)
        except Exception as e:
            pass
        time.sleep(2)
else:
    print("⚠️ Настройки для мессенджера MAX не заданы в Переменных.")
    while True:
        time.sleep(60)
