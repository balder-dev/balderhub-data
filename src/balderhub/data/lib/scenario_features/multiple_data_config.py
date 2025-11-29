from .abstract_data_item_related_feature import AbstractDataItemRelatedFeature
from ..utils.single_data_item_collection import SingleDataItemCollection


class MultipleDataConfig(AbstractDataItemRelatedFeature):
    """
    This config feature returns a list of data item elements.
    """

    @property
    def data_list(self) -> SingleDataItemCollection:
        """
        :return: returns the data item collection this config feature describes
        """
        raise NotImplementedError()
