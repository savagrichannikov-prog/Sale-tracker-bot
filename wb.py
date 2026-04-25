import re
import requests

def extract_articule(url: str):
    match = re.search(r"/catalog/(\d+)/", url)
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
    price = product.get("salePriceU")
    if price is None:
        return None

    return int(price / 100)
