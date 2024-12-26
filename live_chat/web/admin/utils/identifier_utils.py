from typing import Any, get_args
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqladmin.helpers import (
    _object_identifier_parts,
    get_column_python_type,
    get_primary_keys,
)


def custom_object_identifier_values(
    id_string: str,
    model: Any,
) -> tuple[bool | Any, ...]:
    """Converts a string identifier into a tuple of primary key values for a model."""
    values = []
    pks = get_primary_keys(model)

    for pk, part in zip(pks, _object_identifier_parts(id_string, model)):
        type_ = get_column_python_type(pk)

        if (type_ := get_args(type_)[0]) and type_ in {UUID, GUID}:
            part = str(part)  # noqa: PLW2901

        value = False if type_ is bool and part == "False" else type_(part)
        values.append(value)
    return tuple(values)
