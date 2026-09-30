from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType

from services.join_service import JoinService


def test_join_tables():
    clients = Table("Clients")

    clients.add_column(
        Column("client_id", DataType.INTEGER)
    )
    clients.add_column(
        Column("name", DataType.STRING)
    )

    clients.add_row(
        Row({
            "client_id": 1,
            "name": "Maria"
        })
    )

    clients.add_row(
        Row({
            "client_id": 2,
            "name": "Anna"
        })
    )

    orders = Table("Orders")

    orders.add_column(
        Column("client_id", DataType.INTEGER)
    )
    orders.add_column(
        Column("product", DataType.STRING)
    )

    orders.add_row(
        Row({
            "client_id": 1,
            "product": "Phone"
        })
    )

    orders.add_row(
        Row({
            "client_id": 3,
            "product": "Tablet"
        })
    )

    result = JoinService.join(
        clients,
        orders,
        "client_id"
    )

    assert len(result.rows) == 1

    assert result.rows[0].values == {
        "client_id": 1,
        "name": "Maria",
        "product": "Phone"
    }