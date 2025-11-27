from __future__ import annotations
from typing import List, Any, Callable
from balderhub.data.lib.utils import SingleDataItem
from balderhub.data.lib.utils.filter import Filter


class SingleDataItemCollection:
    """
    helper class to manage a collection of SingleDateItems
    """

    def __init__(self, items: List[SingleDataItem]):
        self._items = items

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def filter(self, filter_obj: Filter | None) -> SingleDataItemCollection:
        if filter_obj is None:
            return self.__class__(self._items)

        remaining_items = []
        for item in self._items:
            if filter_obj.apply(item):
                remaining_items.append(item)
        return self.__class__(remaining_items)

    def sort(self, key: Callable = None, reverse: bool = False) -> SingleDataItemCollection:
        items = self._items.copy()
        items.sort(key=key, reverse=reverse)
        return SingleDataItemCollection(items)

    def copy(self):
        return SingleDataItemCollection([*self._items])

    def get_all_unique_identifier(self):
        return [item.get_unique_identification() for item in self._items]

    def has_unique_elements(self) -> bool:
        return len(self._items) == len(set(self.get_all_unique_identifier()))

    def get_by_identifier(self, identifier: Any):
        remaining = [item for item in self._items if item.get_unique_identification() == identifier]
        if len(remaining) == 0:
            raise KeyError(f'no items with identifier `{identifier}` exists')
        if len(remaining) > 1:
            raise KeyError(f'multiple items with identifier `{identifier}` exists')
        return remaining[0]

    def append(self, item: SingleDataItem):
        self._items.append(item)

    def remove(self, item: SingleDataItem):
        self._items.remove(item)

    def get_difference_error_messages(
            self,
            other_collection: SingleDataItemCollection,
            ignore_order: bool = False,
            ignore_field_lookups: List[str] = None,
            allow_non_definable: bool = False,
    ) -> List[str]:
        if len(self) != len(other_collection):
            return [f'list have different lengths (self: {len(self)} | other: {len(other_collection)})']
        if ignore_order:
            self_copy = self.sort(key=lambda e: e.get_unique_identification())
            other_copy = other_collection.sort(key=lambda e: e.get_unique_identification())
        else:
            self_copy = self.copy()
            other_copy = other_collection.copy()

        result = []
        for idx in range(len(self)):
            cur_self = self_copy[idx]
            cur_other = other_copy[idx]
            result.extend(cur_self.get_difference_error_messages(
                cur_other,
                ignore_field_lookups,
                allow_non_definable=allow_non_definable)
            )
        return result

    def compare(
            self,
            other_collection: SingleDataItemCollection,
            ignore_order: bool = False,
            ignore_field_lookups: List[str] = None,
            allow_non_definable: bool = False,
    ) -> bool:
        return not bool(
            self.get_difference_error_messages(
                other_collection,
                ignore_order=ignore_order,
                ignore_field_lookups=ignore_field_lookups,
                allow_non_definable=allow_non_definable
            )
        )
