import json
import pandas as pd
import os

########################################
# Конфигурация (измените под себя)
########################################
EXCEL_FILE_PATH = 'source.xlsx'        # Путь к Excel-файлу
EXCEL_SHEET_NAME = 'Sheet1'            # Название листа Excel
EXCEL_COLUMN_FIO = 'ФИО'               # Имя столбца с ФИО
EXCEL_COLUMN_VISIBLE = 'VisibleFlag'   # Имя столбца с флагом (True/False)

JSON_SOURCE_PATH = 'data.json'         # Путь к входному JSON
JSON_OUTPUT_PATH = 'data_updated.json' # Путь к результату

# Если в JSON ключ, по которому лежит фамилия/ФИО,
# отличается от EXCEL_COLUMN_FIO (например, "surname"),
# пропишите здесь:
JSON_NAME_KEY = 'name'   # Как называется ключ с ФИО внутри JSON?

# Имя поля, которое надо обновить:
JSON_VISIBLE_KEY = 'visible'
########################################


def load_excel_data(excel_path, sheet_name, fio_column, visible_column):
    """
    Считывает Excel-файл, возвращает словарь {ФИО: True/False}.
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    # Убедимся, что в таблице есть нужные столбцы
    if fio_column not in df.columns or visible_column not in df.columns:
        raise ValueError(f"В Excel-листе '{sheet_name}' не найдены столбцы "
                         f"'{fio_column}' и/или '{visible_column}'")

    # Формируем словарь: ФИО -> Булево значение
    fio_to_visibility = {}
    for _, row in df.iterrows():
        name = str(row[fio_column]).strip()  # На всякий случай удаляем пробелы
        visibility_value = row[visible_column]
        # Для совместимости можно конвертировать строковые 'true'/'false'
        # если в Excel они не булевы, а текстовые
        if isinstance(visibility_value, str):
            visibility_value = visibility_value.strip().lower() in ['true', '1', 'да', 'yes']
        fio_to_visibility[name] = bool(visibility_value)

    return fio_to_visibility


def update_visibility_in_data(data, fio_map, json_name_key, json_visible_key):
    """
    Рекурсивно обходит объект data (список или словарь) и,
    если встречает ключ json_name_key со значением,
    присутствующим в fio_map, обновляет json_visible_key.
    """
    if isinstance(data, dict):
        # Если в словаре есть ключ с именем
        if json_name_key in data:
            name_value = str(data[json_name_key]).strip()
            if name_value in fio_map:
                data[json_visible_key] = fio_map[name_value]

        # Рекурсивно обходим остальные поля словаря
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                update_visibility_in_data(value, fio_map, json_name_key, json_visible_key)

    elif isinstance(data, list):
        # Для списка делаем обход каждого элемента
        for item in data:
            update_visibility_in_data(item, fio_map, json_name_key, json_visible_key)

    # Если это не список и не словарь, возвращать ничего не нужно
    # (базовый случай рекурсии)


def main():
    # 1. Загружаем данные из Excel
    fio_to_visibility_map = load_excel_data(
        EXCEL_FILE_PATH,
        EXCEL_SHEET_NAME,
        EXCEL_COLUMN_FIO,
        EXCEL_COLUMN_VISIBLE
    )

    # 2. Загружаем исходный JSON
    if not os.path.exists(JSON_SOURCE_PATH):
        raise FileNotFoundError(f"Не найден файл JSON: {JSON_SOURCE_PATH}")
    
    with open(JSON_SOURCE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Рекурсивно обновляем data
    update_visibility_in_data(data, fio_to_visibility_map, JSON_NAME_KEY, JSON_VISIBLE_KEY)

    # 4. Сохраняем результат в новый файл
    with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Файл {JSON_SOURCE_PATH} успешно обновлён и сохранён в {JSON_OUTPUT_PATH}")


if __name__ == '__main__':
    main()
