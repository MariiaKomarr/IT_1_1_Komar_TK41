from models.database import Database
from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType

from services.storage_service import StorageService


def test_save_and_load(tmp_path):
    database = Database("TestDB")

    table = Table("Clients")
    table.add_column(
        Column("id", DataType.INTEGER)
    )

    table.add_row(
        Row({"id": 1})
    )

    database.add_table(table)

    file_path = tmp_path / "database.json"

    StorageService.save(
        database,
        str(file_path)
    )

    loaded_database = StorageService.load(
        str(file_path)
    )

    assert loaded_database.name == "TestDB"
    assert len(loaded_database.tables) == 1
    assert loaded_database.tables[0].name == "Clients"
    assert loaded_database.tables[0].rows[0].values["id"] == 1