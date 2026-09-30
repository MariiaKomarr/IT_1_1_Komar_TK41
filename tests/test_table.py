import pytest

from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType


def test_add_valid_row():
    table = Table("Clients")

    table.add_column(
        Column("id", DataType.INTEGER)
    )

    table.add_column(
        Column("name", DataType.STRING)
    )

    table.add_row(
        Row({
            "id": 1,
            "name": "Maria"
        })
    )

    assert len(table.rows) == 1
    assert table.rows[0].values["name"] == "Maria"


def test_invalid_row():
    table = Table("Clients")

    table.add_column(
        Column("id", DataType.INTEGER)
    )

    with pytest.raises(ValueError):
        table.add_row(
            Row({
                "id": "not integer"
            })
        )