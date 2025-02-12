from typing import Any, get_args
from uuid import UUID

from fastapi_users_db_sqlalchemy import GUID
from sqladmin.helpers import (
    _object_identifier_parts,
    get_column_python_type,
    get_primary_keys,
)
from sqlalchemy import Select, select


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


class CustomStmtMixin:
    """Mixin for SQLAdmin that raise error with UUID identifiers."""

    model: Any

    def _stmt_by_identifier(self, identifier: str) -> Select[Any]:
        stmt: Select[Any] = select(self.model)
        pks = get_primary_keys(self.model)
        values = custom_object_identifier_values(identifier, self.model)
        conditions = [pk == value for (pk, value) in zip(pks, values)]
        return stmt.where(*conditions)
