from __future__ import annotations

import copy
from typing import Any

from balderhub.unit.scenarios import ScenarioUnit


from balderhub.data.lib.utils.functions import (
    convert_field_lookups_to_dict_structure,
    convert_dict_structure_to_field_lookups,
    set_lookup_field_in_data_dict,
    full_dictionary_is_not_definable,
)
from balderhub.data.lib.utils.not_definable import NOT_DEFINABLE


class ScenarioUtilsFunctions(ScenarioUnit):
    """Unit-like tests for utils functions."""

    def test_convert_field_lookups_roundtrip(self):
        flat = {
            "a__d": 3.2,
            "a__b__c": 2,
            "a__b__d": 3,
            "a__c": "H",
            "b": 3,
        }

        nested_expected = {
            "a": {"d": 3.2, "b": {"c": 2, "d": 3}, "c": "H"},
            "b": 3,
        }

        nested = convert_field_lookups_to_dict_structure(flat)
        assert nested == nested_expected

        flat_back = convert_dict_structure_to_field_lookups(nested)
        assert flat_back == flat

    def test_convert_field_lookups_nested_false_first_level_only(self):
        flat = {
            "a__d": 1,
            "a__b__c": 2,
            "x": 9,
        }
        first_level = convert_field_lookups_to_dict_structure(flat, nested=False)
        # Should not expand nested dictionaries recursively when nested=False
        assert set(first_level.keys()) == {"a", "x"}
        assert isinstance(first_level["a"], dict)
        # The inner dict should still hold lookup-like keys
        assert first_level["a"]["d"] == 1
        assert first_level["a"]["b__c"] == 2

    def test_convert_dict_structure_handles_lists(self):
        data = {
            "a": [
                {"b": 1, "c": 2},
                {"b": 3, "c": 4},
            ],
            "x": {"y": 5},
        }
        flat = convert_dict_structure_to_field_lookups(data)
        assert isinstance(flat["a"], list)
        assert len(flat["a"]) == 2
        assert flat["a"][0]["b"] == 1
        assert flat["a"][0]["c"] == 2
        assert flat["a"][1]["b"] == 3
        assert flat["a"][1]["c"] == 4
        assert flat["x__y"] == 5

        nested = convert_field_lookups_to_dict_structure(flat)
        assert nested == data

    def test_set_lookup_field_in_data_dict_success(self):
        d: dict[str, Any] = {"a": {"b": {"c": 1}, "d": 2}}
        set_lookup_field_in_data_dict(d, "a__b__c", 5)

        expected = copy.deepcopy(d)
        expected["a"]["b"]["c"] = 5

        assert d == expected

    def test_set_lookup_field_in_data_dict_type_error(self):
        # Not a dict
        try:
            set_lookup_field_in_data_dict([], "a__b__c", 1)  # type: ignore[arg-type]
            assert False, "TypeError expected"
        except TypeError as exc:
            assert exc.args[0] == "the attribute `data_dict` needs to be a dictionary (is `<class 'list'>`)", exc

    def test_set_lookup_field_in_data_dict_missing_intermediate_key(self):
        d = {"a": {}}
        try:
            set_lookup_field_in_data_dict(d, "a__b__c", 1)
            assert False, "KeyError expected for missing intermediate key"
        except KeyError as exc:
            assert exc.args[0] == ("can not locate key `a.b.c`, because the nested subkey `a` does not exist within "
                                   "dictionary `{'a': {}}`"), exc

    def test_set_lookup_field_in_data_dict_intermediate_not_dict(self):
        d = {"a": {"b": 5}}
        try:
            set_lookup_field_in_data_dict(d, "a__b__c", 1)
            assert False, "ValueError expected for intermediate not being a dict"
        except ValueError as exc:
            assert exc.args[0] == ("can not locate key `a.b.c`, because the nested element at subkey `a` is not a "
                                   "dictionary (is: `<class 'int'>`)"), exc

    def test_set_lookup_field_in_data_dict_missing_final_key(self):
        d = {"a": {"b": {"x": 2}}}
        try:
            set_lookup_field_in_data_dict(d, "a__b__c", 1)
            assert False, "KeyError expected for missing final key"
        except KeyError as exc:
            assert exc.args[0] == "can not update value at key `a.b.c`, because the field `a.b.c` does not exist", exc

    def test_full_dictionary_is_not_definable_true(self):
        d = {
            "a": {
                "b": NOT_DEFINABLE,
                "c": {"d": NOT_DEFINABLE},
            },
            "x": NOT_DEFINABLE,
        }
        assert full_dictionary_is_not_definable(d) is True

    def test_full_dictionary_is_not_definable_false_with_real_value(self):
        d = {
            "a": {
                "b": NOT_DEFINABLE,
                "c": {"d": 42},
            }
        }
        assert full_dictionary_is_not_definable(d) is False
