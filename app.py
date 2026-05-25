import os
from decimal import Decimal, InvalidOperation

import pyodbc
from flask import Flask, flash, redirect, render_template, request, url_for


DEFAULT_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    "DATABASE=HardwareStoreDB;"
    "Trusted_Connection=yes;"
    "Encrypt=no"
)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


def get_connection():
    connection_string = os.environ.get(
        "HARDWARE_STORE_CONNECTION_STRING",
        DEFAULT_CONNECTION_STRING,
    )
    return pyodbc.connect(connection_string)


def fetch_products():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ProductID, ProductName, Category, Price, StockQuantity
            FROM dbo.Products
            ORDER BY ProductID DESC
            """
        )
        return cursor.fetchall()


def fetch_customers():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT UserID, Username, Email
            FROM dbo.Users
            WHERE Role = ?
            ORDER BY Username
            """,
            "Customer",
        )
        return cursor.fetchall()


@app.route("/")
def index():
    return render_template("products.html", products=fetch_products())


@app.post("/products")
def add_product():
    name = request.form.get("product_name", "").strip()
    category = request.form.get("category", "").strip()
    price_raw = request.form.get("price", "").strip()
    stock_raw = request.form.get("stock_quantity", "").strip()

    if not name or not category:
        flash("Product name and category are required.", "error")
        return redirect(url_for("index"))

    try:
        price = Decimal(price_raw)
        stock_quantity = int(stock_raw)
    except (InvalidOperation, ValueError):
        flash("Price and stock quantity must be valid numbers.", "error")
        return redirect(url_for("index"))

    if price < 0 or stock_quantity < 0:
        flash("Price and stock quantity cannot be negative.", "error")
        return redirect(url_for("index"))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO dbo.Products (ProductName, Category, Price, StockQuantity)
            VALUES (?, ?, ?, ?)
            """,
            name,
            category,
            price,
            stock_quantity,
        )
        conn.commit()

    flash("Product added to inventory.", "success")
    return redirect(url_for("index"))


@app.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.Order_Details
            WHERE ProductID = ?
            """,
            product_id,
        )
        linked_order_count = cursor.fetchone()[0]

        if linked_order_count:
            flash("This product is linked to existing orders and cannot be removed.", "error")
            return redirect(url_for("index"))

        cursor.execute("DELETE FROM dbo.Products WHERE ProductID = ?", product_id)
        conn.commit()

    flash("Product removed from inventory.", "success")
    return redirect(url_for("index"))


@app.route("/orders")
def orders():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                o.OrderID,
                u.Username,
                u.Email,
                o.OrderDate,
                o.TotalAmount,
                p.ProductName,
                od.Quantity,
                od.SubtotalPrice
            FROM dbo.Orders o
            INNER JOIN dbo.Users u ON o.UserID = u.UserID
            INNER JOIN dbo.Order_Details od ON o.OrderID = od.OrderID
            INNER JOIN dbo.Products p ON od.ProductID = p.ProductID
            ORDER BY o.OrderID DESC
            """
        )
        order_rows = cursor.fetchall()

    return render_template(
        "orders.html",
        orders=order_rows,
        products=fetch_products(),
        customers=fetch_customers(),
    )


@app.post("/orders")
def create_order():
    try:
        user_id = int(request.form.get("user_id", ""))
        product_id = int(request.form.get("product_id", ""))
        quantity = int(request.form.get("quantity", ""))
    except ValueError:
        flash("Customer, product, and quantity are required.", "error")
        return redirect(url_for("orders"))

    if quantity <= 0:
        flash("Quantity must be greater than zero.", "error")
        return redirect(url_for("orders"))

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT Price, StockQuantity
                FROM dbo.Products WITH (UPDLOCK)
                WHERE ProductID = ?
                """,
                product_id,
            )
            product = cursor.fetchone()

            if not product:
                flash("Selected product is no longer available.", "error")
                return redirect(url_for("orders"))

            price = Decimal(product.Price)
            stock_quantity = int(product.StockQuantity)

            if stock_quantity < quantity:
                flash("Not enough stock is available for this order.", "error")
                return redirect(url_for("orders"))

            subtotal = price * quantity

            cursor.execute(
                """
                INSERT INTO dbo.Orders (UserID, TotalAmount)
                OUTPUT INSERTED.OrderID
                VALUES (?, ?)
                """,
                user_id,
                subtotal,
            )
            order_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO dbo.Order_Details
                    (OrderID, ProductID, Quantity, SubtotalPrice)
                VALUES (?, ?, ?, ?)
                """,
                order_id,
                product_id,
                quantity,
                subtotal,
            )

            cursor.execute(
                """
                UPDATE dbo.Products
                SET StockQuantity = StockQuantity - ?
                WHERE ProductID = ?
                """,
                quantity,
                product_id,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    flash("Order created successfully and inventory was updated.", "success")
    return redirect(url_for("orders"))


if __name__ == "__main__":
    app.run(debug=True)
