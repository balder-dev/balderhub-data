import dataclasses

import balderhub.data.lib.utils
from balderhub.data.lib.utils import SingleDataItem, ResponseMessageList
from balderhub.data.lib.utils.abstract_data_item_related_feature import AbstractDataItemRelatedFeature


class ExampleFieldValueProviderFeature(AbstractDataItemRelatedFeature):

    @dataclasses.dataclass
    class NamedExample:
        name: str
        field_name: str
        new_field_value: balderhub.data.lib.utils.SingleDataItem
        expected_response_messages: ResponseMessageList = ResponseMessageList()

        def __str__(self):
            return f"FieldValueExample<{self.field_name}: {self.name}>"

    def get_valid_new_value_for_field(self, data_item: SingleDataItem, field: str) -> list[NamedExample]:
        raise NotImplementedError

    def get_invalid_new_value_for_field(self, data_item: SingleDataItem, field: str) -> list[NamedExample]:
        raise NotImplementedError
