import requests
from to_exel import ExcelManager


def get_items():
    manager = ExcelManager('items.xlsx',
                           ['Название', 'ID', 'Бренд', 'Ссылка', 'Название продавца', 'Цена', 'Форма', 'ОГРН', 'ИНН',
                            'Количество'])

    headers_user = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }

    with open('unique_ids.txt', 'r') as input_file:
        ids = [id.strip() for id in input_file.readlines()]

    for id in ids:
        data = []
        link = f'https://www.wildberries.ru/catalog/{id}/detail.aspx'
        try:
            response = requests.get(
                f'https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={id}',
                headers=headers_user
            )
            response.raise_for_status()  # Проверяем статус ответа, чтобы обрабатывать только успешные запросы
            json_data = response.json()

            for value in json_data.get('data', {}).get('products', []):
                val = value.get('volume', '')
                brand = value.get('brand', '')
                name = value.get('name', '')
                seller = value.get('supplierId', '')
                name_seller = value.get('supplier', '')
                for v in value.get('sizes', []):
                    price = int(v['price']['product']) / 100 if v.get('price') else 'Нет в наличии'

                    response_seller = requests.get(
                        f'http://static-basket-01.wbbasket.ru/vol0/data/supplier-by-id/{seller}.json',
                        headers=headers_user
                    )
                    response_seller.raise_for_status()

                    seller_data = response_seller.json()
                    ooo = seller_data.get('supplierFullName', '')
                    ogrn = seller_data.get('ogrn', '') or seller_data.get('ogrnip', '')
                    inn = seller_data.get('inn', '')

                    data.append([name, id, brand, link, name_seller, price, ooo, ogrn, inn, val])
        except Exception as ex:
            print(f"Ошибка при обработке товара с ID {id}: {ex}")
            continue

        manager.save_to_excel(data=data)


get_items()
