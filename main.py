import telebot
from telebot import types
import threading
import time

from db import init_db, add_item, get_items, remove_item, update_price, get_all_items
from wb import extract_articule, get_price

TOKEN = "8661089957:AAHB816uUEyrOU1gpY7eQOuQKnsaQArzrck"

bot = telebot.TeleBot(TOKEN)


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить товар")
    markup.add("📋 Мои товары", "🔍 Проверить цены")
    markup.add("🗑 Удалить товар")
    return markup


init_db()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет!\n\n"
        "Я отслеживаю цену товаров Wildberries и сообщаю, когда цена падает.\n\n"
        "Нажми кнопку или отправь ссылку на товар.",
        reply_markup=main_menu()
    )


# --------- ДОБАВЛЕНИЕ ТОВАРА ---------

user_waiting_link = set()


@bot.message_handler(func=lambda m: m.text == "➕ Добавить товар")
def ask_link(message):
    user_waiting_link.add(message.from_user.id)
    bot.send_message(message.chat.id, "Отправь ссылку WB на товар или просто артикул:")


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    # если пользователь не добавляет товар - игнорим обычный текст
    if message.from_user.id not in user_waiting_link:
        return

    user_waiting_link.remove(message.from_user.id)

    url_or_text = message.text.strip()
    articule = extract_articule(url_or_text)

    if not articule:
        bot.send_message(
            message.chat.id,
            "❌ Не могу найти артикул.\n\n"
            "Пришли ссылку на карточку товара (catalog/123...).",
            reply_markup=main_menu()
        )
        return

    price = get_price(articule)

    if price is None:
        bot.send_message(
            message.chat.id,
            "❌ Не смог получить цену.\n"
            "Скорее всего это не ссылка на товар (например корзина или подборка).",
            reply_markup=main_menu()
        )
        return

    url = url_or_text
    if url.isdigit():
        url = f"https://www.wildberries.ru/catalog/{articule}/detail.aspx"

    add_item(message.from_user.id, url, articule, price)

    bot.send_message(
        message.chat.id,
        f"✅ Добавлено!\nАртикул: {articule}\nЦена сейчас: {price} ₽\n\n"
        "⏳ Автопроверка каждые 30 минут включена.",
        reply_markup=main_menu()
    )


# --------- СПИСОК ТОВАРОВ ---------

@bot.message_handler(func=lambda m: m.text == "📋 Мои товары")
def list_items(message):
    items = get_items(message.from_user.id)

    if not items:
        bot.send_message(message.chat.id, "📭 У тебя нет товаров.", reply_markup=main_menu())
        return

    text = "📌 Твои товары:\n\n"
    for item in items:
        item_id, url, articule, last_price = item
        text += f"ID: {item_id}\nЦена: {last_price} ₽\n{url}\n\n"

    bot.send_message(message.chat.id, text, reply_markup=main_menu())


# --------- УДАЛЕНИЕ ---------

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить товар")
def delete_help(message):
    items = get_items(message.from_user.id)

    if not items:
        bot.send_message(message.chat.id, "📭 У тебя нет товаров.", reply_markup=main_menu())
        return

    text = "Напиши ID товара, который удалить.\n\n"
    for item in items:
        item_id, url, articule, last_price = item
        text += f"ID: {item_id} | {last_price} ₽\n"

    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, "Отправь ID числом:")

    bot.register_next_step_handler(message, delete_by_id)


def delete_by_id(message):
    try:
        item_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Нужно число.", reply_markup=main_menu())
        return

    remove_item(message.from_user.id, item_id)
    bot.send_message(message.chat.id, "🗑 Удалено.", reply_markup=main_menu())


# --------- РУЧНАЯ ПРОВЕРКА ---------

@bot.message_handler(func=lambda m: m.text == "🔍 Проверить цены")
def manual_check(message):
    items = get_items(message.from_user.id)

    if not items:
        bot.
        send_message(message.chat.id, "📭 Нет товаров для проверки.", reply_markup=main_menu())
        return

    bot.send_message(message.chat.id, "⏳ Проверяю цены...")

    for item in items:
        item_id, url, articule, last_price = item
        new_price = get_price(articule)

        if new_price is None:
            continue

        if new_price < last_price:
            bot.send_message(
                message.chat.id,
                f"🔥 Цена упала!\nБыло: {last_price} ₽\nСтало: {new_price} ₽\n{url}"
            )
            update_price(item_id, new_price)

        elif new_price > last_price:
            update_price(item_id, new_price)

    bot.send_message(message.chat.id, "✅ Проверка завершена.", reply_markup=main_menu())


# --------- АВТОПРОВЕРКА ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ---------

def auto_check_loop():
    while True:
        try:
            all_items = get_all_items()

            for item in all_items:
                item_id, user_id, url, articule, last_price = item

                new_price = get_price(articule)
                if new_price is None:
                    continue

                if new_price < last_price:
                    bot.send_message(
                        user_id,
                        f"🔥 Скидка!\nБыло: {last_price} ₽\nСтало: {new_price} ₽\n{url}"
                    )
                    update_price(item_id, new_price)

                elif new_price > last_price:
                    update_price(item_id, new_price)

        except Exception as e:
            print("Ошибка автопроверки:", e)

        # каждые 30 минут
        time.sleep(1800)


threading.Thread(target=auto_check_loop, daemon=True).start()


bot.infinity_polling()
