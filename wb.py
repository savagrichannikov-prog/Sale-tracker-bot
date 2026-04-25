import re
import requests


def extract_articule(text: str):
    if not text:
        return None

    text = text.strip()

    # если отправили просто число
    if text.isdigit():
        return text

    # /catalog/12345678/
    match = re.search(r"/catalog/(\d+)", text)
    if match:
        return match.group(1)

    # nm=12345678
    match = re.search(r"nm=(\d+)", text)
    if match:
        return match.group(1)

    # если есть большое число в ссылке
    match = re.search(r"(\d{5,12})", text)
    if match:
        return match.group(1)

    return None


def get_price(articule: str):
    api_url = (
        "https://card.wb.ru/cards/v1/detail"
        f"?appType=1&curr=rub&dest=-1257786&spp=30&nm={articule}"
    )

    r = requests.get(api_url, timeout=10)
    data = r.json()

    products = data.get("data", {}).get("products", [])
    if not products:
        return None

    product = products[0]

    # цена со скидкой
    price = product.get("salePriceU")

    if price is None:
        return None

    return int(price / 100)
