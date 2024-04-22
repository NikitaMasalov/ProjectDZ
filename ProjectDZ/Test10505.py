import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import random
from reportlab.pdfgen import canvas

# Создание базы данных и таблиц
conn = sqlite3.connect('store.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS products
             (id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             manufacturer TEXT,
             price REAL,
             image TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders
             (id INTEGER PRIMARY KEY,
             customer_name TEXT,
             total_price REAL,
             status TEXT,
             pickup_point TEXT,
             code INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS order_items
             (id INTEGER PRIMARY KEY,
             order_id INTEGER,
             product_id INTEGER,
             quantity INTEGER,
             FOREIGN KEY (order_id) REFERENCES orders (id),
             FOREIGN KEY (product_id) REFERENCES products (id))''')

conn.commit()

# Функция для добавления товара в базу данных
def add_product(name, description, manufacturer, price, image):
    c.execute("INSERT INTO products (name, description, manufacturer, price, image) VALUES (?, ?, ?, ?, ?)",
              (name, description, manufacturer, price, image))
    conn.commit()

# Функция для получения списка товаров из базы данных
def get_products():
    c.execute("SELECT * FROM products")
    return c.fetchall()

# Функция для создания нового заказа
def create_order(customer_name, total_price, pickup_point):
    code = random.randint(100, 999)
    c.execute("INSERT INTO orders (customer_name, total_price, status, pickup_point, code) VALUES (?, ?, ?, ?, ?)",
              (customer_name, total_price, "new", pickup_point, code))
    order_id = c.lastrowid
    conn.commit()
    return order_id, code

# Функция для добавления товара в заказ
def add_order_item(order_id, product_id, quantity):
    c.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
              (order_id, product_id, quantity))
    conn.commit()

# Функция для получения информации о заказе
def get_order(order_id):
    c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = c.fetchone()

    c.execute("SELECT p.name, p.price, oi.quantity FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?",
              (order_id,))
    items = c.fetchall()

    return order, items

# Функция для обновления количества товара в заказе
def update_order_item_quantity(order_id, product_id, quantity):
    c.execute("UPDATE order_items SET quantity=? WHERE order_id=? AND product_id=?",
              (quantity, order_id, product_id))
    conn.commit()

# Функция для удаления товара из заказа
def remove_order_item(order_id, product_id):
    c.execute("DELETE FROM order_items WHERE order_id=? AND product_id=?",
              (order_id, product_id))
    conn.commit()

# Функция для создания PDF-талона заказа
def create_order_ticket(order_id, code, delivery_days):
    order, items = get_order(order_id)

    total_price = 0
    for item in items:
        total_price += item[1] * item[2]

    filename = filedialog.asksaveasfilename(defaultextension=".pdf")
    if filename:
        c = canvas.Canvas(filename)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Order Ticket")
        c.setFont("Helvetica", 12)
        c.drawString(100, 700, f"Date: {order[1]}")
        c.drawString(100, 675, f"Order ID: {order[0]}")
        c.drawString(100, 650, f"Total Price: {total_price}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 575, f"Code: {code}")
        c.setFont("Helvetica", 12)
        c.drawString(100, 550, f"Delivery Days: {delivery_days}")
        c.drawString(100, 520, f"Compound: {total_price}")
        c.showPage()
        c.save()

# Функция для отображения списка товаров
def show_products():
    products_window = tk.Toplevel(root)
    products_window.title("Product List")

    tree = ttk.Treeview(products_window, columns=("ID", "Name", "Description", "Manufacturer", "Price", "Image"))
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Description", text="Description")
    tree.heading("Manufacturer", text="Manufacturer")
    tree.heading("Price", text="Price")
    tree.heading("Image", text="Image")

    products = get_products()
    for product in products:
        tree.insert("", "end", values=product)

    tree.pack()

    def add_to_order(event):
        item = tree.selection()[0]
        product_id = tree.item(item, "values")[0]
        if "order_id" not in products_window.__dict__:
            products_window.order_id, code = create_order("Guest", 0, "")
        add_order_item(products_window.order_id, product_id, 1)
        view_order_button.config(state="normal")

    tree.bind("<Double-1>", add_to_order)

    view_order_button = ttk.Button(products_window, text="View Order", state="disabled", command=lambda: view_order(products_window.order_id))
    view_order_button.pack()

# Функция для отображения информации о заказе
def view_order(order_id):
    order_window = tk.Toplevel(root)
    order_window.title("Order Details")

    order, items = get_order(order_id)

    total_price = 0
    for item in items:
        total_price += item[1] * item[2]

    label = ttk.Label(order_window, text=f"Order ID: {order[0]}")
    label.pack()

    label = ttk.Label(order_window, text=f"Customer Name: {order[1]}")
    label.pack()

    label = ttk.Label(order_window, text=f"Total Price: {total_price}")
    label.pack()

    label = ttk.Label(order_window, text=f"Status: {order[3]}")
    label.pack()

    label = ttk.Label(order_window, text=f"Code: {order[5]}")
    label.pack()

    tree = ttk.Treeview(order_window, columns=("Name", "Price", "Quantity"))
    tree.heading("Name", text="Name")
    tree.heading("Price", text="Price")
    tree.heading("Quantity", text="Quantity")

    for item in items:
        tree.insert("", "end", values=item)

    tree.pack()

    def update_quantity(event):
        item = tree.selection()[0]
        product_name = tree.item(item, "values")[0]
        quantity = simpledialog.askinteger("Update Quantity", f"Enter new quantity for {product_name}:")
        if quantity is not None:
            if quantity == 0:
                remove_order_item(order_id, product_id)
            else:
                update_order_item_quantity(order_id, product_id, quantity)
            view_order(order_id)

    tree.bind("<Double-1>", update_quantity)

    pickup_points = ["Point 1", "Point 2", "Point 3"]
    pickup_var = tk.StringVar(order_window)
    pickup_var.set(order[4])
    pickup_menu = ttk.OptionMenu(order_window, pickup_var, order[4], *pickup_points)
    pickup_menu.pack()

    def save_order_ticket():
        in_stock_count = sum(1 for item in items if item[2] > 0)
        delivery_days = 3 if in_stock_count >= 3 else 6
        create_order_ticket(order_id, order[5], delivery_days)

    save_button = ttk.Button(order_window, text="Save Order Ticket", command=save_order_ticket)
    save_button.pack()

# Создание главного окна
root = tk.Tk()
root.title("Store Management System")

# Кнопка для просмотра списка товаров
products_button = ttk.Button(root, text="View Products", command=show_products)
products_button.pack()

root.mainloop()