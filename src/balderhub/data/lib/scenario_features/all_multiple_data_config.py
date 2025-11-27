from .multiple_data_config import MultipleDataConfig
from ..utils import SingleDataItemCollection


class AllMultipleDataConfig(MultipleDataConfig):
    """
    Specific scenario feature config that describes the available data of a data item type
    """

    @property
    def data_list(self) -> SingleDataItemCollection:
        raise NotImplementedError()
