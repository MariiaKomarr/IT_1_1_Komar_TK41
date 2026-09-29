from services.validation_service import ValidationService


class Table:
    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Назва таблиці не може бути порожньою.")

        self.name = name.strip()
        self.columns = []
        self.rows = []

    def add_column(self, column):
        for existing_column in self.columns:
            if existing_column.name == column.name:
                raise ValueError(
                    f"Стовпець '{column.name}' вже існує."
                )

        self.columns.append(column)

    def delete_column(self, column_name: str):
        column = None

        for existing_column in self.columns:
            if existing_column.name == column_name:
                column = existing_column
                break

        if column is None:
            raise ValueError(
                f"Стовпець '{column_name}' не існує."
            )

        self.columns.remove(column)

        for row in self.rows:
            row.values.pop(column_name, None)

    def add_row(self, row):
        self._validate_row(row)
        self.rows.append(row)

    def update_row(self, index: int, row):
        if index < 0 or index >= len(self.rows):
            raise IndexError("Запис з таким індексом не існує.")

        self._validate_row(row)
        self.rows[index] = row

    def delete_row(self, index: int):
        if index < 0 or index >= len(self.rows):
            raise IndexError("Запис з таким індексом не існує.")

        self.rows.pop(index)

    def _validate_row(self, row):
        for column in self.columns:

            if column.name not in row.values:
                raise ValueError(
                    f"Відсутнє значення для стовпця "
                    f"'{column.name}'."
                )

            value = row.values[column.name]

            if not ValidationService.validate(
                value,
                column.datatype
            ):
                raise ValueError(
                    f"Некоректне значення '{value}' "
                    f"для стовпця '{column.name}' "
                    f"типу '{column.datatype.value}'."
                )

        column_names = {
            column.name for column in self.columns
        }

        for field_name in row.values:
            if field_name not in column_names:
                raise ValueError(
                    f"Стовпця '{field_name}' "
                    f"не існує в таблиці."
                )