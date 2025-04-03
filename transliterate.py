import pyodbc
from transliterate import translit
import json
import os

# Путь к файлу, где будет сохраняться отображение старое->новое имя
mapping_file = "data.json"

# Если файл существует, загружаем его содержимое, иначе создаём пустой словарь
if os.path.exists(mapping_file):
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping_dict = json.load(f)
else:
    mapping_dict = {}

# Параметры подключения – замените на свои данные
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=YOUR_SERVER_NAME;"
    "Database=YOUR_DATABASE_NAME;"
    "UID=YOUR_USERNAME;"
    "PWD=YOUR_PASSWORD;"
)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
except Exception as e:
    print("Ошибка подключения к БД:", e)
    exit(1)

# Получаем список пользователей
select_query = "SELECT id, username FROM Users"
try:
    cursor.execute(select_query)
    rows = cursor.fetchall()
except Exception as e:
    print("Ошибка выполнения запроса SELECT:", e)
    conn.close()
    exit(1)

for row in rows:
    user_id = row.id
    username = row.username

    try:
        # Выполняем транслитерацию с русского на английский
        new_username = translit(username, 'ru', reversed=True)
    except Exception as e:
        print(f"Ошибка транслитерации для пользователя {username}: {e}")
        continue

    # Если новое имя начинается с буквы 'R' (без учёта регистра) — пропускаем обновление
    if new_username and new_username[0].upper() == 'R':
        print(f"Пропускаем пользователя {username}: транслитерация {new_username} начинается с 'R'")
        continue

    try:
        # Начинаем транзакцию для обновления в нескольких таблицах
        update_query_users = "UPDATE Users SET username = ? WHERE id = ?"
        cursor.execute(update_query_users, new_username, user_id)

        update_query_orders = "UPDATE Orders SET username = ? WHERE user_id = ?"
        cursor.execute(update_query_orders, new_username, user_id)

        # Фиксируем транзакцию
        conn.commit()
        print(f"Обновлен username для пользователя с id {user_id}: {username} -> {new_username}")

        # Обновляем отображение в словаре (старое имя -> новое имя)
        mapping_dict[username] = new_username

        # Сохраняем обновлённый словарь в data.json
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(mapping_dict, f, ensure_ascii=False, indent=4)

    except Exception as e:
        conn.rollback()
        print(f"Ошибка обновления для пользователя с id {user_id}: {e}")

cursor.close()
conn.close()
