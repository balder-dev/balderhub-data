from typing import Optional

import pydantic
from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib.utils.not_definable import NOT_DEFINABLE
from balderhub.data.lib.utils.lookup_field_string import LookupFieldString
from balderhub.data.lib.utils.exceptions import MisconfiguredDataItemError


# Test data item classes for testing purposes
class SimpleDataItem(SingleDataItem):
    name: str
    value: int
    
    def get_unique_identification(self):
        return f"{self.name}_{self.value}"


class NestedDataItem(SingleDataItem):
    id: int
    simple: SimpleDataItem
    
    def get_unique_identification(self):
        return self.id


class ComplexDataItem(SingleDataItem):
    title: str
    count: int
    optional_field: Optional[str]
    nested: NestedDataItem
    
    def get_unique_identification(self):
        return self.title


class ListDataItem(SingleDataItem):
    items: list[int]
    nested_items: list[SimpleDataItem]
    
    def get_unique_identification(self):
        return len(self.items)


class ScenarioUtilsSingleDataItem(ScenarioUnit):
    """Unittests for SingleDataItem class."""

    def test_create_as_nested_simple(self):
        item = SimpleDataItem.create_as_nested(name="test", value=42)
        assert item.name == "test"
        assert item.value == 42

    def test_create_as_nested_with_lookup_fields(self):
        item = NestedDataItem.create_as_nested(id=1, simple__name="test", simple__value=99)
        assert item.id == 1
        assert item.simple.name == "test"
        assert item.simple.value == 99

    def test_create_non_definable_nested_true(self):
        item = SimpleDataItem.create_non_definable(nested=True)
        assert item.name == NOT_DEFINABLE
        assert item.value == NOT_DEFINABLE

        item = NestedDataItem.create_non_definable(nested=True)
        assert item.id == NOT_DEFINABLE
        # Nested field shouldn't be NOT_DEFINABLE - should be a object with NOT_DEFINABLEs
        assert isinstance(item.simple, SimpleDataItem)
        assert item.simple.name == NOT_DEFINABLE
        assert item.simple.value == NOT_DEFINABLE

    def test_create_non_definable_nested_false(self):
        item = NestedDataItem.create_non_definable(nested=False)
        assert item.id == NOT_DEFINABLE
        # Nested field should be NOT_DEFINABLE, not a nested non-definable object
        assert item.simple == NOT_DEFINABLE

    def test_get_field_simple(self):
        field_info = SimpleDataItem.get_field("name")
        assert field_info is not None
        assert field_info.annotation is not None

    def test_get_field_nested_lookup(self):
        field_info = NestedDataItem.get_field("simple__name")
        assert field_info is not None

    def test_get_field_with_lookup_field_string(self):
        lfs = LookupFieldString("simple__value")
        field_info = NestedDataItem.get_field(lfs)
        assert field_info is not None

    def test_get_field_missing_raises_key_error(self):
        try:
            SimpleDataItem.get_field("nonexistent")
            assert False, "KeyError expected for missing field"
        except KeyError as exc:
            assert exc.args[0] == "can not find a field `nonexistent` in data item `SimpleDataItem`", str(exc)

    def test_get_field_nested_missing_raises_key_error(self):
        try:
            NestedDataItem.get_field("simple__nonexistent")
            assert False, "KeyError expected for missing nested field"
        except KeyError as exc:
            assert exc.args[0] == "can not find a field `nonexistent` in data item `SimpleDataItem`", str(exc)

    def test_is_optional_field_true(self):
        assert ComplexDataItem.is_optional_field("optional_field") is True

    def test_is_optional_field_false(self):
        assert ComplexDataItem.is_optional_field("title") is False

    def test_is_optional_field_nested(self):
        # Test nested field optional checking
        result = ComplexDataItem.is_optional_field("nested__simple__name")
        assert result is False

    def test_get_element_type_for_list(self):
        elem_type = ListDataItem.get_element_type_for_list("items")
        assert elem_type is int

    def test_get_element_type_for_list_nested_data_item(self):
        elem_type = ListDataItem.get_element_type_for_list("nested_items")
        assert elem_type is SimpleDataItem

    def test_get_element_type_for_list_non_list_raises_type_error(self):
        try:
            SimpleDataItem.get_element_type_for_list("name")
            assert False, "TypeError expected for non-list field"
        except TypeError as exc:
            assert exc.args[0] == "the referenced field `name` is no list (is from type `<class 'str'>`)", str(exc)

    def test_get_all_fields_for_simple(self):
        fields = SimpleDataItem.get_all_fields_for(nested=False)
        assert set(fields) == {"name", "value"}

    def test_get_all_fields_for_nested_true(self):
        fields = NestedDataItem.get_all_fields_for(nested=True)
        assert "id" in fields
        assert "simple__name" in fields
        assert "simple__value" in fields

    def test_get_all_fields_for_nested_false(self):
        fields = NestedDataItem.get_all_fields_for(nested=False)
        assert set(fields) == {"id", "simple"}

    def test_get_all_fields_for_with_subkey(self):
        fields = NestedDataItem.get_all_fields_for(subkey="simple", nested=True)
        assert set(fields) == {"simple__name", "simple__value"}

    def test_get_all_fields_for_with_except_fields(self):
        fields = SimpleDataItem.get_all_fields_for(nested=False, except_fields=["value"])
        assert fields == ["name"]

    def test_get_all_fields_for_except_fields_missing_raises_key_error(self):
        try:
            SimpleDataItem.get_all_fields_for(nested=False, except_fields=["nonexistent"])
            assert False, "KeyError expected for missing except_field"
        except KeyError as exc:
            assert exc.args[0] == "can not find except_field `nonexistent` in possible data: ['name', 'value']", exc

    def test_get_field_data_type_simple(self):
        field_type = SimpleDataItem.get_field_data_type("name")
        assert field_type is str

    def test_get_field_data_type_int(self):
        field_type = SimpleDataItem.get_field_data_type("value")
        assert field_type is int

    def test_get_field_data_type_nested_data_item(self):
        field_type = NestedDataItem.get_field_data_type("simple")
        assert field_type is SimpleDataItem

    def test_get_field_data_type_optional(self):
        field_type = ComplexDataItem.get_field_data_type("optional_field")
        assert field_type is str

    def test_get_field_data_type_list(self):
        field_type = ListDataItem.get_field_data_type("items")
        assert field_type is list

    def test_get_field_value_simple(self):
        item = SimpleDataItem.create_as_nested(name="test", value=42)
        assert item.get_field_value("name") == "test"
        assert item.get_field_value("value") == 42

    def test_get_field_value_nested(self):
        item = NestedDataItem.create_as_nested(id=1, simple__name="nested_test", simple__value=99)
        assert item.get_field_value("simple__name") == "nested_test"
        assert item.get_field_value("simple__value") == 99

    def test_get_field_value_not_definable(self):
        item = SimpleDataItem.create_non_definable(nested=True)
        assert item.get_field_value("name") == NOT_DEFINABLE

    def test_get_field_value_missing_raises_key_error(self):
        item = SimpleDataItem.create_as_nested(name="test", value=42)
        try:
            item.get_field_value("nonexistent")
            assert False, "KeyError expected for missing field"
        except KeyError as exc:
            assert exc.args[0] == "can not find field `nonexistent` in `name='test' value=42`", str(exc)

    def test_set_field_value_simple(self):
        item = SimpleDataItem.create_as_nested(name="old", value=1)
        item.set_field_value("name", "new")
        assert item.name == "new"
        assert item.value == 1

    def test_set_field_value_only_change_this_value_false(self):
        item = NestedDataItem.create_as_nested(id=1, simple__name="test", simple__value=42)
        # Set a nested value with only_change_this_value=False (default)
        item.set_field_value("simple__name", "changed", only_change_this_value=False)
        assert item.simple.name == "changed"
        # Other fields in simple should be NOT_DEFINABLE
        assert item.simple.value == NOT_DEFINABLE

    def test_set_field_value_only_change_this_value_true(self):
        item = NestedDataItem.create_as_nested(id=1, simple__name="test", simple__value=42)
        # Set a nested value with only_change_this_value=True
        item.set_field_value("simple__value", 100, only_change_this_value=True)
        assert item.simple.value == 100
        # Other fields should remain unchanged
        assert item.simple.name == "test"

    def test_all_fields_are_not_definable_true(self):
        item = SimpleDataItem.create_non_definable(nested=True)
        assert item.all_fields_are_not_definable() is True

    def test_all_fields_are_not_definable_false(self):
        item = SimpleDataItem.create_as_nested(name="test", value=42)
        assert item.all_fields_are_not_definable() is False

    def test_all_fields_are_not_definable_partial_not_definable(self):
        item = SimpleDataItem.create_as_nested(name="test", value=NOT_DEFINABLE)
        assert item.all_fields_are_not_definable() is False

    def test_all_field_lookups_are_within_true_direct_field(self):
        result = SimpleDataItem.all_field_lookups_are_within("name", ["name", "value"])
        assert result is True

    def test_all_field_lookups_are_within_false_direct_field(self):
        result = SimpleDataItem.all_field_lookups_are_within("name", ["value"])
        assert result is False

    def test_all_field_lookups_are_within_true_nested_data_item(self):
        # If field is a SingleDataItem and all its fields are within the list
        result = NestedDataItem.all_field_lookups_are_within(
            "simple",
            ["id", "simple__name", "simple__value"]
        )
        assert result is True

    def test_all_field_lookups_are_within_false_nested_data_item_missing_subfield(self):
        # If field is a SingleDataItem but not all its fields are within the list
        result = NestedDataItem.all_field_lookups_are_within(
            "simple",
            ["id", "simple__name"]  # missing simple__value
        )
        assert result is False

    def test_compare_equal_simple(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="test", value=42)
        assert item1.compare(item2) is True

    def test_compare_not_equal_different_value(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="test", value=99)
        assert item1.compare(item2) is False

    def test_compare_with_ignore_field_lookups(self):
        item1 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World2", simple__value=42)
        # Ignore the 'value' field
        assert item1.compare(item2, ignore_field_lookups=["simple"]) is True

    def test_compare_with_ignore_field_lookups_nested(self):
        item1 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World2", simple__value=42)
        # Ignore the 'value' field
        assert item1.compare(item2, ignore_field_lookups=["simple__name"]) is True
        assert item1.compare(item2, ignore_field_lookups=["simple__value"]) is False

    def test_compare_with_allow_non_definable_true(self):
        item1 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple=NOT_DEFINABLE)
        # Should be equal when allow_non_definable=True
        assert item1.compare(item2, allow_non_definable=True) is True

    def test_compare_with_allow_non_definable_true_nested(self):
        item1 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=NOT_DEFINABLE)
        # Should be equal when allow_non_definable=True
        assert item1.compare(item2, allow_non_definable=True) is True

    def test_compare_with_allow_non_definable_false(self):
        item1 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple=NOT_DEFINABLE)
        # Should not be equal when allow_non_definable=False
        assert item1.compare(item2, allow_non_definable=False) is False

    def test_compare_with_allow_non_definable_false_nested(self):
        item1 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple__name="Hello World", simple__value=NOT_DEFINABLE)
        # Should not be equal when allow_non_definable=False
        assert item1.compare(item2, allow_non_definable=False) is False

    def test_compare_different_type_raises_type_error(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = NestedDataItem.create_as_nested(id=1, simple__name="test", simple__value=42)
        try:
            item1.compare(item2)
            assert False, "TypeError expected for comparing different types"
        except TypeError as exc:
            assert exc.args[0] == "`other` must be a `<class 'tests.scenarios.scenario_utils_single_data_item.SimpleDataItem'>` instance (is `id=1 simple=SimpleDataItem(name='test', value=42)`)", str(exc)

    def test_get_difference_error_messages_equal(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="test", value=42)
        errors = item1.get_difference_error_messages(item2)
        assert len(errors) == 0, errors

    def test_get_difference_error_messages_different_value(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="test", value=99)
        errors = item1.get_difference_error_messages(item2)
        assert len(errors) == 2, errors
        assert "detect different unique identification key - self: `test_42` | other: `test_99`" in errors
        assert "detect different value for dataclass field `value` - self: `42` | other: `99`" in errors

    def test_get_difference_error_messages_different_unique_id(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="other", value=42)
        errors = item1.get_difference_error_messages(item2, validate_unique_identification_separately=True)
        assert len(errors) == 2, errors
        assert 'detect different unique identification key - self: `test_42` | other: `other_42`' in errors
        assert 'detect different value for dataclass field `name` - self: `test` | other: `other`' in errors

    def test_get_difference_error_messages_skip_unique_id_validation(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="other", value=42)
        errors = item1.get_difference_error_messages(item2, validate_unique_identification_separately=False)
        # Should still have error for 'name' field difference
        assert len(errors) == 1, errors
        assert errors[0] == "detect different value for dataclass field `name` - self: `test` | other: `other`", errors[0]

    def test_get_difference_error_messages_with_ignore_fields(self):
        item1 = SimpleDataItem.create_as_nested(name="test", value=42)
        item2 = SimpleDataItem.create_as_nested(name="test", value=99)
        errors = item1.get_difference_error_messages(item2, ignore_field_lookups=["value"])
        assert len(errors) == 1, errors
        assert errors[0] == "detect different unique identification key - self: `test_42` | other: `test_99`", errors[0]

    def test_get_unique_identification(self):
        item = SimpleDataItem.create_as_nested(name="test", value=42)
        unique_id = item.get_unique_identification()
        assert unique_id == "test_42", unique_id

    def test_metaclass_validates_no_default_values(self):
        # Test that defining a class with default values raises ValueError
        try:
            class InvalidDataItem(SingleDataItem):
                name: str = "default"  # This should raise an error
                
                def get_unique_identification(self):
                    return self.name
            assert False, "ValueError expected for default values"
        except ValueError as exc:
            assert exc.args[0] == "no default values allowed for balderhub-data type definitions", str(exc)

    def test_metaclass_validates_no_double_underscores(self):
        # Test that defining a class with double underscores in field names raises KeyError
        try:
            class InvalidDataItem(SingleDataItem):
                field__name: str  # This should raise an error
                
                def get_unique_identification(self):
                    return "id"
            assert False, "KeyError expected for double underscores"
        except KeyError as exc:
            assert exc.args[0] == "no double underscores are allowed in field names", str(exc)

    def test_pydantic_strict_mode_validation(self):
        # Test that strict mode is enabled (should reject wrong types)
        try:
            SimpleDataItem.create_as_nested(name="test", value="not_an_int")
            assert False, "ValidationError expected for wrong type"
        except pydantic.ValidationError as exc:
            # Pydantic raises ValidationError
            error_msg = [
                line for line in str(exc).strip().splitlines()
                if not line.strip().startswith("For further information visit")
            ]
            assert error_msg == [
                "2 validation errors for SimpleDataItem",
                "value.int",
                "  Input should be a valid integer [type=int_type, input_value='not_an_int', input_type=str]",
                "value.is-instance[_NOT_DEFINABLE_TYPE]",
                "  Input should be an instance of _NOT_DEFINABLE_TYPE [type=is_instance_of, input_value='not_an_int', input_type=str]"
            ], exc

    def test_pydantic_extra_forbid_validation(self):
        # Test that extra fields are forbidden
        try:
            SimpleDataItem.create_as_nested(name="test", value=42, extra_field="not_allowed")
            assert False, "ValidationError expected for extra field"
        except pydantic.ValidationError as exc:
            # Pydantic raises ValidationError for extra fields
            error_msg = [
                line for line in str(exc).strip().splitlines()
                if not line.strip().startswith("For further information visit")
            ]

            assert error_msg == [
                "1 validation error for SimpleDataItem",
                "extra_field",
                "  Extra inputs are not permitted [type=extra_forbidden, input_value='not_allowed', input_type=str]"
            ], exc
