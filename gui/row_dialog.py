from datetime import datetime, date

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

from models.row import Row
from services.validation_service import ValidationService


class RowDialog(QDialog):

    def __init__(
        self,
        table,
        parent=None,
        row=None
    ):
        super().__init__(parent)

        self.table = table
        self.row = row

        # Назва стовпця -> QLineEdit
        self.inputs = {}

        if self.row is None:
            self.setWindowTitle(
                f"Додати запис — {self.table.name}"
            )
        else:
            self.setWindowTitle(
                f"Редагувати запис — {self.table.name}"
            )

        self.resize(550, 350)

        self._create_ui()



    def _create_ui(self):

        main_layout = QVBoxLayout(self)


        for column in self.table.columns:

            field_layout = QHBoxLayout()


            properties = []

            if column.unique:
                properties.append(
                    "UNIQUE"
                )

            if column.required:
                properties.append(
                    "REQUIRED"
                )

            properties_text = ""

            if properties:
                properties_text = (
                    ", " + ", ".join(properties)
                )

            label = QLabel(
                f"{column.name} "
                f"({column.datatype.value}"
                f"{properties_text}):"
            )


            input_field = QLineEdit()


            if column.datatype.value == "integer":

                input_field.setPlaceholderText(
                    "Ціле число"
                )

            elif column.datatype.value == "real":

                input_field.setPlaceholderText(
                    "Наприклад: 125.50"
                )

            elif column.datatype.value == "char":

                input_field.setPlaceholderText(
                    "Один символ"
                )

            elif column.datatype.value == "string":

                input_field.setPlaceholderText(
                    "Текст"
                )

            elif column.datatype.value == "date":

                input_field.setPlaceholderText(
                    "ДД.ММ.РРРР, наприклад: 25.09.2003"
                )

            elif column.datatype.value == "dateInv":

                input_field.setPlaceholderText(
                    "Наприклад: "
                    "01.01.2026 - 31.12.2026"
                )


            if self.row is not None:

                old_value = self.row.values.get(
                    column.name
                )

                # None показуємо як порожнє поле,
                # а не як текст "None"
                if old_value is None:
                    input_field.setText("")
                else:
                    input_field.setText(
                        str(old_value)
                    )

            self.inputs[column.name] = (
                input_field
            )

            field_layout.addWidget(
                label
            )

            field_layout.addWidget(
                input_field
            )

            main_layout.addLayout(
                field_layout
            )


        buttons_layout = QHBoxLayout()

        if self.row is None:

            self.save_button = QPushButton(
                "Додати"
            )

        else:

            self.save_button = QPushButton(
                "Зберегти зміни"
            )

        self.cancel_button = QPushButton(
            "Скасувати"
        )

        buttons_layout.addWidget(
            self.save_button
        )

        buttons_layout.addWidget(
            self.cancel_button
        )

        main_layout.addLayout(
            buttons_layout
        )


        self.save_button.clicked.connect(
            self.validate_and_accept
        )

        self.cancel_button.clicked.connect(
            self.reject
        )


    def validate_and_accept(self):

        values = {}


        for column in self.table.columns:

            value = (
                self.inputs[column.name]
                .text()
                .strip()
            )


            if not value:

                # REQUIRED -> помилка
                if column.required:

                    QMessageBox.warning(
                        self,
                        "Помилка",
                        f"Поле '{column.name}' "
                        f"є обов'язковим."
                    )

                    return

                # Необов'язкове поле
                values[column.name] = None

                continue


            try:

                converted_value = (
                    self.convert_value(
                        value,
                        column.datatype
                    )
                )

            except ValueError as error:

                QMessageBox.warning(
                    self,
                    "Помилка",
                    str(error)
                )

                return


            if not ValidationService.validate(
                converted_value,
                column.datatype
            ):

                QMessageBox.warning(
                    self,
                    "Помилка",
                    f"Некоректне значення "
                    f"для поля '{column.name}'.\n"
                    f"Очікується тип: "
                    f"{column.datatype.value}"
                )

                return


            if (
                column.name.lower() == "birth_date"
                and column.datatype.value == "date"
            ):

                try:

                    birth_date = datetime.strptime(
                        converted_value,
                        "%d.%m.%Y"
                    ).date()

                except ValueError:

                    QMessageBox.warning(
                        self,
                        "Помилка",
                        "Некоректна дата народження.\n"
                        "Використовуйте формат "
                        "ДД.ММ.РРРР."
                    )

                    return

                if birth_date > date.today():

                    QMessageBox.warning(
                        self,
                        "Помилка",
                        "Дата народження не може "
                        "бути в майбутньому."
                    )

                    return


            values[column.name] = (
                converted_value
            )


        for column in self.table.columns:

            if not column.unique:
                continue

            new_value = values.get(
                column.name
            )

            # None дозволяємо повторювати
            if new_value is None:
                continue

            for existing_row in self.table.rows:

                # При редагуванні рядок
                # не порівнюємо сам із собою
                if (
                    self.row is not None
                    and existing_row is self.row
                ):
                    continue

                existing_value = (
                    existing_row.values.get(
                        column.name
                    )
                )

                if existing_value == new_value:

                    QMessageBox.warning(
                        self,
                        "Помилка",
                        f"Значення '{new_value}' "
                        f"у полі '{column.name}' "
                        f"має бути унікальним."
                    )

                    return


        self.accept()


    def convert_value(
        self,
        value,
        datatype
    ):

        # Порожнє необов'язкове значення
        if value is None or value == "":
            return None

        type_name = datatype.value


        if type_name == "integer":

            try:

                return int(
                    value
                )

            except ValueError:

                raise ValueError(
                    f"Значення '{value}' "
                    f"повинно бути цілим числом."
                )


        elif type_name == "real":

            try:

                return float(
                    value.replace(",", ".")
                )

            except ValueError:

                raise ValueError(
                    f"Значення '{value}' "
                    f"повинно бути дійсним числом."
                )


        elif type_name == "char":

            if len(value) != 1:

                raise ValueError(
                    f"Значення '{value}' "
                    f"повинно містити "
                    f"рівно один символ."
                )

            return value


        return value



    def get_row(self):

        values = {}

        for column in self.table.columns:

            text_value = (
                self.inputs[column.name]
                .text()
                .strip()
            )



            if not text_value:

                values[column.name] = None
                continue


            values[column.name] = (
                self.convert_value(
                    text_value,
                    column.datatype
                )
            )

        return Row(
            values
        )