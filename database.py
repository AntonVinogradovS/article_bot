import sqlite3

async def create_database():
    conn = sqlite3.connect('products_database.db')
    cursor = conn.cursor()

    # Создание таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photos TEXT,
            name TEXT,
            article TEXT
        )
    ''')

    conn.commit()
    conn.close()

async def insert_product(photos, name, article):
    conn = sqlite3.connect('products_database.db')
    cursor = conn.cursor()

    # Вставка данных в таблицу
    cursor.execute('''
        INSERT INTO products (photos, name, article)
        VALUES (?, ?, ?)
    ''', (photos, name, article))

    conn.commit()
    conn.close()

async def delete_product(article):
    conn = sqlite3.connect('products_database.db')
    cursor = conn.cursor()

    # Удаление записи по артикулу
    cursor.execute('''
        DELETE FROM products
        WHERE article = ?
    ''', (article,))

    conn.commit()
    conn.close()

async def find_product_by_article(article):
    conn = sqlite3.connect('products_database.db')
    cursor = conn.cursor()

    # Поиск записи по артикулу
    cursor.execute('''
        SELECT * FROM products 
        WHERE article = ?
    ''', (article,))

    product = cursor.fetchone()

    conn.close()
    if product != None:
        return list(product)
    else:
        return 1
    

async def update_product_by_article(id, article, new_photos, new_name):
    conn = sqlite3.connect('products_database.db')
    cursor = conn.cursor()

    # Изменение записи по артикулу
    cursor.execute('''
        UPDATE products
        SET photos = ?, name = ?, article = ?
        WHERE id = ?
    ''', (new_photos, new_name, article, id))

    conn.commit()
    conn.close()

async def create_excel_from_database():
    # Подключение к базе данных
    conn = sqlite3.connect('products_database.db')
    cursor = conn.cursor()

    # Получение данных из таблицы
    cursor.execute('SELECT * FROM products')
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return data

async def search_product_by_article_or_name(article_or_name):
    # Connect to the SQLite database
    connection = sqlite3.connect('products_database.db')
    cursor = connection.cursor()

    # Search by article
    cursor.execute("SELECT * FROM products WHERE article = ?", (article_or_name,))
    product_by_article = cursor.fetchone()

    if product_by_article:
        connection.close()
        return product_by_article

    # If not found, search by name
    cursor.execute("SELECT * FROM products WHERE name = ?", (article_or_name,))
    product_by_name = cursor.fetchone()

    if product_by_name:
        connection.close()
        return product_by_name
    connection.close()
    return 1

    

    return product_by_name
