from models.database import Database
from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType

from services.join_service import JoinService

database = Database("Shop")

clients = Table("Clients")

clients.add_column(
    Column("client_id", DataType.INTEGER)
)

clients.add_column(
    Column("name", DataType.STRING)
)

clients.add_column(
    Column("birth_date", DataType.DATE)
)

clients.add_row(
    Row({
        "client_id": 1,
        "name": "Maria",
        "birth_date": "25.09.2003"
    })
)

clients.add_row(
    Row({
        "client_id": 2,
        "name": "Anna",
        "birth_date": "10.04.2002"
    })
)

clients.add_row(
    Row({
        "client_id": 3,
        "name": "Oleg",
        "birth_date": "15.01.2001"
    })
)

database.add_table(clients)

orders = Table("Orders")

orders.add_column(
    Column("client_id", DataType.INTEGER)
)

orders.add_column(
    Column("product", DataType.STRING)
)

orders.add_column(
    Column("price", DataType.REAL)
)

orders.add_row(
    Row({
        "client_id": 1,
        "product": "Phone",
        "price": 25000.0
    })
)

orders.add_row(
    Row({
        "client_id": 2,
        "product": "Laptop",
        "price": 45000.0
    })
)

orders.add_row(
    Row({
        "client_id": 4,
        "product": "Tablet",
        "price": 18000.0
    })
)

database.add_table(orders)

result = JoinService.join(
    clients,
    orders,
    "client_id"
)


print("\nРезультат JOIN:")
print("Таблиця:", result.name)

print("\nСтовпці:")

for column in result.columns:
    print(
        f"{column.name}: {column.datatype.value}"
    )

print("\nЗаписи:")

for row in result.rows:
    print(row.values)