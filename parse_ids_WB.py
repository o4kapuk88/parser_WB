import time
import requests

list_category = ['popular', 'rate', 'priceup', 'pricedown', 'newly', 'benefit']

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36'
}


def get_items():
    unique_ids = set()  # Для хранения уникальных идентификаторов
    with open('unique_ids.txt', 'a+') as file:
        # Чтение всех ранее записанных идентификаторов
        file.seek(0)
        existing_ids = set(line.strip() for line in file)

        for category in list_category:
            for page in range(1, 101):
                url = f'https://search.wb.ru/exactmatch/ru/common/v5/search?ab_searchfilters=t1&appType=1&curr=rub&dest=-1257786&fbrand=2628;9083;120357;146549;221346;236994;254450;280487;346818;436984;453188;453299;794043;1059752;1085665;1492241;2586302;6179007;20155844;21199150;39271604;43324231;52747986;71896117;256138020;310535825;310608835;310659889;310746978;310785895;310790195;310796074;310800808;310818971;310822329;310906131;310926219;310941186;310941263;310946474;310953701;310957504;310988831;310992261;311003231;311018638;311085913;311090339;311091663;311117417;311137858;311146965;311157032;311165656;311177986;311180722;311181092;311193768;311197809;311207977;311210125;311212304;311252821;311262128;311265892;311273083;311273770;311291758;311292079;311297091;311306945;311315175;311316770;311316774;311316787&page={page}&query=attar%20collection&resultset=catalog&sort={category}&spp=30&suppressSpellcheck=false'
                time.sleep(0.3)
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    print(f"Ошибка при запросе {url}: {response.status_code}")
                    continue

                try:
                    json_data = response.json()
                except Exception as e:
                    print(f"Ошибка при разборе JSON: {e}")
                    continue

                # Получение списка идентификаторов и добавление только новых уникальных идентификаторов
                products = json_data.get('data', {}).get('products', [])
                for product in products:
                    product_id = str(product.get('id'))
                    if product_id not in existing_ids:
                        existing_ids.add(product_id)
                        unique_ids.add(product_id)

        for unique_id in unique_ids:
            file.write(unique_id + '\n')


get_items()
