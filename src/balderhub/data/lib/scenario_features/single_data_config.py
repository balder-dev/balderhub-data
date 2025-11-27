from balderhub.data.lib.utils.abstract_data_item_related_feature import AbstractDataItemRelatedFeature
from balderhub.data.lib.utils.single_data_item import SingleDataItem


class SingleDataConfig(AbstractDataItemRelatedFeature):
    """
    This config feature provides information for a single data item element of its specific data item type.
    """
    # TODO maybe we can eliminate these kind of features??

    @property
    def data_item(self) -> SingleDataItem:
        """
        :return: the specific data item
        """
        raise NotImplementedError()
