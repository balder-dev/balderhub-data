from __future__ import annotations
from typing import List

import random

from balderhub.data.lib.utils import SingleDataItemCollection
from balderhub.data.lib.utils.abstract_data_item_related_feature import AbstractDataItemRelatedFeature
from balderhub.data.lib.utils.single_data_item import SingleDataItemType



class MultipleDataConfig(AbstractDataItemRelatedFeature):

    class DoesNotExist(Exception):
        pass

    class MultipleElementsReturned(Exception):
        pass

    @property
    def data_list(self) -> SingleDataItemCollection:
        raise NotImplementedError()

    def get_for_identifier(self, identifier) -> SingleDataItemType | None:
        # TODO remove here and add in SingleDataItemCollection!

        elems = [e for e in self.data_list if e.get_unique_identification() == identifier]
        if len(elems) == 0:
            return None
        if len(elems) > 1:
            raise ValueError(f'found more than one elements with identifier {identifier}')
        return elems[0]

    def filter_by(self, **kwargs) -> List[SingleDataItemType]:
        # TODO remove here and add in SingleDataItemCollection!

        result = []
        for cur_elem in self.data_list:
            match = True
            for name, value in kwargs.items():
                if getattr(cur_elem, name) != value:
                    match = False
                    break
            if match:
                result.append(cur_elem)
        return result

    def get_by(self, **kwargs) -> List[SingleDataItemType]:
        # TODO remove here and add in SingleDataItemCollection!
        result = self.filter_by(**kwargs)
        if len(result) == 0:
            raise self.DoesNotExist(f'can not find a item for given filter attributes `{kwargs}`')
        if len(result) > 1:
            raise self.MultipleElementsReturned(f"found more than one element for given filter attributes `{kwargs}` - "
                                                f"use `filter_by()` if you want to retrieve multiple objects")
        return result[0]

    def get_random(self) -> SingleDataItemType:
        # TODO remove here and add in SingleDataItemCollection!
        return random.choice(self.data_list)
