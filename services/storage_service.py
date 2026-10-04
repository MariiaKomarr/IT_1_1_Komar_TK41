import json

from models.database import Database
from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType


class StorageService:


    @staticmethod
    def save(
        database: Database,
        file_path: str
    ):

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
                    "data_type": column.datatype.value,

                    # Обмеження стовпця
                    "unique": column.unique,
                    "required": column.required
                })


            for row in table.rows:

                table_data["rows"].append(
                    row.values
                )

            data["tables"].append(
                table_data
            )


        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )



    @staticmethod
    def load(
        file_path: str
    ) -> Database:


        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )


        database = Database(
            data["name"]
        )


        for table_data in data["tables"]:

            table = Table(
                table_data["name"]
            )


            for column_data in table_data["columns"]:

                datatype = DataType(
                    column_data["data_type"]
                )


                is_unique = column_data.get(
                    "unique",
                    False
                )

                is_required = column_data.get(
                    "required",
                    False
                )

                column = Column(
                    column_data["name"],
                    datatype,
                    unique=is_unique,
                    required=is_required
                )

                table.add_column(
                    column
                )


            for row_data in table_data["rows"]:

                row = Row(
                    row_data
                )

                table.add_row(
                    row
                )


            database.add_table(
                table
            )

        return database