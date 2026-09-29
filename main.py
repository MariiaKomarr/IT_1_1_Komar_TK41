from models.database import Database
from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType


database = Database("Shop")

clients = Table("Clients")

clients.add_column(
    Column("id", DataType.INTEGER)
)

clients.add_column(
    Column("name", DataType.STRING)
)

clients.add_column(
    Column("birth_date", DataType.DATE)
)

clients.add_column(
    Column("active_period", DataType.DATE_INV)
)

clients.add_row(
    Row({
        "id": 1,
        "name": "Maria",
        "birth_date": "25.09.2003",
        "active_period": "01.09.2026 - 30.09.2026"
    })
)

database.add_table(clients)


print("База:", database.name)

for table in database.tables:
    print("\nТаблиця:", table.name)

    for column in table.columns:
        print(
            f"{column.name}: {column.datatype.value}"
        )

    for row in table.rows:
        print(row.values)