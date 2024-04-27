import os
import re
import pandas as pd


def safe_filename(filename):
    # Заменяем недопустимые символы на подчеркивания
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)


def split_ids_by_seller_and_brand(input_file, output_folder):
    # Загрузка данных из исходного файла
    df = pd.read_excel(input_file)

    # Получение уникальных названий продавцов
    unique_sellers = df['Название продавца'].unique()

    # Проверка наличия папки output_folder и создание ее, если она не существует
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Проход по каждому уникальному продавцу
    for seller in unique_sellers:
        # Создание подпапки для каждого продавца
        seller_folder = f"{output_folder}/{safe_filename(seller)}"
        if not os.path.exists(seller_folder):
            os.makedirs(seller_folder)

        # Получение группы товаров для текущего продавца
        seller_group = df[df['Название продавца'] == seller]

        # Получение уникальных брендов для данного продавца
        unique_brands = seller_group['Бренд'].unique()

        # Проход по каждому уникальному бренду
        for brand in unique_brands:
            # Получение товаров данного бренда
            brand_group = seller_group[seller_group['Бренд'] == brand]
            ids = brand_group['ID'].tolist()  # Получение списка ID для данного бренда

            # Разделение ID на группы по 100 и запись каждой группы в новый файл
            num_files = len(ids) // 100 + (1 if len(ids) % 100 > 0 else 0)  # Вычисление количества файлов
            for i in range(num_files):
                start_idx = i * 100
                end_idx = min((i + 1) * 100, len(ids))
                ids_subset = ids[start_idx:end_idx]

                # Создание безопасного имени файла
                safe_brand_name = safe_filename(brand)
                output_file = f"{seller_folder}/{safe_brand_name}_{i + 1}.xlsx"

                # Запись группы ID в новый файл
                pd.DataFrame({'ID': ids_subset}).to_excel(output_file, index=False)


# Пример использования функции
split_ids_by_seller_and_brand('items.xlsx', 'texts')
