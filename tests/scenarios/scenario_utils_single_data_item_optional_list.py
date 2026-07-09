from typing import Optional

from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.single_data_item import SingleDataItem


# Test data item classes for testing purposes
class SimpleDataItem(SingleDataItem):
    name: str
    value: int
    
    def get_unique_identification(self):
        return f"{self.name}_{self.value}"


class OptionalNestedSingleRef(SingleDataItem):
    name: str
    optional_single_data_item: Optional[SimpleDataItem] = None
    optional_list_of_single_data_items: Optional[list[SimpleDataItem]] = None

    def get_unique_identification(self):
        return self.name


class ScenarioUtilsSingleDataItemOptionalList(ScenarioUnit):
    """Unittests for SingleDataItem class."""

    def test_type_determination(self):
        elem = OptionalNestedSingleRef.get_field_data_type('optional_single_data_item')
        assert elem is SimpleDataItem, elem

        elem = OptionalNestedSingleRef.get_field_data_type('optional_list_of_single_data_items')
        assert elem is list

        elem = OptionalNestedSingleRef.get_element_type_for_list('optional_list_of_single_data_items')
        assert elem is SimpleDataItem, elem

    def test_create_without_anything(self):
        item = OptionalNestedSingleRef.create_as_nested(name="test")
        assert item.name == "test"
        assert item.optional_single_data_item is None
        assert item.optional_list_of_single_data_items is None

    def test_create_empty_optional_list(self):
        item = OptionalNestedSingleRef.create_as_nested(name="test", optional_list_of_single_data_items=[])
        assert item.name == "test"
        assert item.optional_single_data_item is None
        assert item.optional_list_of_single_data_items == []

    def test_create_with_list(self):
        list_to_create = [
            SimpleDataItem(name='test', value=1),
            SimpleDataItem(name='test2', value=2),
        ]
        item = OptionalNestedSingleRef.create_as_nested(name="test", optional_list_of_single_data_items=list_to_create)
        assert item.name == "test"
        assert item.optional_single_data_item is None
        assert item.optional_list_of_single_data_items == list_to_create
