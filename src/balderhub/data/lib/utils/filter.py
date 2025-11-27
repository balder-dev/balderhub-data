from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from balderhub.data.lib.utils.single_data_item import SingleDataItem

T = TypeVar('T', bound=SingleDataItem)


class Filter(ABC):
    """
    Object allows to define filter for a specific data class
    """

    @abstractmethod
    def apply(self, item: T) -> bool:
        """
        Method that executes the filtering. It will be called for every list element and should return True if the
        element is still part of the list or False if it is not part of the list.
        :param item: the current item
        :return: True if the item should be added to the filtered result, otherwise False
        """
