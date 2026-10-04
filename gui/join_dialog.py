from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QMessageBox
)

from services.join_service import JoinService


class JoinDialog(QDialog):

    def __init__(self, database, parent=None):
        super().__init__(parent)

        self.database = database

        # Тут буде результат JOIN
        self.result_table = None

        self.setWindowTitle("JOIN таблиць")
        self.resize(500, 300)

        self._create_ui()
        self.load_tables()


    def _create_ui(self):

        main_layout = QVBoxLayout(self)


        table1_layout = QHBoxLayout()

        table1_label = QLabel(
            "Перша таблиця:"
        )

        self.table1_combo = QComboBox()

        table1_layout.addWidget(
            table1_label
        )

        table1_layout.addWidget(
            self.table1_combo
        )

        main_layout.addLayout(
            table1_layout
        )


        table2_layout = QHBoxLayout()

        table2_label = QLabel(
            "Друга таблиця:"
        )

        self.table2_combo = QComboBox()

        table2_layout.addWidget(
            table2_label
        )

        table2_layout.addWidget(
            self.table2_combo
        )

        main_layout.addLayout(
            table2_layout
        )


        field_layout = QHBoxLayout()

        field_label = QLabel(
            "Спільне поле:"
        )

        self.field_combo = QComboBox()

        field_layout.addWidget(
            field_label
        )

        field_layout.addWidget(
            self.field_combo
        )

        main_layout.addLayout(
            field_layout
        )


        self.info_label = QLabel(
            "Виберіть дві таблиці."
        )

        main_layout.addWidget(
            self.info_label
        )


        buttons_layout = QHBoxLayout()

        self.join_button = QPushButton(
            "Виконати JOIN"
        )

        self.cancel_button = QPushButton(
            "Скасувати"
        )

        buttons_layout.addWidget(
            self.join_button
        )

        buttons_layout.addWidget(
            self.cancel_button
        )

        main_layout.addLayout(
            buttons_layout
        )


        self.table1_combo.currentIndexChanged.connect(
            self.update_common_fields
        )

        self.table2_combo.currentIndexChanged.connect(
            self.update_common_fields
        )

        self.join_button.clicked.connect(
            self.perform_join
        )

        self.cancel_button.clicked.connect(
            self.reject
        )


    def load_tables(self):

        self.table1_combo.clear()
        self.table2_combo.clear()

        for table in self.database.tables:

            # Зберігаємо сам об'єкт Table
            # всередині QComboBox
            self.table1_combo.addItem(
                table.name,
                table
            )

            self.table2_combo.addItem(
                table.name,
                table
            )

        # Якщо є хоча б дві таблиці,
        # одразу вибираємо різні
        if len(self.database.tables) >= 2:

            self.table1_combo.setCurrentIndex(0)
            self.table2_combo.setCurrentIndex(1)

        self.update_common_fields()


    def update_common_fields(self):

        self.field_combo.clear()

        table1 = self.table1_combo.currentData()
        table2 = self.table2_combo.currentData()

        if table1 is None or table2 is None:
            return

        # Не дозволяємо JOIN таблиці із самою собою
        if table1 is table2:

            self.info_label.setText(
                "Виберіть дві різні таблиці."
            )

            self.join_button.setEnabled(
                False
            )

            return

        common_fields = []


        for column1 in table1.columns:

            for column2 in table2.columns:

                if (
                    column1.name == column2.name
                    and
                    column1.datatype == column2.datatype
                ):

                    common_fields.append(
                        column1.name
                    )


        if not common_fields:

            self.info_label.setText(
                "Немає спільних полів "
                "з однаковим типом."
            )

            self.join_button.setEnabled(
                False
            )

            return


        self.field_combo.addItems(
            common_fields
        )

        self.info_label.setText(
            f"Знайдено спільних полів: "
            f"{len(common_fields)}"
        )

        self.join_button.setEnabled(
            True
        )


    def perform_join(self):

        table1 = (
            self.table1_combo
            .currentData()
        )

        table2 = (
            self.table2_combo
            .currentData()
        )

        common_field = (
            self.field_combo
            .currentText()
        )

        if table1 is None or table2 is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть дві таблиці."
            )

            return

        if table1 is table2:

            QMessageBox.warning(
                self,
                "Помилка",
                "Необхідно вибрати "
                "дві різні таблиці."
            )

            return

        if not common_field:

            QMessageBox.warning(
                self,
                "Помилка",
                "Немає поля для JOIN."
            )

            return

        try:

            self.result_table = JoinService.join(
                table1,
                table2,
                common_field
            )

            # Закриваємо діалог із результатом Accepted
            self.accept()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка JOIN",
                str(error)
            )


    def get_result_table(self):

        return self.result_table