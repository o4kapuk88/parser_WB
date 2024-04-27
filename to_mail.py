import shutil
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import zipfile


def zip_folder(folder_path, output_zip, max_size_mb=10):
    current_zip_index = 1
    current_zip_path = f"{output_zip[:-4]}_{current_zip_index}.zip"
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        current_size = 0
        names = set()
        file_exists = False
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.pdf'):
                    file_exists = True
                    file_path = os.path.join(root, file)
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if current_size + file_size_mb > max_size_mb:
                        zip_file.close()
                        current_zip_index += 1
                        current_zip_path = f"{output_zip[:-4]}_{current_zip_index}.zip"
                        zip_file = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
                        current_size = 0
                        names.clear()
                    base_name = os.path.basename(file)
                    name, ext = os.path.splitext(base_name)
                    count = 1
                    new_name = base_name
                    while new_name in names:
                        new_name = f'{name}_{count}{ext}'
                        count += 1
                    names.add(new_name)
                    zip_file.write(file_path, os.path.relpath(file_path, folder_path))
                    current_size += file_size_mb
        if not file_exists:
            os.remove(current_zip_path)


def split_file(input_file, chunk_size):
    part_number = 1
    with open(input_file, 'rb') as f_in:
        while True:
            chunk = f_in.read(chunk_size)
            if not chunk:
                break
            output_file = f"{input_file[:-4]}_{part_number}.zip"
            with open(output_file, 'wb') as f_out:
                f_out.write(chunk)
            part_number += 1


def send_email(sender_email, receiver_email, subject, message, attachment_paths, smtp_server,
               smtp_port, smtp_username, smtp_password):
    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    for attachment_path in attachment_paths:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()  # Пример использования функций для отправки email


sender_email = 'protivwb@mail.ru'
receiver_email = 'zaripovtf@gmail.com'
subject = 'Архив с PDF файлами и другими файлами'
message = 'Архив с PDF файлами и другими файлами'
smtp_server = 'smtp.mail.ru'
smtp_port = 465  # Порт SMTP сервера для защищенного соединения
smtp_username = 'protivwb@mail.ru'
smtp_password = 'crtzcTB0BapmS6KvZLLv'  # Используйте специальный пароль для внешнего приложения

folder_path = '/home/o4kapuk/PycharmProjects/parser_WB/data'
output_zip = 'data.zip'
zip_folder(folder_path, output_zip)

temp_folder = '/home/o4kapuk/PycharmProjects/parser_WB/temp'
os.makedirs(temp_folder, exist_ok=True)
split_file(output_zip, 10 * 1024 * 1024)


for root, dirs, files in os.walk(temp_folder):
    for file in files:
        if file.endswith('.zip'):
            attachment_path = os.path.join(root, file)
            send_email(sender_email, receiver_email, subject, message, attachment_path, smtp_server, smtp_port,)

attachment_paths = ['text_answer.txt', 'новый_требование WB.docx', 'mail.txt']
send_email(sender_email, receiver_email, subject, message, attachment_paths, smtp_server, smtp_port, smtp_username,
           smtp_password)


shutil.rmtree(temp_folder)
