from typing import Optional

from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib.utils.single_data_item_collection import SingleDataItemCollection
from balderhub.data.lib.utils.not_definable import NOT_DEFINABLE
from balderhub.data.lib.utils.filter import Filter


# Test data item classes for testing purposes
class SimpleItem(SingleDataItem):
    name: str
    value: int
    
    def get_unique_identification(self):
        return f"{self.name}_{self.value}"


class NestedItem(SingleDataItem):
    id: int
    simple: SimpleItem
    
    def get_unique_identification(self):
        return self.id


class OptionalItem(SingleDataItem):
    name: str
    optional_field: Optional[str]
    
    def get_unique_identification(self):
        return self.name


class ScenarioUtilsSingleDataItemCollection(ScenarioUnit):
    """Unit-like tests for SingleDataItemCollection class."""

    def test_init_empty(self):
        collection = SingleDataItemCollection()
        assert len(collection) == 0
        assert not collection

    def test_init_with_items(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        assert len(collection) == 2
        assert bool(collection)

    def test_repr(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1])
        assert repr(collection) == "SingleDataItemCollection(items=[SimpleItem(name='test1', value=1)])", repr(collection)

    def test_bool_non_empty_is_true(self):
        item = SimpleItem.create_as_nested(name="test", value=1)
        collection = SingleDataItemCollection([item])
        assert bool(collection)

    def test_iter(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        items = list(collection)
        assert len(items) == 2
        assert items[0] == item1
        assert items[1] == item2

    def test_filter_with_none_returns_copy(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        filtered = collection.filter(None)
        assert len(filtered) == 2
        assert filtered is not collection

    def test_filter_with_filter_object(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        
        # Create a simple filter that matches item1
        class TestFilter(Filter):
            def apply(self, item: SimpleItem) -> bool:
                return item.name == "test1"
        
        filtered = collection.filter(TestFilter())
        assert len(filtered) == 1
        assert filtered[0] == item1

    def test_sort_default(self):
        item1 = SimpleItem.create_as_nested(name="b", value=2)
        item2 = SimpleItem.create_as_nested(name="a", value=1)
        collection = SingleDataItemCollection([item1, item2])
        sorted_collection = collection.sort(key=lambda x: x.name)
        assert sorted_collection[0].name == "a"
        assert sorted_collection[1].name == "b"

    def test_sort_reverse(self):
        item1 = SimpleItem.create_as_nested(name="a", value=1)
        item2 = SimpleItem.create_as_nested(name="b", value=2)
        collection = SingleDataItemCollection([item1, item2])
        sorted_collection = collection.sort(key=lambda x: x.name, reverse=True)
        assert sorted_collection[0].name == "b"
        assert sorted_collection[1].name == "a"

    def test_sort_returns_new_instance(self):
        item1 = SimpleItem.create_as_nested(name="b", value=2)
        item2 = SimpleItem.create_as_nested(name="a", value=1)
        collection = SingleDataItemCollection([item1, item2])
        sorted_collection = collection.sort(key=lambda x: x.name)
        assert sorted_collection is not collection
        assert collection[0].name == "b"  # Original unchanged
        assert collection[1].name == "a"  # Original unchanged

        # new one is sorted now
        assert sorted_collection[0].name == "a"
        assert sorted_collection[1].name == "b"

    def test_copy_creates_new_instance(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1])
        copied = collection.copy()
        assert copied is not collection
        assert len(copied) == len(collection)
        assert copied == collection

    def test_copy_shares_items(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1])
        copied = collection.copy()
        assert copied[0] is collection[0]

    def test_copy_modification_does_not_affect_original(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1])
        copied = collection.copy()
        copied.append(item2)
        assert len(collection) == 1
        assert len(copied) == 2

    def test_get_all_unique_identifier(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        identifiers = collection.get_all_unique_identifier()
        assert identifiers == ["test1_1", "test2_2"]

    def test_has_unique_elements_true(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        assert collection.has_unique_elements()

    def test_has_unique_elements_false_with_duplicates(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1, item2])
        assert not collection.has_unique_elements()

    def test_has_unique_elements_false_with_duplicates_of_same_ref(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1, item1])
        assert not collection.has_unique_elements()

    def test_get_by_identifier_success(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        result = collection.get_by_identifier("test1_1")
        assert result == item1
        result = collection.get_by_identifier("test2_2")
        assert result == item2

    def test_get_by_identifier_raises_key_error_if_not_found(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1])
        try:
            collection.get_by_identifier("nonexistent")
            assert False, "KeyError expected"
        except KeyError as exc:
            assert exc.args[0] == "no items with identifier `nonexistent` exists", exc

    def test_get_by_identifier_raises_key_error_if_multiple(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1, item2])
        try:
            collection.get_by_identifier("test1_1")
            assert False, "KeyError expected"
        except KeyError as exc:
            assert exc.args[0] == "multiple items with identifier `test1_1` exists", exc

    def test_filter_by_single_field(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        filtered = collection.filter_by(name="test1")
        assert len(filtered) == 1
        assert filtered[0] == item1

    def test_filter_by_multiple_fields(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=2)
        item3 = SimpleItem.create_as_nested(name="test2", value=1)
        collection = SingleDataItemCollection([item1, item2, item3])
        filtered = collection.filter_by(name="test1", value=1)
        assert len(filtered) == 1
        assert filtered[0] == item1

    def test_filter_by_nested_field(self):
        nested1 = NestedItem.create_as_nested(id=1, simple__name="test1", simple__value=10)
        nested2 = NestedItem.create_as_nested(id=2, simple__name="test2", simple__value=20)
        collection = SingleDataItemCollection([nested1, nested2])
        filtered = collection.filter_by(simple__name="test1")
        assert len(filtered) == 1
        assert filtered[0] == nested1

    def test_filter_by_no_matches(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1])
        filtered = collection.filter_by(name="nonexistent")
        assert len(filtered) == 0

    def test_get_by_success(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        result = collection.get_by(name="test1")
        assert result == item1

    def test_get_by_raises_does_not_exist(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection = SingleDataItemCollection([item1])
        try:
            collection.get_by(name="nonexistent")
            assert False, "DoesNotExist expected"
        except SingleDataItemCollection.DoesNotExist as exc:
            assert exc.args[0] == "can not find a item for given filter attributes `{'name': 'nonexistent'}`", exc

    def test_get_by_raises_multiple_elements_returned(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=2)
        collection = SingleDataItemCollection([item1, item2])
        try:
            collection.get_by(name="test1")
            assert False, "MultipleElementsReturned expected"
        except SingleDataItemCollection.MultipleElementsReturned as exc:
            assert exc.args[0] == ("found more than one element for given filter attributes `{'name': 'test1'}` "
                                   "- use `filter_by()` if you want to retrieve multiple objects"), exc

    def test_get_random(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        result = collection.get_random()
        assert result in [item1, item2]

    def test_append(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1])
        collection.append(item2)
        assert len(collection) == 2
        assert collection[0] == item1
        assert collection[1] == item2

    def test_remove(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection = SingleDataItemCollection([item1, item2])
        collection.remove(item1)
        assert len(collection) == 1
        assert collection[0] == item2

    def test_get_difference_error_messages_empty_collections(self):
        collection1 = SingleDataItemCollection()
        collection2 = SingleDataItemCollection()
        errors = collection1.get_difference_error_messages(collection2)
        assert len(errors) == 0

    def test_get_difference_error_messages_different_lengths(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection()
        errors = collection1.get_difference_error_messages(collection2)
        assert len(errors) == 1, errors
        assert errors[0] == "list have different lengths (self: 1 | other: 0)", errors

    def test_get_difference_error_messages_identical_collections(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=1)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        errors = collection1.get_difference_error_messages(collection2)
        assert len(errors) == 0

    def test_get_difference_error_messages_different_items(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        errors = collection1.get_difference_error_messages(collection2)
        assert len(errors) == 3, errors
        assert errors[0] == "detect different unique identification key - self: `test1_1` | other: `test2_2`", errors
        assert errors[1] == "detect different value for dataclass field `name` - self: `test1` | other: `test2`", errors
        assert errors[2] == "detect different value for dataclass field `value` - self: `1` | other: `2`", errors

    def test_get_difference_error_messages_ignore_order(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection1 = SingleDataItemCollection([item1, item2])
        collection2 = SingleDataItemCollection([item2, item1])
        errors = collection1.get_difference_error_messages(collection2, ignore_order=True)
        assert len(errors) == 0

    def test_get_difference_error_messages_order_matters(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection1 = SingleDataItemCollection([item1, item2])
        collection2 = SingleDataItemCollection([item2, item1])
        errors = collection1.get_difference_error_messages(collection2, ignore_order=False)
        assert len(errors) == 6, errors
        assert errors[0] == "detect different unique identification key - self: `test1_1` | other: `test2_2`", errors
        assert errors[1] == "detect different value for dataclass field `name` - self: `test1` | other: `test2`", errors
        assert errors[2] == "detect different value for dataclass field `value` - self: `1` | other: `2`", errors
        assert errors[3] == "detect different unique identification key - self: `test2_2` | other: `test1_1`", errors
        assert errors[4] == "detect different value for dataclass field `name` - self: `test2` | other: `test1`", errors
        assert errors[5] == "detect different value for dataclass field `value` - self: `2` | other: `1`", errors

    def test_get_difference_error_messages_ignore_field_lookups(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=999)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        errors = collection1.get_difference_error_messages(collection2, ignore_field_lookups=["value"], )
        assert len(errors) == 1, errors
        assert errors[0] == "detect different unique identification key - self: `test1_1` | other: `test1_999`", errors
        # but no error for difference in value

    def test_get_difference_error_messages_allow_non_definable(self):
        item1 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedItem.create_as_nested(id=1, simple=NOT_DEFINABLE)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        errors = collection1.get_difference_error_messages(collection2, allow_non_definable=True)
        assert len(errors) == 0, errors

    def test_get_difference_error_messages_allow_non_definable_nested(self):
        item1 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=NOT_DEFINABLE)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        errors = collection1.get_difference_error_messages(collection2, allow_non_definable=True)
        assert len(errors) == 0, errors

    def test_compare_empty_collections(self):
        collection1 = SingleDataItemCollection()
        collection2 = SingleDataItemCollection()
        assert collection1.compare(collection2)

    def test_compare_identical_collections(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test1", value=1)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        assert collection1.compare(collection2)

    def test_compare_different_collections(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        assert not collection1.compare(collection2)

    def test_compare_ignore_order(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection1 = SingleDataItemCollection([item1, item2])
        collection2 = SingleDataItemCollection([item2, item1])
        assert collection1.compare(collection2, ignore_order=True)

    def test_compare_order_matters(self):
        item1 = SimpleItem.create_as_nested(name="test1", value=1)
        item2 = SimpleItem.create_as_nested(name="test2", value=2)
        collection1 = SingleDataItemCollection([item1, item2])
        collection2 = SingleDataItemCollection([item2, item1])
        assert not collection1.compare(collection2, ignore_order=False)

    def test_compare_ignore_field_lookups(self):
        item1 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=52)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        assert collection1.compare(collection2, ignore_field_lookups=["simple"])

    def test_compare_ignore_field_lookups_nested(self):
        item1 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=52)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        assert collection1.compare(collection2, ignore_field_lookups=["simple__value"])

    def test_compare_allow_non_definable(self):
        item1 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedItem.create_as_nested(id=1, simple=NOT_DEFINABLE)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        assert collection1.compare(collection2, allow_non_definable=True)

    def test_compare_allow_non_definable_nested(self):
        item1 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedItem.create_as_nested(id=1, simple__name="Hello World", simple__value=NOT_DEFINABLE)
        collection1 = SingleDataItemCollection([item1])
        collection2 = SingleDataItemCollection([item2])
        assert collection1.compare(collection2, allow_non_definable=True)
