from __future__ import annotations

import copy
from typing import Any, TypeVar, get_args, get_origin

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = TypeVar("T")


class UnorderedList(list[T]):
    """
    Represents a list that compares equality by its elements, regardless of their order. This class
    is intended to provide functionality for unordered list comparisons, particularly useful when
    order does not hold significance in operations like equality checks.
    """
    def __eq__(self, other):
        self_copy = copy.copy(self)
        other_copy = copy.copy(other)

        return self_copy.sort() == other_copy.sort()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        origin = get_origin(source_type)
        if origin is cls:  # handles both bare UnorderedList and UnorderedList[T]
            args = get_args(source_type)
            if args:
                # Use handler.generate_schema(...) to avoid the recursion warning
                item_schema = handler.generate_schema(args[0])
                return core_schema.list_schema(item_schema)

            return core_schema.list_schema(handler.generate_schema(Any))

        # Fallback for unexpected cases
        return handler.generate_schema(list)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return handler(core_schema.list_schema(core_schema.any_schema()))
