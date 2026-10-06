from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

import os

from models.database import Database
from models.table import Table
from models.column import Column
from models.row import Row
from models.datatype import DataType

from services.storage_service import StorageService
from services.join_service import JoinService


app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static"
)

current_database = None
current_database_file = None


DATABASE_FOLDER = "saved_databases"

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)


def auto_save_database():

    if (
        current_database is not None
        and current_database_file is not None
    ):

        StorageService.save(
            current_database,
            current_database_file
        )


@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route(
    "/create-database",
    methods=["GET", "POST"]
)
def create_database():

    global current_database
    global current_database_file

    error = None

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        )

        try:

            current_database = Database(name)

            # Одразу визначаємо файл,
            # у якому буде зберігатися БД

            file_name = (
                current_database.name
                + ".json"
            )

            current_database_file = os.path.join(
                DATABASE_FOLDER,
                file_name
            )

            # Одразу створюємо JSON-файл
            auto_save_database()

            return redirect(
                url_for("database_view")
            )

        except ValueError as e:

            error = str(e)

    return render_template(
        "create_database.html",
        error=error
    )


@app.route("/database")
def database_view():

    if current_database is None:

        return redirect(
            url_for("index")
        )

    return render_template(
        "database.html",
        database=current_database
    )


@app.route(
    "/create-table",
    methods=["GET", "POST"]
)
def create_table():

    global current_database

    if current_database is None:

        return redirect(
            url_for("index")
        )

    error = None

    form_data = {
        "table_name": "",
        "columns": [
            {
                "name": "",
                "type": DataType.INTEGER.value,
                "unique": False,
                "required": False
            }
        ]
    }

    if request.method == "POST":

        table_name = request.form.get(
            "table_name",
            ""
        ).strip()

        column_names = request.form.getlist(
            "column_name"
        )

        column_types = request.form.getlist(
            "column_type"
        )

        unique_columns = request.form.getlist(
            "unique"
        )

        required_columns = request.form.getlist(
            "required"
        )

        columns_data = []

        for i, column_name in enumerate(
            column_names
        ):

            columns_data.append({
                "name": column_name,

                "type": (
                    column_types[i]
                    if i < len(column_types)
                    else DataType.INTEGER.value
                ),

                "unique":
                    str(i) in unique_columns,

                "required":
                    str(i) in required_columns
            })

        form_data = {
            "table_name": table_name,
            "columns": columns_data
        }

        try:

            if not table_name:

                raise ValueError(
                    "Назва таблиці не може бути порожньою."
                )

            if not column_names:

                raise ValueError(
                    "Таблиця повинна містити хоча б один стовпець."
                )

            table = Table(
                table_name
            )

            for i, column_name in enumerate(
                column_names
            ):

                column_name = column_name.strip()

                if not column_name:

                    raise ValueError(
                        "Назва стовпця не може бути порожньою."
                    )

                datatype = DataType(
                    column_types[i]
                )

                column = Column(
                    column_name,
                    datatype,
                    unique=str(i) in unique_columns,
                    required=str(i) in required_columns
                )

                table.add_column(
                    column
                )

            current_database.add_table(
                table
            )

            # Автозбереження
            auto_save_database()

            return redirect(
                url_for("database_view")
            )

        except ValueError as e:

            error = str(e)

    return render_template(
        "create_table.html",
        error=error,
        datatypes=list(DataType),
        form_data=form_data
    )


@app.route(
    "/table/<table_name>"
)
def table_view(table_name):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    return render_template(
        "table.html",
        database=current_database,
        table=table
    )

@app.route(
    "/table/<table_name>/add-row",
    methods=["GET", "POST"]
)
def add_row(table_name):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    error = None
    form_data = {}

    if request.method == "POST":

        try:

            values = {}

            for column in table.columns:

                raw_value = request.form.get(
                    column.name,
                    ""
                )

                form_data[
                    column.name
                ] = raw_value

                if raw_value.strip() == "":

                    values[
                        column.name
                    ] = None

                    continue

                # INTEGER
                if column.datatype == DataType.INTEGER:

                    try:

                        values[
                            column.name
                        ] = int(raw_value)

                    except ValueError:

                        raise ValueError(
                            f"Поле '{column.name}' "
                            f"повинно містити ціле число."
                        )

                # REAL
                elif column.datatype == DataType.REAL:

                    try:

                        values[
                            column.name
                        ] = float(
                            raw_value.replace(
                                ",",
                                "."
                            )
                        )

                    except ValueError:

                        raise ValueError(
                            f"Поле '{column.name}' "
                            f"повинно містити число."
                        )

                # CHAR / STRING / DATE / DATE_INV
                else:

                    values[
                        column.name
                    ] = raw_value

            row = Row(
                values
            )

            table.add_row(
                row
            )

            # Автозбереження
            auto_save_database()

            return redirect(
                url_for(
                    "table_view",
                    table_name=table.name
                )
            )

        except ValueError as e:

            error = str(e)

    return render_template(
        "add_row.html",
        database=current_database,
        table=table,
        error=error,
        form_data=form_data
    )


@app.route(
    "/table/<table_name>/edit-row/<int:row_index>",
    methods=["GET", "POST"]
)
def edit_row(
    table_name,
    row_index
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    if (
        row_index < 0
        or row_index >= len(table.rows)
    ):

        return redirect(
            url_for(
                "table_view",
                table_name=table.name
            )
        )

    current_row = table.rows[
        row_index
    ]

    error = None

    form_data = {

        column.name:
            (
                ""
                if current_row.values.get(
                    column.name
                ) is None
                else str(
                    current_row.values.get(
                        column.name
                    )
                )
            )

        for column in table.columns
    }

    if request.method == "POST":

        try:

            values = {}
            form_data = {}

            for column in table.columns:

                raw_value = request.form.get(
                    column.name,
                    ""
                )

                form_data[
                    column.name
                ] = raw_value

                if raw_value.strip() == "":

                    values[
                        column.name
                    ] = None

                    continue

                if column.datatype == DataType.INTEGER:

                    try:

                        values[
                            column.name
                        ] = int(raw_value)

                    except ValueError:

                        raise ValueError(
                            f"Поле '{column.name}' "
                            f"повинно містити ціле число."
                        )

                elif column.datatype == DataType.REAL:

                    try:

                        values[
                            column.name
                        ] = float(
                            raw_value.replace(
                                ",",
                                "."
                            )
                        )

                    except ValueError:

                        raise ValueError(
                            f"Поле '{column.name}' "
                            f"повинно містити число."
                        )

                else:

                    values[
                        column.name
                    ] = raw_value

            new_row = Row(
                values
            )

            table.update_row(
                row_index,
                new_row
            )

            # Автозбереження
            auto_save_database()

            return redirect(
                url_for(
                    "table_view",
                    table_name=table.name
                )
            )

        except ValueError as e:

            error = str(e)

    return render_template(
        "edit_row.html",
        database=current_database,
        table=table,
        row_index=row_index,
        error=error,
        form_data=form_data
    )


@app.route(
    "/table/<table_name>/delete-row/<int:row_index>",
    methods=["POST"]
)
def delete_row(
    table_name,
    row_index
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    try:

        table.delete_row(
            row_index
        )

        # Автозбереження
        auto_save_database()

    except IndexError:

        pass

    return redirect(
        url_for(
            "table_view",
            table_name=table.name
        )
    )


@app.route(
    "/table/<table_name>/structure"
)
def edit_table_structure(
    table_name
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    error = request.args.get(
        "error"
    )

    return render_template(
        "edit_table_structure.html",
        database=current_database,
        table=table,
        error=error
    )


@app.route(
    "/table/<table_name>/add-column",
    methods=["GET", "POST"]
)
def add_column(
    table_name
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    error = None

    form_data = {
        "name": "",
        "type": DataType.INTEGER.value,
        "unique": False,
        "required": False
    }

    if request.method == "POST":

        column_name = request.form.get(
            "column_name",
            ""
        ).strip()

        column_type = request.form.get(
            "column_type",
            DataType.INTEGER.value
        )

        is_unique = (
            request.form.get(
                "unique"
            ) == "on"
        )

        is_required = (
            request.form.get(
                "required"
            ) == "on"
        )

        form_data = {
            "name": column_name,
            "type": column_type,
            "unique": is_unique,
            "required": is_required
        }

        try:

            if not column_name:

                raise ValueError(
                    "Назва стовпця не може бути порожньою."
                )

            datatype = DataType(
                column_type
            )

            column = Column(
                column_name,
                datatype,
                unique=is_unique,
                required=is_required
            )

            table.add_column(
                column
            )

            # Автозбереження
            auto_save_database()

            return redirect(
                url_for(
                    "edit_table_structure",
                    table_name=table.name
                )
            )

        except ValueError as e:

            error = str(e)

    return render_template(
        "add_column.html",
        database=current_database,
        table=table,
        datatypes=list(DataType),
        error=error,
        form_data=form_data
    )


@app.route(
    "/table/<table_name>/edit-column/<column_name>",
    methods=["GET", "POST"]
)
def edit_column(
    table_name,
    column_name
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    column = table.get_column(
        column_name
    )

    if column is None:

        return redirect(
            url_for(
                "edit_table_structure",
                table_name=table.name
            )
        )

    error = None

    form_data = {
        "name": column.name,
        "type": column.datatype.value,
        "unique": column.unique,
        "required": column.required
    }

    if request.method == "POST":

        new_name = request.form.get(
            "column_name",
            ""
        ).strip()

        new_type = request.form.get(
            "column_type",
            column.datatype.value
        )

        new_unique = (
            request.form.get(
                "unique"
            ) == "on"
        )

        new_required = (
            request.form.get(
                "required"
            ) == "on"
        )

        form_data = {
            "name": new_name,
            "type": new_type,
            "unique": new_unique,
            "required": new_required
        }

        try:

            new_datatype = DataType(
                new_type
            )

            table.update_column(
                old_name=column_name,
                new_name=new_name,
                new_datatype=new_datatype,
                new_unique=new_unique,
                new_required=new_required
            )

            # Автозбереження
            auto_save_database()

            return redirect(
                url_for(
                    "edit_table_structure",
                    table_name=table.name
                )
            )

        except ValueError as e:

            error = str(e)

    return render_template(
        "edit_column.html",
        database=current_database,
        table=table,
        column=column,
        datatypes=list(DataType),
        form_data=form_data,
        error=error
    )

@app.route(
    "/table/<table_name>/delete-column/<column_name>",
    methods=["POST"]
)
def delete_column(
    table_name,
    column_name
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    table = current_database.get_table(
        table_name
    )

    if table is None:

        return redirect(
            url_for("database_view")
        )

    try:

        table.delete_column(
            column_name
        )

        # Автозбереження
        auto_save_database()

    except ValueError as e:

        return redirect(
            url_for(
                "edit_table_structure",
                table_name=table.name,
                error=str(e)
            )
        )

    return redirect(
        url_for(
            "edit_table_structure",
            table_name=table.name
        )
    )


@app.route(
    "/table/<table_name>/delete",
    methods=["POST"]
)
def delete_table(
    table_name
):

    if current_database is None:

        return redirect(
            url_for("index")
        )

    try:

        current_database.delete_table(
            table_name
        )

        # Автозбереження
        auto_save_database()

    except ValueError:

        pass

    return redirect(
        url_for("database_view")
    )


@app.route(
    "/save-database",
    methods=["POST"]
)
def save_database():

    global current_database_file

    if current_database is None:

        return redirect(
            url_for("index")
        )

    # Якщо файл ще не визначений
    if current_database_file is None:

        file_name = (
            current_database.name
            + ".json"
        )

        current_database_file = os.path.join(
            DATABASE_FOLDER,
            file_name
        )

    StorageService.save(
        current_database,
        current_database_file
    )

    return redirect(
        url_for("database_view")
    )

@app.route(
    "/open-database"
)
def open_database():

    files = []

    if os.path.exists(
        DATABASE_FOLDER
    ):

        for file_name in os.listdir(
            DATABASE_FOLDER
        ):

            if file_name.endswith(
                ".json"
            ):

                files.append(
                    file_name
                )

    files.sort()

    return render_template(
        "open_database.html",
        files=files
    )

@app.route(
    "/load-database/<file_name>",
    methods=["POST"]
)
def load_database(
    file_name
):

    global current_database
    global current_database_file

    safe_file_name = os.path.basename(
        file_name
    )

    file_path = os.path.join(
        DATABASE_FOLDER,
        safe_file_name
    )

    if not os.path.exists(
        file_path
    ):

        return redirect(
            url_for("open_database")
        )

    try:

        current_database = StorageService.load(
            file_path
        )

        # Важливо для подальшого автозбереження
        current_database_file = file_path

    except (
        ValueError,
        OSError,
        KeyError
    ):

        return redirect(
            url_for("open_database")
        )

    return redirect(
        url_for("database_view")
    )


@app.route(
    "/join-tables",
    methods=["GET", "POST"]
)
def join_tables():

    global current_database

    if current_database is None:

        return redirect(
            url_for("index")
        )

    error = None

    form_data = {
        "table1": "",
        "table2": "",
        "common_field": "",
        "save_result": "no",
        "result_name": ""
    }

    if request.method == "POST":

        table1_name = request.form.get(
            "table1",
            ""
        )

        table2_name = request.form.get(
            "table2",
            ""
        )

        common_field = request.form.get(
            "common_field",
            ""
        ).strip()

        save_result = request.form.get(
            "save_result",
            "no"
        )

        result_name = request.form.get(
            "result_name",
            ""
        ).strip()

        form_data = {
            "table1": table1_name,
            "table2": table2_name,
            "common_field": common_field,
            "save_result": save_result,
            "result_name": result_name
        }

        try:

            if not table1_name:

                raise ValueError(
                    "Оберіть першу таблицю."
                )

            if not table2_name:

                raise ValueError(
                    "Оберіть другу таблицю."
                )

            if table1_name == table2_name:

                raise ValueError(
                    "Для сполучення потрібно "
                    "обрати дві різні таблиці."
                )

            if not common_field:

                raise ValueError(
                    "Оберіть спільне поле."
                )

            table1 = current_database.get_table(
                table1_name
            )

            table2 = current_database.get_table(
                table2_name
            )

            if table1 is None:

                raise ValueError(
                    "Першу таблицю не знайдено."
                )

            if table2 is None:

                raise ValueError(
                    "Другу таблицю не знайдено."
                )

            result_table = JoinService.join(
                table1,
                table2,
                common_field
            )

            if save_result == "yes":

                if not result_name:

                    raise ValueError(
                        "Вкажіть назву нової таблиці."
                    )

                if current_database.get_table(
                    result_name
                ) is not None:

                    raise ValueError(
                        f"Таблиця '{result_name}' "
                        f"вже існує."
                    )

                result_table.name = (
                    result_name
                )

                current_database.add_table(
                    result_table
                )

                # JOIN зберігаємо,
                # бо користувач вибрав "Зберегти"
                auto_save_database()

                return redirect(
                    url_for(
                        "table_view",
                        table_name=result_table.name
                    )
                )

            return render_template(
                "join_result.html",
                database=current_database,
                table=result_table,
                table1_name=table1_name,
                table2_name=table2_name,
                common_field=common_field
            )

        except ValueError as e:

            error = str(e)

    tables_data = {}

    for table in current_database.tables:

        tables_data[
            table.name
        ] = [

            {
                "name": column.name,
                "type": column.datatype.value
            }

            for column in table.columns
        ]

    return render_template(
        "join_tables.html",
        database=current_database,
        tables_data=tables_data,
        error=error,
        form_data=form_data
    )

if __name__ == "__main__":

    app.run(
        debug=True
    )