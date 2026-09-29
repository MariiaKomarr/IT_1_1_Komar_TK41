from models.datatype import DataType


class Column:
    def __init__(self, name: str, data_type: DataType):
        if not name.strip():
            raise ValueError("Назва стовпця не може бути порожньою.")

        if not isinstance(data_type, DataType):
            raise ValueError("Невідомий тип даних.")

        self.name = name.strip()
        self.datatype = data_type