class Column:

    def __init__(
        self,
        name,
        datatype,
        unique=False,
        required=False
    ):

        if not name or not name.strip():
            raise ValueError(
                "Назва стовпця не може бути порожньою."
            )

        self.name = name.strip()
        self.datatype = datatype
        self.unique = unique
        self.required = required


    def __repr__(self):

        properties = []

        if self.unique:
            properties.append("UNIQUE")

        if self.required:
            properties.append("REQUIRED")

        properties_text = ""

        if properties:
            properties_text = " " + " ".join(properties)

        return (
            f"Column("
            f"name='{self.name}', "
            f"datatype={self.datatype.value}"
            f"{properties_text}"
            f")"
        )