from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QComboBox,
    QMessageBox,
    QCheckBox
)

from models.table import Table
from models.column import Column
from models.datatype import DataType


class CreateTableDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Тут тимчасово зберігаємо створені стовпці
        self.columns = []

        self.setWindowTitle("Створення таблиці")
        self.resize(550, 550)

        self._create_ui()


    def _create_ui(self):

        main_layout = QVBoxLayout(self)


        table_name_label = QLabel(
            "Назва таблиці:"
        )

        self.table_name_input = QLineEdit()

        self.table_name_input.setPlaceholderText(
            "Наприклад: Clients"
        )

        main_layout.addWidget(
            table_name_label
        )

        main_layout.addWidget(
            self.table_name_input
        )


        column_label = QLabel(
            "Новий стовпець:"
        )

        main_layout.addWidget(
            column_label
        )


        column_name_layout = QHBoxLayout()

        column_name_label = QLabel(
            "Назва:"
        )

        self.column_name_input = QLineEdit()

        self.column_name_input.setPlaceholderText(
            "Наприклад: client_id"
        )

        column_name_layout.addWidget(
            column_name_label
        )

        column_name_layout.addWidget(
            self.column_name_input
        )

        main_layout.addLayout(
            column_name_layout
        )


        datatype_layout = QHBoxLayout()

        datatype_label = QLabel(
            "Тип:"
        )

        self.datatype_combo = QComboBox()

        for datatype in DataType:

            self.datatype_combo.addItem(
                datatype.value,
                datatype
            )

        datatype_layout.addWidget(
            datatype_label
        )

        datatype_layout.addWidget(
            self.datatype_combo
        )

        main_layout.addLayout(
            datatype_layout
        )


        self.unique_checkbox = QCheckBox(
            "Унікальне поле (UNIQUE)"
        )

        main_layout.addWidget(
            self.unique_checkbox
        )


        self.required_checkbox = QCheckBox(
            "Обов'язкове поле (REQUIRED)"
        )

        main_layout.addWidget(
            self.required_checkbox
        )


        self.add_column_button = QPushButton(
            "Додати стовпець"
        )

        main_layout.addWidget(
            self.add_column_button
        )


        columns_label = QLabel(
            "Стовпці таблиці:"
        )

        main_layout.addWidget(
            columns_label
        )

        self.columns_list = QListWidget()

        main_layout.addWidget(
            self.columns_list
        )


        self.delete_column_button = QPushButton(
            "Видалити вибраний стовпець"
        )

        main_layout.addWidget(
            self.delete_column_button
        )


        buttons_layout = QHBoxLayout()

        self.create_button = QPushButton(
            "Створити таблицю"
        )

        self.cancel_button = QPushButton(
            "Скасувати"
        )

        buttons_layout.addWidget(
            self.create_button
        )

        buttons_layout.addWidget(
            self.cancel_button
        )

        main_layout.addLayout(
            buttons_layout
        )



        self.add_column_button.clicked.connect(
            self.add_column
        )

        self.delete_column_button.clicked.connect(
            self.delete_column
        )

        self.create_button.clicked.connect(
            self.validate_and_accept
        )

        self.cancel_button.clicked.connect(
            self.reject
        )



    def add_column(self):

        column_name = (
            self.column_name_input
            .text()
            .strip()
        )


        if not column_name:

            QMessageBox.warning(
                self,
                "Помилка",
                "Введіть назву стовпця."
            )

            return


        for existing_column in self.columns:

            if (
                existing_column.name.lower()
                == column_name.lower()
            ):

                QMessageBox.warning(
                    self,
                    "Помилка",
                    f"Стовпець '{column_name}' "
                    f"вже існує."
                )

                return


        datatype = (
            self.datatype_combo
            .currentData()
        )

        if datatype is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть тип даних."
            )

            return


        is_unique = (
            self.unique_checkbox
            .isChecked()
        )


        is_required = (
            self.required_checkbox
            .isChecked()
        )


        try:

            column = Column(
                column_name,
                datatype,
                unique=is_unique,
                required=is_required
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )

            return


        self.columns.append(
            column
        )


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
                " ["
                + ", ".join(properties)
                + "]"
            )

        self.columns_list.addItem(
            f"{column.name} : "
            f"{column.datatype.value}"
            f"{properties_text}"
        )


        self.column_name_input.clear()

        self.unique_checkbox.setChecked(
            False
        )

        self.required_checkbox.setChecked(
            False
        )

        self.column_name_input.setFocus()


    def delete_column(self):

        current_row = (
            self.columns_list
            .currentRow()
        )

        if current_row < 0:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть стовпець "
                "для видалення."
            )

            return

        # Видаляємо з внутрішнього списку
        self.columns.pop(
            current_row
        )

        # Видаляємо з GUI
        self.columns_list.takeItem(
            current_row
        )



    def validate_and_accept(self):

        table_name = (
            self.table_name_input
            .text()
            .strip()
        )


        if not table_name:

            QMessageBox.warning(
                self,
                "Помилка",
                "Введіть назву таблиці."
            )

            return


        if not self.columns:

            QMessageBox.warning(
                self,
                "Помилка",
                "Додайте хоча б один стовпець."
            )

            return

        self.accept()




    def get_table(self):

        table_name = (
            self.table_name_input
            .text()
            .strip()
        )

        table = Table(
            table_name
        )


        for column in self.columns:

            new_column = Column(
                column.name,
                column.datatype,
                unique=column.unique,
                required=column.required
            )

            table.add_column(
                new_column
            )

        return table