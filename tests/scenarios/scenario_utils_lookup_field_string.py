from __future__ import annotations

from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.lookup_field_string import LookupFieldString


class ScenarioUtilsLookupFieldString(ScenarioUnit):
    """Unittests for LookupFieldString class."""

    def test_init_with_single_string_with_double_underscore(self):
        lfs = LookupFieldString("a__b__c")
        assert lfs.split_field_keys == ["a", "b", "c"]
        assert str(lfs) == "a__b__c"

    def test_init_with_single_string_without_double_underscore(self):
        lfs = LookupFieldString("simple")
        assert lfs.split_field_keys == ["simple"]
        assert str(lfs) == "simple"

    def test_init_with_multiple_strings(self):
        lfs = LookupFieldString("a", "b", "c")
        assert lfs.split_field_keys == ["a", "b", "c"]
        assert str(lfs) == "a__b__c"

    def test_init_with_lookup_field_string(self):
        lfs1 = LookupFieldString("a__b__c")
        lfs2 = LookupFieldString(lfs1)
        assert lfs2.split_field_keys == ["a", "b", "c"]
        assert str(lfs2) == "a__b__c"

    def test_init_empty_raises_value_error(self):
        try:
            LookupFieldString()
            assert False, "ValueError expected for empty args"
        except ValueError as exc:
            assert exc.args[0] == "empty lookup field string are not possible", exc

    def test_init_single_empty_string_raises_value_error(self):
        try:
            LookupFieldString("")
            assert False, "ValueError expected for empty string"
        except ValueError as exc:
            assert exc.args[0] == "empty lookup field string are not possible", exc

    def test_init_multiple_args_with_double_underscore_raises_value_error(self):
        try:
            LookupFieldString("a", "b__c")
            assert False, "ValueError expected for double underscore in multi-arg mode"
        except ValueError as exc:
            assert exc.args[0] == ("lookup strings and non lookup strings can not be mixed - double underscores in "
                                   "attribute names are not allowed"), exc

    def test_init_with_non_string_raises_type_error(self):
        try:
            LookupFieldString(123)  # type: ignore[arg-type]
            assert False, "TypeError expected for non-string argument"
        except TypeError as exc:
            assert exc.args[0] == "Argument must be a string", exc

    def test_split_field_keys_returns_copy(self):
        lfs = LookupFieldString("a__b")
        keys1 = lfs.split_field_keys
        keys2 = lfs.split_field_keys
        assert keys1 == keys2
        assert keys1 is not keys2  # Should be a copy

    def test_nested_level_single(self):
        lfs = LookupFieldString("field")
        assert lfs.nested_level == 1

    def test_nested_level_multiple(self):
        lfs = LookupFieldString("a__b__c__d")
        assert lfs.nested_level == 4

    def test_add_sub_field_with_string(self):
        lfs = LookupFieldString("a__b")
        new_lfs = lfs.add_sub_field("c")
        assert new_lfs.split_field_keys == ["a", "b", "c"]
        assert str(new_lfs) == "a__b__c"
        # Original should be unchanged
        assert lfs.split_field_keys == ["a", "b"]

    def test_add_sub_field_with_lookup_field_string(self):
        lfs1 = LookupFieldString("a__b")
        lfs2 = LookupFieldString("c__d")
        new_lfs = lfs1.add_sub_field(lfs2)

        assert new_lfs.split_field_keys == ["a", "b", "c", "d"]
        assert str(new_lfs) == "a__b__c__d"
        # Original should be unchanged
        assert str(lfs1) == "a__b"
        assert str(lfs2) == "c__d"

    def test_equality_with_same_lookup_field_string(self):
        lfs1 = LookupFieldString("a__b__c")
        lfs2 = LookupFieldString("a", "b", "c")
        assert lfs1 == lfs2

    def test_equality_with_string(self):
        lfs = LookupFieldString("a__b__c")
        assert lfs == "a__b__c"

    def test_equality_with_different_string(self):
        lfs = LookupFieldString("a__b__c")
        assert not (lfs == "x__y__z")

    def test_equality_with_non_string_non_lookup_field_string(self):
        lfs = LookupFieldString("a__b")
        assert not (lfs == 123)
        assert not (lfs == None)
        assert not (lfs == ["a", "b"])

    def test_hash_consistency(self):
        lfs1 = LookupFieldString("a__b__c")
        lfs2 = LookupFieldString("a", "b", "c")
        assert hash(lfs1) == hash(lfs2)

    def test_hash_usable_in_set(self):
        lfs1 = LookupFieldString("a__b")
        lfs2 = LookupFieldString("c__d")
        lfs3 = LookupFieldString("a__b")  # Same as lfs1
        
        lookup_set = {lfs1, lfs2, lfs3}
        # lfs3 should not add a new element since it's equal to lfs1
        assert len(lookup_set) == 2

    def test_hash_usable_in_dict(self):
        lfs1 = LookupFieldString("key1")
        lfs2 = LookupFieldString("key2")
        
        lookup_dict = {lfs1: "value1", lfs2: "value2"}
        assert lookup_dict[lfs1] == "value1"
        assert lookup_dict[LookupFieldString("key1")] == "value1"  # Same key

    def test_complex_nested_field_operations(self):
        # Build up a complex lookup field step by step
        base = LookupFieldString("root")
        level1 = base.add_sub_field("child1")
        level2 = level1.add_sub_field("child2__grandchild")
        
        assert level2.split_field_keys == ["root", "child1", "child2", "grandchild"]
        assert level2.nested_level == 4
        assert str(level2) == "root__child1__child2__grandchild"
