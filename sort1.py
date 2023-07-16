import shutil
import re
import os
from os import path
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()     
def translate(name):
    new_name = name.translate(TRANS)
    return new_name

def normalize(name):
    """Функція для нормалізації імен файлів та папок"""
    normalized_name = ''
    # Транслітерація
    normalized_name = name.translate(TRANS)
    # Замінюємо всі символи, що не є латинськими або цифрами на "_"
    normalized_name = re.sub(r"[^A-Za-z0-9.]", "_", normalized_name)
    # Замінюємо всі крапки, окрім останньої, на "_"
    normalized_name = re.sub(r"\.(?=[^.]*\.)", "_", normalized_name)
    return normalized_name


def process_file(folder_path):
    """Функція для нобробки формату файлів"""
    # Створення словника, де ключ - це формат файлу, а значення - це відповідна папка
    file_formats = {
        'archives': ('zip', 'gz', 'tar'),
        'video': ('avi', 'mp4', 'mov', 'mkv'),
        'audio': ('mp3', 'ogg', 'wav', 'amr'),
        'documents': ('doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'),
        'images': ('jpeg', 'png', 'jpg', 'svg'),
    }

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            # Знаходимо папку для відповідного формату або використовуємо 'unknown', якщо формат не відомий
            target_folder = 'unknown'
            for folder, extensions in file_formats.items():
                if any(file_path.endswith(extension) for extension in extensions):
                    target_folder = folder
                    break
            # Створюємо відповідну папку, якщо вона ще не існує
            target_folder_path = os.path.join(folder_path, target_folder)
            if not os.path.exists(target_folder_path):
                os.makedirs(target_folder_path)
            # Оновлюємо назву файлу
            if target_folder != 'unknown':
                normalized_filename = normalize(filename)
            else:
                normalized_filename = filename
            # Якщо файл є архівом, розархівувати його
            if target_folder == 'archives':
                # Створюємо підпапку з такою самою назвою, як архів, у папці 'archives'
                archive_folder_name = os.path.splitext(normalized_filename)[0]
                archive_folder_path = os.path.join(target_folder_path, archive_folder_name)
                if not os.path.exists(archive_folder_path):
                    os.makedirs(archive_folder_path)
                # Розархівуємо архів в підпапку
                shutil.unpack_archive(file_path, archive_folder_path)
                os.remove(file_path)  # Видалення архіву після розархівування
            else:
                # Переміщуємо файл в папку з відповідним форматом з оновленою назвою
                shutil.move(file_path, os.path.join(target_folder_path, normalized_filename))
 

def process_files_in_folder(folder_path):
    """Рекурсивна Функція"""
    # Отримуємо список файлів та папок у заданій директорії
    contents = os.listdir(folder_path)
    # Перебираємо файли та папки
    for item in contents:
        item_path = os.path.join(folder_path, item)
        # Якщо елемент є файлом, обробляємо його за допомогою process_file()
        if os.path.isfile(item_path):
            process_file(folder_path)
        # Якщо елемент є папкою і не є папкою archives, video, audio, documents, images, unknown
        elif os.path.isdir(item_path) and item not in ['archives', 'video', 'audio', 'documents', 'images', 'unknown']:
            # Обробляємо назву папки за допомогою normalize()
            normalized_folder_name = normalize(item)
            # Перейменовуємо папку на оновлену назву
            new_folder_path = os.path.join(folder_path, normalized_folder_name)
            os.rename(item_path, new_folder_path)
            # Рекурсивно обробляємо папку
            process_files_in_folder(new_folder_path)
            # Видаляємо порожні папки
            if not os.listdir(new_folder_path):
                os.rmdir(new_folder_path)

