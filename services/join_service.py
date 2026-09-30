from models.table import Table
from models.column import Column
from models.row import Row


class JoinService:

    @staticmethod
    def join(table1: Table, table2: Table, common_field: str) -> Table:

        column1 = JoinService._find_column(table1, common_field)

        column2 = JoinService._find_column(table2, common_field)

        if column1 is None or column2 is None:
            raise ValueError(
                f"Поле '{common_field}' повинно існувати в обох таблицях."
            )

        if column1.datatype != column2.datatype:
            raise ValueError(
                f"Типи поля '{common_field}' у таблицях не співпадають."
            )

        result = Table(
            f"{table1.name}_{table2.name}_join"
        )

        for column in table1.columns:
            result.add_column(
                Column(column.name, column.datatype)
            )

        for column in table2.columns:

            if column.name == common_field:
                continue

            new_name = column.name

            if JoinService._find_column(result, new_name) is not None:
                new_name = f"{table2.name}_{new_name}"

            result.add_column(
                Column(new_name, column.datatype)
            )

        for row1 in table1.rows:
            for row2 in table2.rows:

                if (
                    row1.values[common_field]
                    == row2.values[common_field]
                ):
                    values = dict(row1.values)

                    for column in table2.columns:

                        if column.name == common_field:
                            continue

                        new_name = column.name

                        if new_name in values:
                            new_name = f"{table2.name}_{new_name}"

                        values[new_name] = row2.values[column.name]

                    result.add_row(Row(values))

        return result

    @staticmethod
    def _find_column(table: Table, column_name: str):

        for column in table.columns:
            if column.name == column_name:
                return column

        return None