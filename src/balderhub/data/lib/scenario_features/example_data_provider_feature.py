from typing import List
import dataclasses

import balderhub.data.lib.utils
from balderhub.data.lib.utils import ResponseMessageList
from balderhub.data.lib.utils.abstract_data_item_related_feature import AbstractDataItemRelatedFeature


class ExampleDataProviderFeature(AbstractDataItemRelatedFeature):

    @dataclasses.dataclass
    class NamedExample:
        name: str
        data: balderhub.data.lib.utils.SingleDataItem
        expected_response_messages: ResponseMessageList = ResponseMessageList()

        def __str__(self):
            return f"Example<{self.data.__class__.__name__}: {self.name}>"

    def get_valid_examples(self) -> List[NamedExample]:
        raise NotImplementedError

    def get_invalid_examples(self) -> List[NamedExample]:
        raise NotImplementedError
