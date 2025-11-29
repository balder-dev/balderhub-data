from __future__ import annotations
from typing import List, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .filter import Filter
    from .single_data_item import SingleDataItem


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
        """
        This method applies a filter to all items in the collection
        :param filter_obj:
        :return:
        """
        if filter_obj is None:
            return self.__class__(self._items)

        remaining_items = []
        for item in self._items:
            if filter_obj.apply(item):
                remaining_items.append(item)
        return self.__class__(remaining_items)

    def sort(self, key: Callable = None, reverse: bool = False) -> SingleDataItemCollection:
        """
        This method sorts the items in the collection according to the given key.
        :param key: a sorting callable
        :param reverse: True if the order should be reversed, otherwise False
        :return: a new SingleDataItemCollection instance with the sorted items
        """
        items = self._items.copy()
        items.sort(key=key, reverse=reverse)
        return SingleDataItemCollection(items)

    def copy(self):
        """
        This method returns a new SingleDataItemCollection instance with the same items.

        .. note::
            The inner items will not be copied.

        :return: the copied SingleDataItemCollection instance
        """
        return SingleDataItemCollection([*self._items])

    def get_all_unique_identifier(self):
        """
        This method returns a list with all unique-identification values (provided by
        :meth:`SingleDataItem.get_unique_identification()`) of the items.

        :return: the unique-identification values
        """
        return [item.get_unique_identification() for item in self._items]

    def has_unique_elements(self) -> bool:
        """
        :return: returns True if all items within the collection are unique (identified by
                 :meth:`SingleDataItem.get_unique_identification()`)
        """
        return len(self._items) == len(set(self.get_all_unique_identifier()))

    def get_by_identifier(self, identifier: Any):
        """
        This method returns a specific element by its unique identifier. It throws an error in case there are more than
        one element with this unique-identifier or if there are no elements with this unique-identifier.

        :param identifier: the unique identifier
        :return: the determined object
        """
        remaining = [item for item in self._items if item.get_unique_identification() == identifier]
        if len(remaining) == 0:
            raise KeyError(f'no items with identifier `{identifier}` exists')
        if len(remaining) > 1:
            raise KeyError(f'multiple items with identifier `{identifier}` exists')
        return remaining[0]

    def append(self, item: SingleDataItem) -> None:
        """
        This method adds an item to the collection.
        :param item: the item that should be added
        """
        self._items.append(item)

    def remove(self, item: SingleDataItem) -> None:
        """
        This method removes an item from the collection.
        :param item: the item that should be removed
        """
        self._items.remove(item)

    def get_difference_error_messages(
            self,
            other_collection: SingleDataItemCollection,
            ignore_order: bool = False,
            ignore_field_lookups: List[str] = None,
            allow_non_definable: bool = False,
    ) -> List[str]:
        """
        This method returns a list with all error messages that has been returned by comparing the list elements with
        each other.

        :param other_collection: the other collection to compare with
        :param ignore_order: True if the order does not matter and the method should match the elements by its unique
                             identifier
        :param ignore_field_lookups: a list with field-lookups that should be ignored while comparing the items
        :param allow_non_definable: True if the method should ignore fields for which one data item has the value
                                    `NOT_DEFINABLE`
        :return: a list of error messages (empty list if the collection is identically)
        """
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
        """
        This method returns True if the collections are the same

        :param other_collection: the other collection to compare with
        :param ignore_order: True if the order does not matter and the method should match the elements by its unique
                             identifier
        :param ignore_field_lookups: a list with field-lookups that should be ignored while comparing the items
        :param allow_non_definable: True if the method should ignore fields for which one data item has the value
                                    `NOT_DEFINABLE`
        :return: True if the collection is the same, otherwise False
        """
        return not bool(
            self.get_difference_error_messages(
                other_collection,
                ignore_order=ignore_order,
                ignore_field_lookups=ignore_field_lookups,
                allow_non_definable=allow_non_definable
            )
        )
