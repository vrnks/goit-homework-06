import shutil
import re
import os
from pathlib import Path
import sys
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
    
    for root, _, files in os.walk(folder_path):  # Використовуємо os.walk() для рекурсивного проходження по всіх вкладених папках
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                # Знаходимо папку для відповідного формату або використовуємо 'unknown', якщо формат не відомий
                target_folder = 'unknown'
                for folder, extensions in file_formats.items():
                    if any(file_path.endswith(extension) for extension in extensions):
                        target_folder = folder
                        break
                # Створюємо відповідну папку, якщо вона ще не існує у папці, що передана на сортування
                target_folder_path = os.path.join(os.path.dirname(folder_path), target_folder)
                # Перевіряємо, чи target_folder_path не виходить за межі folder_path
                if not target_folder_path.startswith(folder_path):
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
    # Виведення списку файлів в кожній категорії
    print_file_lists(folder_path, file_formats)
 

def process_files_in_folder(folder_path):
    """Рекурсивна функція для обробки всіх файлів та папок всередині даної папки"""
    # Отримуємо список файлів та папок у заданій директорії
    contents = os.listdir(folder_path)
    # Перебираємо файли та папки
    for item in contents:
        item_path = os.path.join(folder_path, item)
        # Якщо елемент є файлом, обробляємо його за допомогою process_file()
        if os.path.isfile(item_path):
            process_file(folder_path)
        # Якщо елемент є папкою
        elif os.path.isdir(item_path):
            if item not in ['archives', 'video', 'audio', 'documents', 'images', 'unknown']:
            # Рекурсивно обробляємо папку
                process_files_in_folder(item_path)
                if not os.listdir(item_path):
                    os.rmdir(item_path)
                    
def print_file_lists(folder_path, file_formats):
    """Функція для виведення списку файлів в кожній категорії"""
    known_extensions = set()
    unknown_extensions = set()

    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                for folder, extensions in file_formats.items():
                    if any(file_path.endswith(extension) for extension in extensions):
                        # Виведення файлів в кожній категорії
                        print(f"Категорія '{folder}': {filename}")
                        # Збираємо відомі розширення
                        known_extensions.add(os.path.splitext(filename)[1])
                        break
                else:
                    # Виведення файлів з невідомими розширеннями
                    print(f"Невідома категорія: {filename}")
                    unknown_extensions.add(os.path.splitext(filename)[1])

    # Виведення переліку усіх відомих розширень
    print("\nПерелік відомих розширень:")
    for extension in known_extensions:
        print(extension)

    # Виведення переліку всіх невідомих розширень
    print("\nПерелік невідомих розширень:")
    for extension in unknown_extensions:
        print(extension)

def main():
    # Отримуємо шлях до папки, яка передається на сортування
    folder_path = sys.argv[1]
    # Перевіряємо, чи існує папка
    if not os.path.exists(folder_path):
        print(f"Шлях '{folder_path}' не існує.")
        return
    # Обробляємо файли та папки у вказаній директорії
    process_files_in_folder(folder_path)
    return 'Виконано успішно.'

if __name__ == "__main__":
    print(main())