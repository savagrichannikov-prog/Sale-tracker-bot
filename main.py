import telebot
from db import add_item, get_items, remove_item, update_price
from wb import extract_articule, get_price

TOKEN = "8661089957:AAHB816uUEyrOU1gpY7eQOuQKnsaQArzrck"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,
                     "👋 Привет! Я бот отслеживания скидок Wildberries.\n\n"
                     "Команды:\n"
                     "/add ссылка - добавить товар\n"
                     "/list - список товаров\n"
                     "/remove ID - удалить\n"
                     "/check - проверить цены вручную\n\n"
                     "Пример:\n/add https://www.wildberries.ru/catalog/12345678/detail.aspx")


@bot.message_handler(commands=["add"])
def add(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ Используй: /add ссылка")
        return

    url = parts[1]
    articule = extract_articule(url)

    if not articule:
        bot.send_message(message.chat.id, "❌ Не смог найти артикул. Проверь ссылку WB.")
        return

    price = get_price(articule)
    if price is None:
        bot.send_message(message.chat.id, "❌ Не смог получить цену. Попробуй позже.")
        return

    add_item(message.from_user.id, url, articule, price)
    bot.send_message(message.chat.id, f"✅ Добавлено!\nАртикул: {articule}\nЦена сейчас: {price} ₽")


@bot.message_handler(commands=["list"])
def list_items(message):
    items = get_items(message.from_user.id)

    if not items:
        bot.send_message(message.chat.id, "📭 У тебя пока нет товаров.")
        return

    text = "📌 Твои товары:\n\n"
    for item in items:
        item_id, url, articule, last_price = item
        text += f"ID: {item_id}\nЦена: {last_price} ₽\n{url}\n\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["remove"])
def remove(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ Используй: /remove ID")
        return

    try:
        item_id = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ ID должен быть числом.")
        return

    remove_item(message.from_user.id, item_id)
    bot.send_message(message.chat.id, "🗑 Удалено.")


@bot.message_handler(commands=["check"])
def check_prices(message):
    items = get_items(message.from_user.id)
    if not items:
        bot.send_message(message.chat.id, "📭 Нет товаров для проверки.")
        return

    for item in items:
        item_id, url, articule, last_price = item
        new_price = get_price(articule)

        if new_price is None:
            continue

        if new_price < last_price:
            bot.send_message(message.chat.id,
                             f"🔥 Цена упала!\n"
                             f"Было: {last_price} ₽\n"
                             f"Стало: {new_price} ₽\n{url}")
            update_price(item_id, new_price)

        elif new_price > last_price:
            update_price(item_id, new_price)

    bot.send_message(message.chat.id, "✅ Проверка завершена.")


bot.infinity_polling()
