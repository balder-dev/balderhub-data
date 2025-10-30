from balderhub.data.lib.utils.abstract_data_item_related_feature import AbstractDataItemRelatedFeature
from balderhub.data.lib.utils.single_data_item import SingleDataItem


class SingleDataConfig(AbstractDataItemRelatedFeature):

    @property
    def data_item(self) -> SingleDataItem:
        raise NotImplementedError()
