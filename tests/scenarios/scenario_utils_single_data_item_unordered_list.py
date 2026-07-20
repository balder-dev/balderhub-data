from typing import Optional
from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils import SingleDataItem, UnorderedList


# Test data item classes for testing purposes
class SimpleDataItem(SingleDataItem):
    name: str
    value: int

    def get_unique_identification(self):
        return f"{self.name}_{self.value}"


class NestedSingleRef(SingleDataItem):
    name: str
    unsorted_list: UnorderedList[int]
    unsorted_list_of_single_data_items: UnorderedList[SimpleDataItem]
    optional_list_of_single_data_items: Optional[UnorderedList[SimpleDataItem]] = None

    def get_unique_identification(self):
        return self.name


class ScenarioUtilsSingleDataItemUnsortedList(ScenarioUnit):
    """Unittests for SingleDataItem class."""

    def test_compare(self):
        a_1 = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 2, 3]),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        a_2 = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 2, 3]),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        b = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 3, 2]),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        assert a_1.compare(a_2), a_1.get_difference_error_messages(a_2)

        assert a_1.compare(b), a_1.get_difference_error_messages(b)
        assert a_2.compare(b), a_2.get_difference_error_messages(b)

    def test_compare_dataitems(self):
        a = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 2, 3]),
            unsorted_list_of_single_data_items=UnorderedList([
                SimpleDataItem(name='a', value=1),
                SimpleDataItem(name='b', value=2),
                SimpleDataItem(name='c', value=3),
            ])
        )
        b = NestedSingleRef(
            name='a', unsorted_list=UnorderedList([1, 3, 2]),
            unsorted_list_of_single_data_items=UnorderedList([
                SimpleDataItem(name='a', value=1),
                SimpleDataItem(name='c', value=3),
                SimpleDataItem(name='b', value=2),
            ])
        )

        assert a.compare(b), a.get_difference_error_messages(b)

    def test_compare_empty_lists(self):
        a = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList(),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        b = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList(),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        assert a.compare(b), a.get_difference_error_messages(b)

    def test_optional_unsorted_list(self):

        a = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1]),
            unsorted_list_of_single_data_items=UnorderedList(),
            optional_list_of_single_data_items=UnorderedList([SimpleDataItem(name='x', value=1)])
        )
        b = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1]),
            unsorted_list_of_single_data_items=UnorderedList(),
            optional_list_of_single_data_items=UnorderedList([SimpleDataItem(name='x', value=1)])
        )
        assert a.compare(b), a.get_difference_error_messages(b)

    def test_compare_inequality(self):
        a = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 2, 3]),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        b = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 2, 4]),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        c = NestedSingleRef(
            name='a',
            unsorted_list=UnorderedList([1, 2, 3, 4]),
            unsorted_list_of_single_data_items=UnorderedList()
        )
        assert a.get_difference_error_messages(b) == ['unsorted_list[2]: detect different value - self: `[1, 2, 3]` | other: `[1, 2, 4]`'], a.get_difference_error_messages(b)
        assert a.get_difference_error_messages(c) == ['unsorted_list: detect different list length - self=3, other=4'], a.get_difference_error_messages(c)
        assert b.get_difference_error_messages(c) == ['unsorted_list: detect different list length - self=3, other=4'], b.get_difference_error_messages(c)


    def test_get_element_type_for(self):
        assert NestedSingleRef.get_field_data_type('unsorted_list') == UnorderedList
        assert NestedSingleRef.get_element_type_for_list('unsorted_list') == int
        assert NestedSingleRef.get_element_type_for_list('unsorted_list_of_single_data_items') == SimpleDataItem
