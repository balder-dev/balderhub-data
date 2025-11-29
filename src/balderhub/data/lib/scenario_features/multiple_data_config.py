from .abstract_data_item_related_feature import AbstractDataItemRelatedFeature

from ..utils.single_data_item import SingleDataItemTypeT
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

    def get_for_identifier(self, identifier) -> SingleDataItemTypeT | None:
        # TODO remove here and add in SingleDataItemCollection!

        elems = [e for e in self.data_list if e.get_unique_identification() == identifier]
        if len(elems) == 0:
            return None
        if len(elems) > 1:
            raise ValueError(f'found more than one elements with identifier {identifier}')
        return elems[0]


