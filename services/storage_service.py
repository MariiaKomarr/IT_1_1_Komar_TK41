import json

from models.database import Database
from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType


class StorageService:

    @staticmethod
    def save(database: Database, file_path: str):
        data = {
            "name": database.name,
            "tables": []
        }

        for table in database.tables:
            table_data = {
                "name": table.name,
                "columns": [],
                "rows": []
            }

            for column in table.columns:
                table_data["columns"].append({
                    "name": column.name,
                    "data_type": column.datatype.value
                })

            for row in table.rows:
                table_data["rows"].append(row.values)

            data["tables"].append(table_data)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

    @staticmethod
    def load(file_path: str) -> Database:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        database = Database(data["name"])

        for table_data in data["tables"]:
            table = Table(table_data["name"])

            for column_data in table_data["columns"]:
                data_type = DataType(
                    column_data["data_type"]
                )

                table.add_column(
                    Column(
                        column_data["name"],
                        data_type
                    )
                )

            for row_data in table_data["rows"]:
                table.add_row(
                    Row(row_data)
                )

            database.add_table(table)

        return database