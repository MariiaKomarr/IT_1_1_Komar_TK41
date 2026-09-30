from models.datatype import DataType
from services.validation_service import ValidationService


def test_validation():
    assert ValidationService.validate(10, DataType.INTEGER)
    assert ValidationService.validate(10.5, DataType.REAL)
    assert ValidationService.validate("A", DataType.CHAR)
    assert ValidationService.validate("Maria", DataType.STRING)
    assert ValidationService.validate("25.09.2026", DataType.DATE)
    assert ValidationService.validate(
        "01.09.2026 - 30.09.2026",
        DataType.DATE_INV
    )

    assert not ValidationService.validate(
        "Maria",
        DataType.INTEGER
    )

    assert not ValidationService.validate(
        "31.02.2026",
        DataType.DATE
    )