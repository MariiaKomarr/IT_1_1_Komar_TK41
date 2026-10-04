from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView
)

from gui.row_dialog import RowDialog
from gui.edit_table_structure_dialog import EditTableStructureDialog


class TableWindow(QMainWindow):

    def __init__(
        self,
        table,
        parent=None,
        read_only=False
    ):
        super().__init__(parent)

        self.table = table
        self.main_window = parent
        self.read_only = read_only

        self.setWindowTitle(
            f"Таблиця: {self.table.name}"
        )

        self.resize(
            950,
            600
        )

        self._create_ui()
        self.refresh_table()



    def _create_ui(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )


        self.table_label = QLabel(
            f"Таблиця: {self.table.name}"
        )

        main_layout.addWidget(
            self.table_label
        )


        self.table_widget = QTableWidget()

        main_layout.addWidget(
            self.table_widget
        )

        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.table_widget.horizontalHeader().setStretchLastSection(
            True
        )

        # Забороняємо редагування прямо в клітинці
        self.table_widget.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        # Виділяємо весь рядок
        self.table_widget.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        # Один рядок за раз
        self.table_widget.setSelectionMode(
            QAbstractItemView.SingleSelection
        )


        row_buttons_layout = QHBoxLayout()

        self.add_row_button = QPushButton(
            "Додати запис"
        )

        self.edit_row_button = QPushButton(
            "Редагувати запис"
        )

        self.delete_row_button = QPushButton(
            "Видалити запис"
        )

        row_buttons_layout.addWidget(
            self.add_row_button
        )

        row_buttons_layout.addWidget(
            self.edit_row_button
        )

        row_buttons_layout.addWidget(
            self.delete_row_button
        )

        main_layout.addLayout(
            row_buttons_layout
        )


        structure_layout = QHBoxLayout()

        self.edit_structure_button = QPushButton(
            "Змінити структуру таблиці"
        )

        structure_layout.addWidget(
            self.edit_structure_button
        )

        main_layout.addLayout(
            structure_layout
        )


        if self.read_only:

            self.add_row_button.hide()
            self.edit_row_button.hide()
            self.delete_row_button.hide()
            self.edit_structure_button.hide()


        self.add_row_button.clicked.connect(
            self.add_row
        )

        self.edit_row_button.clicked.connect(
            self.edit_row
        )

        self.delete_row_button.clicked.connect(
            self.delete_row
        )

        self.edit_structure_button.clicked.connect(
            self.edit_structure
        )

        # Подвійний клік = редагування
        if not self.read_only:

            self.table_widget.doubleClicked.connect(
                self.edit_row
            )



    def refresh_table(self):

        self.table_widget.clear()


        self.table_widget.setColumnCount(
            len(self.table.columns)
        )

        column_names = []

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

            column_names.append(
                f"{column.name}{properties_text}"
            )

        self.table_widget.setHorizontalHeaderLabels(
            column_names
        )


        self.table_widget.setRowCount(
            len(self.table.rows)
        )

        for row_index, row in enumerate(
            self.table.rows
        ):

            for column_index, column in enumerate(
                self.table.columns
            ):

                value = row.values.get(
                    column.name
                )

                # None показуємо порожньою клітинкою
                display_value = (
                    ""
                    if value is None
                    else str(value)
                )

                item = QTableWidgetItem(
                    display_value
                )

                self.table_widget.setItem(
                    row_index,
                    column_index,
                    item
                )

        self.table_widget.resizeColumnsToContents()

        self.table_widget.horizontalHeader().setStretchLastSection(
            True
        )



    def add_row(self):

        dialog = RowDialog(
            self.table,
            self
        )

        if not dialog.exec():
            return

        try:

            row = dialog.get_row()

            self.table.add_row(
                row
            )

            self.refresh_table()

            self.auto_save()

            QMessageBox.information(
                self,
                "Успішно",
                "Запис успішно додано."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )



    def edit_row(self):

        row_index = (
            self.table_widget
            .currentRow()
        )

        if row_index < 0:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть запис для редагування."
            )

            return

        existing_row = self.table.rows[
            row_index
        ]

        dialog = RowDialog(
            self.table,
            self,
            row=existing_row
        )

        if not dialog.exec():
            return

        try:

            edited_row = (
                dialog.get_row()
            )

            # ВАЖЛИВО:
            # використовуємо метод Table,
            # щоб спрацювали всі перевірки
            self.table.update_row(
                row_index,
                edited_row
            )

            self.refresh_table()

            self.auto_save()

            QMessageBox.information(
                self,
                "Успішно",
                "Запис успішно відредаговано."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )



    def delete_row(self):

        row_index = (
            self.table_widget
            .currentRow()
        )

        if row_index < 0:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть запис для видалення."
            )

            return

        row = self.table.rows[
            row_index
        ]


        row_description = []

        for column in self.table.columns:

            value = row.values.get(
                column.name
            )

            display_value = (
                ""
                if value is None
                else str(value)
            )

            row_description.append(
                f"{column.name}: {display_value}"
            )

        description_text = "\n".join(
            row_description
        )


        answer = QMessageBox.question(
            self,
            "Видалення запису",
            "Ви дійсно хочете видалити цей запис?\n\n"
            + description_text,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        try:

            # Використовуємо метод Table
            self.table.delete_row(
                row_index
            )

            self.refresh_table()

            self.auto_save()

            QMessageBox.information(
                self,
                "Успішно",
                "Запис успішно видалено."
            )

        except (ValueError, IndexError) as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )


    def edit_structure(self):

        dialog = EditTableStructureDialog(
            self.table,
            self
        )

        dialog.exec()


        if dialog.has_changes():

            # Оновлюємо таблицю на екрані
            self.refresh_table()

            # Одразу зберігаємо БД
            self.auto_save()

            QMessageBox.information(
                self,
                "Структуру оновлено",
                "Зміни структури таблиці "
                "успішно збережено."
            )


    def auto_save(self):

        if self.main_window is not None:

            self.main_window.auto_save()