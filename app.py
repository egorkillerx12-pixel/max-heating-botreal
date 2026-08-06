import os
import telebot
from telebot import types

TOKEN = os.getenv("TG_TOKEN")

# Собираем список из 3 разрешенных ID из настроек Amvera
ALLOWED_IDS = []
for key in ["MY_TELEGRAM_ID", "MY_TELEGRAM_ID_2", "MY_TELEGRAM_ID_3"]:
    id_str = os.getenv(key)
    if id_str:
        try:
            ALLOWED_IDS.append(int(id_str))
        except ValueError:
            pass

if TOKEN and ALLOWED_IDS:
    bot = telebot.TeleBot(TOKEN)
    print(f"🚀 Бот компании Азбука Тепла с кнопками доступа запущен...")

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        # Создаем интерактивные кнопки под сообщением
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        # Кнопка-ссылка на сайт (работает для всех)
        btn_site = types.InlineKeyboardButton(text="🌐 Перейти на сайт Азбука тепла.рф", url="https://азбукатепла.рф")
        
        # Кнопка для создания шаблона (запрос уйдет в систему)
        btn_template = types.InlineKeyboardButton(text="🛠 Создать шаблон монтажа", callback_data="start_template")
        
        markup.add(btn_site, btn_template)

        welcome_text = (
            "✨ **Добро пожаловать в официальный бот компании «Азбука тепла»!** ✨\n\n"
            "Выберите интересующее вас действие с помощью кнопок ниже 👇"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

    # Обработка нажатия на кнопку "Создать шаблон"
    @bot.callback_query_handler(func=lambda call: call.data == "start_template")
    def callback_template(call):
        # Проверяем, есть ли у пользователя доступ
        if call.message.chat.id in ALLOWED_IDS:
            instruction = (
                "📝 **Отлично, Босс! Начинаем сборку шаблона.**\n\n"
                "Пришлите мне данные клиента, написав каждое значение **с новой строки** (всего 6 строк):\n\n"
                "👤 Имя клиента\n"
                "🗓 Дата\n"
                "⏰ Время\n"
                "👷‍♂️ Имя мастера\n"
                "📞 Телефон мастера\n"
                "🏠 Адрес объекта"
            )
            bot.send_message(call.message.chat.id, instruction, parse_mode="Markdown")
            # Закрываем часы загрузки на кнопке у пользователя
            bot.answer_callback_query(call.id)
        else:
            # Если нажал чужой человек — выдаем ошибку во всплывающем окне
            bot.answer_callback_query(call.id, text="❌ У вас нет прав доступа к этой функции!", show_alert=True)

    # Прием текстовых данных (работает только для админов)
    @bot.message_handler(func=lambda message: message.chat.id in ALLOWED_IDS)
    def generate_template(message):
        try:
            # Разделяем текст по строкам
            data = [line.strip() for line in message.text.split('\n') if line.strip()]
            
            if len(data) != 6:
                error_msg = (
                    "❌ **Ошибка формата!**\n\n"
                    "Вы ввели не все данные. Напишите строго 6 значений, каждое **с новой строки**:\n"
                    "1. Имя\n2. Дата\n3. Время\n4. Мастер\n5. Телефон мастера\n6. Адрес объекта"
                )
                bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
                return
            
            client_name, date_visit, time_visit, master_name, master_phone, object_address = data
            
            # Финальный красивый шаблон Азбуки Тепла
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

    # Игнорируем любые текстовые сообщения от чужих людей
    @bot.message_handler(func=lambda message: message.chat.id not in ALLOWED_IDS)
    def ignore_strangers(message):
        bot.send_message(message.chat.id, "❌ У вас нет прав для отправки команд этому боту.")

    bot.infinity_polling()
else:
    print("⚠️ Критическая ошибка: В Amvera не настроен TG_TOKEN или список ALLOWED_IDS пуст.")
