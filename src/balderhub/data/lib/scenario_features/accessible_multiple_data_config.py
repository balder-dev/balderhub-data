from .multiple_data_config import MultipleDataConfig
from ..utils import SingleDataItemCollection


class AccessibleMultipleDataConfig(MultipleDataConfig):
    """
    Specific scenario feature config that describes the accessible subset of the full available data
    """

    @property
    def data_list(self) -> SingleDataItemCollection:
        raise NotImplementedError()
