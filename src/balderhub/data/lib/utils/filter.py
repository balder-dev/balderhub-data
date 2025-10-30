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
        pass
