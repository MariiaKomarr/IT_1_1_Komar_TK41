from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QMessageBox,
    QInputDialog,
    QFileDialog
)

from models.database import Database
from services.storage_service import StorageService

from gui.create_table_dialog import CreateTableDialog
from gui.table_window import TableWindow
from gui.join_dialog import JoinDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Поточна база даних
        self.database = None

        # Шлях до JSON-файлу поточної БД
        self.current_file_path = None

        # Посилання на відкриті вікна
        self.table_window = None
        self.join_result_window = None

        self.setWindowTitle(
            "Table Database Management System"
        )

        self.resize(900, 600)

        self._create_ui()



    def _create_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(
            central_widget
        )


        self.database_label = QLabel(
            "База даних не відкрита"
        )

        main_layout.addWidget(
            self.database_label
        )


        database_buttons = QHBoxLayout()

        self.create_database_button = QPushButton(
            "Створити БД"
        )

        self.open_database_button = QPushButton(
            "Відкрити БД"
        )

        self.save_database_button = QPushButton(
            "Зберегти БД"
        )

        database_buttons.addWidget(
            self.create_database_button
        )

        database_buttons.addWidget(
            self.open_database_button
        )

        database_buttons.addWidget(
            self.save_database_button
        )

        main_layout.addLayout(
            database_buttons
        )


        main_layout.addWidget(
            QLabel("Таблиці:")
        )

        self.table_list = QListWidget()

        main_layout.addWidget(
            self.table_list
        )


        table_buttons = QHBoxLayout()

        self.create_table_button = QPushButton(
            "Створити таблицю"
        )

        self.delete_table_button = QPushButton(
            "Видалити таблицю"
        )

        self.join_button = QPushButton(
            "JOIN таблиць"
        )

        table_buttons.addWidget(
            self.create_table_button
        )

        table_buttons.addWidget(
            self.delete_table_button
        )

        table_buttons.addWidget(
            self.join_button
        )

        main_layout.addLayout(
            table_buttons
        )


        self.create_database_button.clicked.connect(
            self.create_database
        )

        self.open_database_button.clicked.connect(
            self.open_database
        )

        self.save_database_button.clicked.connect(
            self.save_database
        )

        self.create_table_button.clicked.connect(
            self.create_table
        )

        self.delete_table_button.clicked.connect(
            self.delete_table
        )

        self.join_button.clicked.connect(
            self.perform_join
        )

        self.table_list.itemDoubleClicked.connect(
            self.open_table
        )


    def create_database(self):

        name, ok = QInputDialog.getText(
            self,
            "Створення БД",
            "Введіть назву бази даних:"
        )

        if not ok:
            return

        name = name.strip()

        if not name:

            QMessageBox.warning(
                self,
                "Помилка",
                "Назва БД не може бути порожньою."
            )

            return

        try:

            self.database = Database(name)

            # Нова БД ще не має файлу
            self.current_file_path = None

            self.refresh_database_view()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )



    def open_database(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Відкрити базу даних",
            "",
            "JSON files (*.json)"
        )

        if not file_path:
            return

        try:

            self.database = StorageService.load(
                file_path
            )

            self.current_file_path = (
                file_path
            )

            self.refresh_database_view()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Помилка",
                f"Не вдалося відкрити БД:\n{error}"
            )



    def save_database(self):

        if self.database is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Спочатку створіть або відкрийте БД."
            )

            return


        if self.current_file_path:

            try:

                StorageService.save(
                    self.database,
                    self.current_file_path
                )

                QMessageBox.information(
                    self,
                    "Успішно",
                    "Базу даних збережено."
                )

            except Exception as error:

                QMessageBox.critical(
                    self,
                    "Помилка",
                    f"Не вдалося зберегти БД:\n{error}"
                )

            return


        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти базу даних",
            f"{self.database.name}.json",
            "JSON files (*.json)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".json"):
            file_path += ".json"

        try:

            StorageService.save(
                self.database,
                file_path
            )

            self.current_file_path = (
                file_path
            )

            QMessageBox.information(
                self,
                "Успішно",
                "Базу даних збережено.\n"
                "Автозбереження активне."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Помилка",
                f"Не вдалося зберегти БД:\n{error}"
            )


    def auto_save(self):

        if self.database is None:
            return

        if self.current_file_path is None:
            return

        try:

            StorageService.save(
                self.database,
                self.current_file_path
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Помилка автозбереження",
                f"Не вдалося автоматично "
                f"зберегти БД:\n{error}"
            )


    def create_table(self):

        if self.database is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Спочатку створіть або відкрийте БД."
            )

            return

        dialog = CreateTableDialog(
            self
        )

        if dialog.exec():

            try:

                table = dialog.get_table()

                self.database.add_table(
                    table
                )

                self.refresh_database_view()

                self.auto_save()

            except ValueError as error:

                QMessageBox.warning(
                    self,
                    "Помилка",
                    str(error)
                )



    def delete_table(self):

        if self.database is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "База даних не відкрита."
            )

            return

        item = self.table_list.currentItem()

        if item is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Виберіть таблицю для видалення."
            )

            return

        table_name = item.text()

        answer = QMessageBox.question(
            self,
            "Видалення таблиці",
            f"Ви дійсно хочете видалити "
            f"таблицю '{table_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        try:

            self.database.delete_table(
                table_name
            )

            self.refresh_database_view()

            self.auto_save()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )


    def open_table(self, item):

        if self.database is None:
            return

        table_name = item.text()

        table = None

        for current_table in self.database.tables:

            if current_table.name == table_name:

                table = current_table
                break

        if table is None:

            QMessageBox.warning(
                self,
                "Помилка",
                f"Таблицю '{table_name}' не знайдено."
            )

            return

        self.table_window = TableWindow(
            table,
            self
        )

        self.table_window.show()


    def perform_join(self):


        if self.database is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Спочатку створіть або відкрийте БД."
            )

            return


        if len(self.database.tables) < 2:

            QMessageBox.warning(
                self,
                "Помилка",
                "Для JOIN потрібно щонайменше дві таблиці."
            )

            return


        dialog = JoinDialog(
            self.database,
            self
        )

        if not dialog.exec():
            return


        result_table = (
            dialog.get_result_table()
        )

        if result_table is None:

            QMessageBox.warning(
                self,
                "Помилка",
                "Не вдалося отримати результат JOIN."
            )

            return


        self.join_result_window = TableWindow(
            result_table,
            self,
            read_only=True
        )

        self.join_result_window.setWindowTitle(
            f"Результат JOIN: "
            f"{result_table.name}"
        )

        self.join_result_window.show()

        answer = QMessageBox.question(
            self,
            "Зберегти результат",
            "Зберегти результат JOIN "
            "як нову таблицю в базі даних?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        default_name = result_table.name

        table_name, ok = QInputDialog.getText(
            self,
            "Назва таблиці",
            "Введіть назву нової таблиці:",
            text=default_name
        )

        if not ok:
            return

        table_name = table_name.strip()

        if not table_name:

            QMessageBox.warning(
                self,
                "Помилка",
                "Назва таблиці не може бути порожньою."
            )

            return


        for table in self.database.tables:

            if (
                table.name.lower()
                == table_name.lower()
            ):

                QMessageBox.warning(
                    self,
                    "Помилка",
                    f"Таблиця '{table_name}' "
                    f"вже існує."
                )

                return

        result_table.name = table_name

        try:

            self.database.add_table(
                result_table
            )

            # Оновлюємо список таблиць
            self.refresh_database_view()

            # Автоматично зберігаємо зміни
            self.auto_save()

            QMessageBox.information(
                self,
                "Успішно",
                f"Результат JOIN збережено "
                f"як таблицю '{table_name}'."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Помилка",
                str(error)
            )


    def refresh_database_view(self):

        self.table_list.clear()


        if self.database is None:

            self.database_label.setText(
                "База даних не відкрита"
            )

            return


        self.database_label.setText(
            f"Поточна БД: "
            f"{self.database.name}"
        )


        for table in self.database.tables:

            self.table_list.addItem(
                table.name
            )