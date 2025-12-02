from typing import Any
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler


# pylint: disable-next=invalid-name
class _NOT_DEFINABLE_TYPE:
    """
    Type for NON_DEFINABLE values. This object is assigned for all fields that are unable to define either by user or
    by data interacting features.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_NOT_DEFINABLE_TYPE, cls).__new__(cls)
        return cls._instance

    def __repr__(self):
        return "NON_DEFINABLE"

    def __eq__(self, other):
        return isinstance(other, _NOT_DEFINABLE_TYPE)

    def __hash__(self):
        return hash(type(self))

    @classmethod
    # pylint: disable-next=unused-argument
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        """
        as it is a singleton class - checking to be a instance is enough
        """
        return core_schema.is_instance_schema(cls)


NOT_DEFINABLE = _NOT_DEFINABLE_TYPE()
