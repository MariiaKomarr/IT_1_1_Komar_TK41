from services.validation_service import ValidationService


class Table:

    def __init__(self, name: str):

        if not name or not name.strip():
            raise ValueError(
                "Назва таблиці не може бути порожньою."
            )

        self.name = name.strip()
        self.columns = []
        self.rows = []

    def add_column(self, column):

        # Перевірка дублювання назви
        for existing_column in self.columns:

            if (
                existing_column.name.lower()
                == column.name.lower()
            ):
                raise ValueError(
                    f"Стовпець '{column.name}' вже існує."
                )

        if column.required and self.rows:

            raise ValueError(
                f"Неможливо додати обов'язковий стовпець "
                f"'{column.name}' до таблиці, яка вже "
                f"містить записи.\n\n"
                f"Спочатку додайте його як необов'язковий, "
                f"заповніть значення, а потім увімкніть "
                f"REQUIRED."
            )

        # Додаємо стовпець
        self.columns.append(column)

        # Для існуючих рядків створюємо порожнє значення
        for existing_row in self.rows:

            existing_row.values[
                column.name
            ] = None


    def delete_column(self, column_name: str):

        column = self.get_column(
            column_name
        )

        if column is None:

            raise ValueError(
                f"Стовпець '{column_name}' не існує."
            )

        if len(self.columns) == 1:

            raise ValueError(
                "Не можна видалити останній "
                "стовпець таблиці."
            )

        self.columns.remove(
            column
        )

        # Видаляємо поле з усіх рядків
        for existing_row in self.rows:

            existing_row.values.pop(
                column_name,
                None
            )

    def update_column(
        self,
        old_name: str,
        new_name: str,
        new_datatype,
        new_unique=False,
        new_required=False
    ):

        column = self.get_column(
            old_name
        )

        if column is None:

            raise ValueError(
                f"Стовпець '{old_name}' не існує."
            )


        new_name = new_name.strip()

        if not new_name:

            raise ValueError(
                "Назва стовпця не може бути порожньою."
            )


        for existing_column in self.columns:

            if existing_column is column:
                continue

            if (
                existing_column.name.lower()
                == new_name.lower()
            ):

                raise ValueError(
                    f"Стовпець '{new_name}' вже існує."
                )

        if column.datatype != new_datatype:

            for existing_row in self.rows:

                value = existing_row.values.get(
                    old_name
                )

                # Порожнє необов'язкове поле
                if value is None:
                    continue

                if not ValidationService.validate(
                    value,
                    new_datatype
                ):

                    raise ValueError(
                        f"Неможливо змінити тип "
                        f"стовпця '{old_name}' на "
                        f"'{new_datatype.value}', "
                        f"оскільки значення '{value}' "
                        f"не відповідає новому типу."
                    )


        if new_unique:

            seen_values = set()

            for existing_row in self.rows:

                value = existing_row.values.get(
                    old_name
                )

                # None не вважаємо дублікатом
                if value is None:
                    continue

                if value in seen_values:

                    raise ValueError(
                        f"Неможливо встановити UNIQUE "
                        f"для поля '{old_name}', "
                        f"оскільки значення '{value}' "
                        f"повторюється."
                    )

                seen_values.add(
                    value
                )


        if new_required:

            for existing_row in self.rows:

                value = existing_row.values.get(
                    old_name
                )

                if value is None or value == "":

                    raise ValueError(
                        f"Неможливо встановити REQUIRED "
                        f"для поля '{old_name}', "
                        f"оскільки є незаповнені значення."
                    )

        if old_name != new_name:

            for existing_row in self.rows:

                value = existing_row.values.pop(
                    old_name,
                    None
                )

                existing_row.values[
                    new_name
                ] = value


        column.name = new_name
        column.datatype = new_datatype
        column.unique = new_unique
        column.required = new_required


    def get_column(self, column_name: str):

        for column in self.columns:

            if column.name == column_name:
                return column

        return None


    def add_row(self, row):

        self._validate_row(
            row
        )

        self._validate_unique(
            row
        )

        self.rows.append(
            row
        )


    def update_row(
        self,
        index: int,
        row
    ):

        if (
            index < 0
            or index >= len(self.rows)
        ):

            raise IndexError(
                "Запис з таким індексом не існує."
            )

        self._validate_row(
            row
        )

        self._validate_unique(
            row,
            exclude_index=index
        )

        self.rows[index] = row


    def delete_row(
        self,
        index: int
    ):

        if (
            index < 0
            or index >= len(self.rows)
        ):

            raise IndexError(
                "Запис з таким індексом не існує."
            )

        self.rows.pop(
            index
        )


    def _validate_row(
        self,
        row
    ):

        for column in self.columns:


            if column.name not in row.values:

                if column.required:

                    raise ValueError(
                        f"Поле '{column.name}' "
                        f"є обов'язковим."
                    )

                continue

            value = row.values[
                column.name
            ]


            if value is None or value == "":

                if column.required:

                    raise ValueError(
                        f"Поле '{column.name}' "
                        f"є обов'язковим."
                    )

                # Необов'язкове поле може бути порожнім
                continue


            if not ValidationService.validate(
                value,
                column.datatype
            ):

                raise ValueError(
                    f"Некоректне значення "
                    f"'{value}' "
                    f"для стовпця "
                    f"'{column.name}' "
                    f"типу "
                    f"'{column.datatype.value}'."
                )

        column_names = {
            column.name
            for column in self.columns
        }

        for field_name in row.values:

            if field_name not in column_names:

                raise ValueError(
                    f"Стовпця '{field_name}' "
                    f"не існує в таблиці."
                )


    def _validate_unique(
        self,
        row,
        exclude_index=None
    ):

        for column in self.columns:

            if not column.unique:
                continue

            new_value = row.values.get(
                column.name
            )

            if new_value is None or new_value == "":
                continue

            for index, existing_row in enumerate(
                self.rows
            ):

                if (
                    exclude_index is not None
                    and index == exclude_index
                ):
                    continue

                existing_value = (
                    existing_row.values.get(
                        column.name
                    )
                )

                if existing_value == new_value:

                    raise ValueError(
                        f"Значення '{new_value}' "
                        f"у полі '{column.name}' "
                        f"має бути унікальним."
                    )