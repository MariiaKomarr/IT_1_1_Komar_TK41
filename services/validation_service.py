from datetime import datetime
from models.datatype import DataType


class ValidationService:

    @staticmethod
    def validate(value, data_type: DataType) -> bool:

        if data_type == DataType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)

        if data_type == DataType.REAL:
            return isinstance(value, (int, float)) and not isinstance(value, bool)

        if data_type == DataType.CHAR:
            return isinstance(value, str) and len(value) == 1

        if data_type == DataType.STRING:
            return isinstance(value, str)

        if data_type == DataType.DATE:
            return ValidationService._validate_date(value)

        if data_type == DataType.DATE_INV:
            return ValidationService._validate_date_interval(value)

        return False

    @staticmethod
    def _validate_date(value) -> bool:
        if not isinstance(value, str):
            return False

        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def _validate_date_interval(value) -> bool:
        if not isinstance(value, str):
            return False

        try:
            parts = value.split("-")

            if len(parts) != 2:
                return False

            start = datetime.strptime(parts[0].strip(), "%d.%m.%Y")
            end = datetime.strptime(parts[1].strip(), "%d.%m.%Y")

            return start <= end

        except ValueError:
            return False