from .abstract_data_item_related_feature import AbstractDataItemRelatedFeature

from ..utils.single_data_item import SingleDataItemTypeT
from ..utils.single_data_item_collection import SingleDataItemCollection


class MultipleDataConfig(AbstractDataItemRelatedFeature):
    """
    This config feature returns a list of data item elements.
    """

    class DoesNotExist(Exception):
        """
        raised in case that the requested data item does not exist
        """

    class MultipleElementsReturned(Exception):
        """
        raised in case there are more than one matching elements in the list
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

    def get_by(self, **kwargs) -> list[SingleDataItemTypeT]:
        # TODO remove here and add in SingleDataItemCollection!
        result = self.filter_by(**kwargs)
        if len(result) == 0:
            raise self.DoesNotExist(f'can not find a item for given filter attributes `{kwargs}`')
        if len(result) > 1:
            raise self.MultipleElementsReturned(f"found more than one element for given filter attributes `{kwargs}` - "
                                                f"use `filter_by()` if you want to retrieve multiple objects")
        return result[0]
