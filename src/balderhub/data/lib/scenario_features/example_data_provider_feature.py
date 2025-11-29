import dataclasses

from balderhub.data.lib.scenario_features.abstract_data_item_related_feature import AbstractDataItemRelatedFeature

from ..utils.response_message_list import ResponseMessageList
from ..utils.single_data_item import SingleDataItem


class ExampleDataProviderFeature(AbstractDataItemRelatedFeature):
    """
    This feature provides full example data for a specific single data item.
    """

    @dataclasses.dataclass
    class NamedExample:
        """internal data class that describes an example"""
        name: str
        data: SingleDataItem
        expected_response_messages: ResponseMessageList = ResponseMessageList()

        def __str__(self):
            return f"Example<{self.data.__class__.__name__}: {self.name}>"

    def get_valid_examples(self) -> list[NamedExample]:
        """
        :return: returns a list of valid examples
        """
        raise NotImplementedError

    def get_invalid_examples(self) -> list[NamedExample]:
        """
        :return: returns a list of invalid examples
        """
        raise NotImplementedError
