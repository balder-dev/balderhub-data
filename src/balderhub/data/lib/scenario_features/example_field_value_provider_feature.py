from typing import Any
import dataclasses

from .abstract_data_item_related_feature import AbstractDataItemRelatedFeature
from ..utils.response_message_list import ResponseMessageList
from ..utils.single_data_item import SingleDataItem


class ExampleFieldValueProviderFeature(AbstractDataItemRelatedFeature):
    """
    This feature provides example data for specific fields of a data item.
    """

    @dataclasses.dataclass
    class NamedExample:
        """internal data class that describes an example"""
        name: str
        field_name: str
        new_field_value: Any
        expected_response_messages: ResponseMessageList = ResponseMessageList()

        def __str__(self):
            return f"FieldValueExample<{self.field_name}: {self.name}>"

    def get_valid_new_value_for_field(self, data_item: SingleDataItem, field: str) -> list[NamedExample]:
        """
        This method returns valid example data for a specific field of an existing data item instance. This will be
        called for change requests of a specific field of an existing data item.

        :param data_item: the current data
        :param field: the field name that should be changed
        :return: the new value for the field
        """
        raise NotImplementedError

    def get_invalid_new_value_for_field(self, data_item: SingleDataItem, field: str) -> list[NamedExample]:
        """
        This method returns invalid example data for a specific field of an existing data item instance. This will be
        called for change requests of a specific field of an existing data item. It will be expected, that it is not
        possible to set the provided value in the app-under-test.

        :param data_item: the current data
        :param field: the field name that should be changed
        :return: the new value for the field
        """
        raise NotImplementedError
