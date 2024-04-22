import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('store.db')
cursor = conn.cursor()

# Пример добавления нескольких товаров в базу данных
products_data = [
    (1, 'Ноутбук', 'Мощный ноутбук для работы и игр', 'Производитель A', 1200.0, 'photo1.jpg'),
    (2, 'Смартфон', 'Современный смартфон с камерой 64 МП', 'Производитель B', 800.0, 'photo1.jpg'),
    (3, 'Планшет', 'Легкий и компактный планшет для чтения и развлечений', 'Производитель C', 500.0, 'photo1.jpg')
]

# SQL запрос для добавления товаров в базу данных
for product in products_data:
    cursor.execute('''
        INSERT INTO products (id, name, description, manufacturer, price, image)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', product)

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()

print('Товары успешно добавлены в базу данных.')