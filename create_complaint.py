import datetime
import os
import time
from playwright.sync_api import sync_playwright

# Путь к папке с текстовыми файлами
folder_path = '/home/o4kapuk/PycharmProjects/parser_WB/data'


# Функция для обхода файлов в папках
def process_files_in_folder(folder_path, extensions):
    for root, dirs, files in os.walk(folder_path):
        for file_name in sorted(files):
            if file_name.endswith(extensions):
                file_path = os.path.join(root, file_name)
                yield file_path


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://seller.wildberries.ru/appeal-copyright/')
    # Проходим по каждому файлу с расширением .xlsx и .pdf и загружаем их на сайт
    for xlsx_file_path, pdf_file_path in zip(
            process_files_in_folder(folder_path, '.xlsx'),
            process_files_in_folder(folder_path, '.pdf')
    ):
        try:

            # Загрузка файла .xlsx
            page.set_input_files('input[id="article_file"]', xlsx_file_path)
            page.wait_for_timeout(1000)
            # Загрузка файла .pdf
            page.set_input_files('//input[@id="file_2"]', pdf_file_path)
            page.wait_for_timeout(1000)
            # Нажимаем на выпадающее меню "Жалоба на нарушение"
            get_violation = page.query_selector('//input[@id="category_id"]')
            get_violation.click()
            page.wait_for_timeout(1000)
            # Нажимаем на выпадающем меню "Товарного знака, наименования бренда"
            page.click('xpath=//button[contains(text(), "Товарного знака, наименования бренда")]')
            page.wait_for_timeout(1000)
            # Нажимаем на выпадающее меню "Суть жалобы"
            get_violation = page.query_selector('//input[@id="theme_id"]')
            get_violation.click()
            page.wait_for_timeout(1000)
            # Нажимаем на выпадающем меню "На товаре или упаковке используется сходное обозначение"
            page.click('xpath=//button[contains(text(), "На товаре или упаковке используется сходное обозначение")]')
            page.wait_for_timeout(1000)
            # Контактная информация
            # Выбор Я правообладатель или Я представитель правообладателя
            check_box = page.query_selector('(//label[@data-name="Checkbox"])[2]')
            check_box.click()
            page.wait_for_timeout(1000)
            registration_number = page.query_selector('//input[@id="oip_id"]')
            registration_number.fill('945815')
            page.wait_for_timeout(1000)
            # Поиск всех элементов <span> с атрибутом data-name="Text"
            all_text_spans = page.query_selector_all('span[data-name="Text"]')

            # Проверка текстового содержимого элементов <span>
            for span in all_text_spans:
                if span.inner_text() == 'Если номер не найден в базе ФИПС или зарегистрирован в ВОИС, отметьте графу ниже и укажите его номер':
                    page.wait_for_timeout(1000)
                    # Если текст найден, нажимаем на чекбокс "International Trade Mark"
                    page.click('input[id="internationalOip-input"]')
                    break  # Прерываем цикл, чтобы избежать лишних действий

            # Название компании (правообладателя)
            page.fill('//input[@id="cro_company"]', 'МБА ПЕРФЮМЕС МАНУФАКТУРИНГ ЛЛК')
            page.wait_for_timeout(1000)
            # Название бренда
            page.fill('//input[@id="cro_brand"]', 'Attar Collection')
            page.wait_for_timeout(1000)
            # ФИО обращающегося
            page.fill('//input[@id="cro_fio"]', 'Зарипов Тимур Фаритович')
            page.wait_for_timeout(1000)
            # E-mail
            page.fill('//input[@id="cro_email"]', 'zaripovtf@gmail.com')
            page.wait_for_timeout(1000)
            # Телефон
            page.fill('//input[@id="cro_phone"]', '89854112714')
            page.wait_for_timeout(1000)
            # Документы
            # Подтверждение вашего права
            page.set_input_files('//input[@id="file_1"]', '/home/o4kapuk/Downloads/1 вкл в свидетельство 945815.pdf')
            page.wait_for_timeout(1000)
            # Текст жалобы
            page.set_input_files('//input[@id="file_3"]', '/home/o4kapuk/Downloads/новый_требование-WB.pdf')
            page.wait_for_timeout(1000)
            # Полномочия
            page.set_input_files('//input[@id="file_4"]', '/home/o4kapuk/Downloads/22 ДОВЕРЕННОСТЬ.pdf')
            page.wait_for_timeout(1000)
            # С правилами оформления претензий ознакомлен(а) //input[@name="rules_accepted"]
            check_box_accept = page.query_selector('//input[@name="rules_accepted"]')
            check_box_accept.click()
            page.wait_for_timeout(7000)

            # Нажатие на кнопку "Загрузить"
            page.wait_for_selector('//button[@type="submit"]')
            page.click('//button[@type="submit"]')
            page.wait_for_selector('//div[@class="e8d21a"]')
            text_answer = page.query_selector('//div[@class="e8d21a"]').inner_text()
            with open('text_answer.txt', 'a', encoding='utf-8') as file:
                file.write(
                    text_answer + '\n' + f'Продавец: {xlsx_file_path.split("/")[-2]}' + '\n' + f'Бренд: {xlsx_file_path.split("/")[-1].replace(".xlsx", "")}' + '\n' + f"Дата отправки обращения: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}" + '\n' + '\n')

            page.wait_for_selector('//button[@class="ca6fba ac246d b03ef7"]')
            page.click('//button[@class="ca6fba ac246d b03ef7"]')
        except Exception as ex:
            page.reload()
