class Database:
    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Назва БД не може бути порожньою.")

        self.name = name.strip()
        self.tables = []

    def add_table(self, table):
        if self.get_table(table.name) is not None:
            raise ValueError(
                f"Таблиця '{table.name}' вже існує."
            )

        self.tables.append(table)

    def delete_table(self, table_name: str):
        table = self.get_table(table_name)

        if table is None:
            raise ValueError(
                f"Таблиця '{table_name}' не існує."
            )

        self.tables.remove(table)

    def get_table(self, table_name: str):
        for table in self.tables:
            if table.name == table_name:
                return table

        return None