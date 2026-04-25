import re
import requests


def extract_articule(url: str):
    """
    Пытаемся достать артикул WB из любых ссылок.
    Работает для:
    - /catalog/12345678/detail.aspx
    - ?nm=12345678
    - если пользователь просто отправил число
    """

    # если человек отправил просто цифры
    if url.strip().isdigit():
        return url.strip()

    # /catalog/12345678/
    match = re.search(r"/catalog/(\d+)", url)
    if match:
        return match.group(1)

    # nm=12345678
    match = re.search(r"nm=(\d+)", url)
    if match:
        return match.group(1)

    # если где-то в ссылке есть большое число (часто артикул)
    match = re.search(r"(\d{5,12})", url)
    if match:
        return match.group(1)

    return None


def get_price(articule: str):
    api_url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={articule}"

    r = requests.get(api_url, timeout=10)
    data = r.json()

    products = data.get("data", {}).get("products", [])
    if not products:
        return None

    product = products[0]

    price = product.get("salePriceU")  # цена в копейках
    if price is None:
        return None

    return int(price / 100)
