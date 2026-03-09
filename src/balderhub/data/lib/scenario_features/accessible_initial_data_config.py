from ..utils.single_data_item_collection import SingleDataItemCollection
from .initial_data_config import InitialDataConfig


class AccessibleInitialDataConfig(InitialDataConfig):
    """
    This config feature returns a list of data item elements, that is accessible for the using device.
    """

    @property
    def data_list(self) -> SingleDataItemCollection:
        """
        :return: returns the data item collection this config feature describes
        """
        raise NotImplementedError()
