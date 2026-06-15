import json
import random
import sqlite3 as sql
from pathlib import Path

import httpx


def random_users(n: int, seed: int):
    response = httpx.get(f"https://randomuser.me/api/?results={n}&nat=gb&seed={seed}")
    return response.json().get("results")


def create_schema(cursor):
    schema = Path("assets/schema.sql").read_text()
    cursor.executescript(schema)


def load_customers(cursor):
    rusers = random_users(1000, 59)
    customers = list(
        map(
            lambda u: (
                u.get("login").get("uuid"),
                u.get("name").get("first"),
                u.get("name").get("last"),
                u.get("dob").get("date"),
            ),
            rusers,
        )
    )
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", list(customers))
    return list(customers)


def load_employee(cursor):
    rusers = random_users(1000, 69)
    employees = list(
        map(
            lambda u: (
                u.get("login").get("uuid"),
                u.get("name").get("first"),
                u.get("name").get("last"),
                u.get("dob").get("date"),
            ),
            rusers,
        )
    )
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", employees)
    return employees


def random_date():
    year = random.randint(1980, 2022)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month}-{day}"


def load_orders(cursor, customers, employees, products):
    n = 10000
    orders = []
    order_items = []
    for order_id in range(n):
        customer = customers[random.randint(0, len(customers) - 1)]
        employee = employees[random.randint(0, len(employees) - 1)]
        orders.append(
            (
                order_id,
                customer[0],
                employee[0],
                random_date(),
            )
        )
        n_products = random.randint(1, 3)
        for i in random.sample(range(0, len(products)-1), n_products):
            order_items.append(
                (
                    order_id,
                    products[i][0],
                    random.randint(1, 10),
                    products[i][3],
                )
            )

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", list(orders))
    cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", order_items)
    return orders

def load_products(cursor):
    text = Path("assets/products.json").read_text()
    rproducts = json.loads(text)
    products = list(
        map(
            lambda p: (
                int(p.get("UPC")),
                p.get("Name"),
                p.get("Category"),
                float(p.get("Price")),
            ),
            rproducts,
        )
    )
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    return products


def main():
    conn = sql.connect("falcon.sqlite")
    cursor = conn.cursor()
    create_schema(cursor)
    products = load_products(cursor)
    customers = load_customers(cursor)
    employees = load_employee(cursor)
    orders = load_orders(cursor, customers, employees, products)
    print(
        "Products: %i\nCustomer: %i\nEmployees: %i\nOrders: %i"
        % (len(products), len(customers), len(employees), len(orders))
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
