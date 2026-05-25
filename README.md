# PC Hardware & Peripherals Store

Member 2 implementation for the Database and Cloud Security assignment.

## Stack

- Python Flask web application
- Microsoft SQL Server Express
- `pyodbc` database connector
- HTML/CSS templates for screenshot-friendly CRUD testing

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create the database and seed data:

```powershell
python scripts\setup_database.py
```

Alternatively, open SQL Server Management Studio, connect to `localhost\SQLEXPRESS`, run `database/schema.sql`, then run `database/seed.sql`.

4. Confirm the database connection:

```powershell
python scripts\check_connection.py
```

5. Start the Flask app:

```powershell
python app.py
```

For a screenshot-friendly server without the debug reloader, you can also use:

```powershell
python run_server.py
```

6. Open the local URL shown in the terminal, usually:

```text
http://127.0.0.1:5050
```

## Functionality To Screenshot

- SQL Server database and tables.
- Flask app running in the terminal.
- Product list before testing.
- Insert a new product.
- Product appears in the table.
- Delete an old product.
- Product disappears from the table.
- Insert another new product.
- Create a customer order.
- Order appears in order history.

## Security Features Used By The App

- Parameterized SQL queries using `?` placeholders in `pyodbc`.
- Table constraints for prices, stock, quantities, roles, and foreign keys.
- Password hashes stored in the `Users` table seed data instead of plaintext.
- MSSQL transaction used during order creation to keep stock and order data consistent.
- Product deletion blocked when a product already has order history.
