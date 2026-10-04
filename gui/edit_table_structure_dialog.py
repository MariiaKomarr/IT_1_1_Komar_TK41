from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QMessageBox,
    QGroupBox
)

from models.column import Column
from models.datatype import DataType


class EditTableStructureDialog(QDialog):

    def __init__(self, table, parent=None):
        super().__init__(parent)

        self.table = table

        # Чи були внесені зміни
        self.structure_changed = False

        self.setWindowTitle(
            f"Структура таблиці: {self.table.name}"
        )

        self.resize(700, 600)

        self._create_ui()
        self.refresh_columns()


    def _create_ui(self):

        main_layout = QVBoxLayout(self)


        title_label = QLabel(
            f"Таблиця: {self.table.name}"
        )

        main_layout.addWidget(
            title_label
        )

        main_layout.addWidget(
            QLabel("Поточні стовпці:")
        )

        self.columns_list = QListWidget()

        main_layout.addWidget(
            self.columns_list
        )

        self.columns_list.currentRowChanged.connect(
            self.load_selected_column
        )


        edit_group = QGroupBox(
            "Параметри стовпця"
        )

        edit_layout = QVBoxLayout(
            edit_group
        )


        name_layout = QHBoxLayout()

        name_label = QLabel(
            "Назва:"
        )

        self.column_name_input = QLineEdit()

        name_layout.addWidget(
            name_label
        )

        name_layout.addWidget(
            self.column_name_input
        )

        edit_layout.addLayout(
            name_layout
        )


        type_layout = QHBoxLayout()

        type_label = QLabel(
            "Тип:"
        )

        self.datatype_combo = QComboBox()

        for datatype in DataType:

            self.datatype_combo.addItem(
                datatype.value,
                datatype
            )

        type_layout.addWidget(
            type_label
        )

        type_layout.addWidget(
            self.datatype_combo
        )

        edit_layout.addLayout(
            type_layout
        )


        self.unique_checkbox = QCheckBox(
            "Унікальне поле (UNIQUE)"
        )

        edit_layout.addWidget(
            self.unique_checkbox
        )


        self.required_checkbox = QCheckBox(
            "Обов'язкове поле (REQUIRED)"
        )

        edit_layout.addWidget(
            self.required_checkbox
        )

        main_layout.addWidget(
            edit_group
        )


        column_buttons_layout = QHBoxLayout()

        self.add_column_button = QPushButton(
            "Додати стовпець"
        )

        self.update_column_button = QPushButton(
            "Зберегти зміни стовпця"
        )

        self.delete_column_button = QPushButton(
            "Видалити стовпець"
        )

        column_buttons_layout.addWidget(
            self.add_column_button
        )

        column_buttons_layout.addWidget(
            self.update_column_button
        )

        column_buttons_layout.addWidget(
            self.delete_column_button
        )

        main_layout.addLayout(
            column_buttons_layout
        )


        close_layout = QHBoxLayout()

        self.close_button = QPushButton(
            "Закрити"
        )

        close_layout.addStretch()

        close_layout.addWidget(
            self.close_button
        )

        main_layout.addLayout(
            close_layout
        )


        self.add_column_button.clicked.connect(
            self.add_column
        )

        self.update_column_button.clicked.connect(
            self.update_column
        )

        self.delete_column_button.clicked.connect(
            self.delete_column
        )

        self.close_button.clicked.connect(
            self.accept
        )


    def refresh_columns(self):

        self.columns_list.clear()

        for column in self.table.columns:

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

        self.clear_form()


    def load_selected_column(
        self,
        index
    ):

        if index < 0:
            return

        if index >= len(
            self.table.columns
        ):
            return

        column = self.table.columns[
            index
        ]


        self.column_name_input.setText(
            column.name
        )


        datatype_index = (
            self.datatype_combo.findData(
                column.datatype
            )
        )

        if datatype_index >= 0:

            self.datatype_combo.setCurrentIndex(
                datatype_index
            )


        self.unique_checkbox.setChecked(
            column.unique
        )


        self.required_checkbox.setChecked(
            column.required
        )


    def add_column(self):

        column_name = (
            self.column_name_input
            .text()
            .strip()
        )

        datatype = (
            self.datatype_combo
            .currentData()
        )

        is_unique = (
            self.unique_checkbox
            .isChecked()
        )

        is_required = (
            self.required_checkbox
            .isChecked()
        )


        if not column_name:

            QMessageBox.warning(
                self,
                "Помилка",
                "Введіть назву стовпця."
            )

            return


        if datatype is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть тип даних."
            )

            return

        try:

            column = Column(
                column_name,
                datatype,
                unique=is_unique,
                required=is_required
            )

            self.table.add_column(
                column
            )

            self.structure_changed = True

            self.refresh_columns()

            QMessageBox.information(
                self,
                "Успішно",
                f"Стовпець '{column_name}' "
                f"додано."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )


    def update_column(self):

        selected_index = (
            self.columns_list
            .currentRow()
        )

        if selected_index < 0:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть стовпець "
                "для редагування."
            )

            return

        old_column = self.table.columns[
            selected_index
        ]

        old_name = old_column.name


        new_name = (
            self.column_name_input
            .text()
            .strip()
        )

        new_datatype = (
            self.datatype_combo
            .currentData()
        )

        new_unique = (
            self.unique_checkbox
            .isChecked()
        )

        new_required = (
            self.required_checkbox
            .isChecked()
        )


        if not new_name:

            QMessageBox.warning(
                self,
                "Помилка",
                "Назва стовпця "
                "не може бути порожньою."
            )

            return

        if new_datatype is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть тип даних."
            )

            return

        try:

            self.table.update_column(
                old_name,
                new_name,
                new_datatype,
                new_unique,
                new_required
            )

            self.structure_changed = True

            self.refresh_columns()

            QMessageBox.information(
                self,
                "Успішно",
                "Стовпець успішно змінено."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )


    def delete_column(self):

        selected_index = (
            self.columns_list
            .currentRow()
        )

        if selected_index < 0:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть стовпець "
                "для видалення."
            )

            return

        column = self.table.columns[
            selected_index
        ]

        column_name = column.name

        answer = QMessageBox.question(
            self,
            "Видалення стовпця",
            f"Видалити стовпець "
            f"'{column_name}'?\n\n"
            f"Усі значення цього стовпця "
            f"будуть видалені з таблиці.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        try:

            self.table.delete_column(
                column_name
            )

            self.structure_changed = True

            self.refresh_columns()

            QMessageBox.information(
                self,
                "Успішно",
                f"Стовпець '{column_name}' "
                f"видалено."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )


    def clear_form(self):

        self.column_name_input.clear()

        if self.datatype_combo.count() > 0:

            self.datatype_combo.setCurrentIndex(
                0
            )

        self.unique_checkbox.setChecked(
            False
        )

        self.required_checkbox.setChecked(
            False
        )


    def has_changes(self):

        return self.structure_changed