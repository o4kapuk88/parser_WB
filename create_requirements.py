import openpyxl
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph
import pandas as pd
import re
import os


def safe_filename(filename):
    # Заменяем недопустимые символы подчеркиванием
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)


def split_ids_by_seller_and_brand(input_file, output_folder):
    # Загружаем данные из файла
    df = pd.read_excel(input_file)

    # Получаем уникальные имена продавцов
    unique_sellers = df['Название продавца'].unique()

    # Итерируемся по каждому уникальному продавцу
    for seller in unique_sellers:
        # Создаем папку для каждого продавца
        seller_folder = os.path.join(output_folder, safe_filename(seller))
        if not os.path.exists(seller_folder):
            os.makedirs(seller_folder)

        # Получаем группу товаров для текущего продавца
        seller_group = df[df['Название продавца'] == seller]

        # Получаем уникальные бренды для этого продавца
        unique_brands = seller_group['Бренд'].unique()

        # Итерируемся по каждому уникальному бренду
        for brand in unique_brands:
            # Получаем товары для этого бренда и продавца
            product_data = seller_group[(seller_group['Бренд'] == brand)]

            # Разделяем ID на группы по 100 и записываем каждую группу в новый файл Excel и PDF
            ids = product_data['ID'].tolist()
            num_files = len(ids) // 100 + (1 if len(ids) % 100 > 0 else 0)
            for i in range(num_files):
                start_idx = i * 100
                end_idx = min((i + 1) * 100, len(ids))
                ids_subset = ids[start_idx:end_idx]
                if len(ids_subset) < 100:
                    # Создаем безопасное имя файла
                    safe_brand_name = safe_filename(brand)
                    output_pdf = os.path.join(seller_folder, f"{safe_brand_name}.pdf")
                    output_xlsx = os.path.join(seller_folder, f"{safe_brand_name}.xlsx")
                else:
                    safe_brand_name = safe_filename(brand)
                    output_pdf = os.path.join(seller_folder, f"{safe_brand_name}_{i + 1}.pdf")
                    output_xlsx = os.path.join(seller_folder, f"{safe_brand_name}_{i + 1}.xlsx")
                # Генерируем PDF файл для этой группы ID
                generate_pdf(product_data, output_pdf)

                # Сохраняем ID в Excel файл
                pd.DataFrame({'ID': ids_subset}).to_excel(output_xlsx, index=False)


def generate_pdf(data, output_file):
    # Регистрируем шрифт
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

    # Создаем PDF документ с альбомной ориентацией
    doc = SimpleDocTemplate(output_file, pagesize=letter)

    # Получаем стиль для текста
    style = ParagraphStyle(name='Normal', fontName='Arial', fontSize=10)

    # Создаем список для хранения параграфов
    paragraphs = []

    # Итерируемся по каждой строке данных
    for index, row in data.iterrows():
        # Создаем текст для текущего товара
        row_data = [f"<b>{column}:</b> {row[column]}" for column in data.columns]
        # Преобразуем список текстовых строк в одну строку с разделителем '<br/>'
        product_text = "<br/>".join(row_data)
        # Создаем параграф с текстом товара и добавляем его в список
        paragraphs.append(Paragraph(product_text, style))
        # Добавляем разделитель между товарами
        paragraphs.append(Paragraph("<br/><br/>" + "=" * 50 + "<br/><br/>", style))

    # Добавляем параграфы в документ
    doc.build(paragraphs)


# Пример использования функции
split_ids_by_seller_and_brand('items.xlsx', 'data')
