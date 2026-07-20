from __future__ import annotations


from pydantic import BaseModel

from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils import UnorderedList


class ScenarioUtilsUnorderedList(ScenarioUnit):
    """Unittests for UnorderedList class."""

    def test_eq_identical_order(self):
        a = UnorderedList([1, 2, 3])
        b = UnorderedList([1, 2, 3])
        assert a == b

    def test_eq_different_order(self):
        a = UnorderedList([1, 2, 3])
        b = UnorderedList([3, 2, 1])
        assert a == b

    def test_eq_different_content(self):
        a = UnorderedList([1, 2, 3])
        b = UnorderedList([1, 2, 4])
        assert a != b

    def test_eq_empty(self):
        a = UnorderedList()
        b = UnorderedList()
        assert a == b

    def test_eq_with_list(self):
        a = UnorderedList([1, 2, 3])
        b = [3, 2, 1]
        assert a == b

    def test_pydantic_model(self):
        class Model(BaseModel):
            items: UnorderedList[int]

        m = Model(items=[3, 1, 2])
        assert isinstance(m.items, list)
        assert m.items == [3, 1, 2]
        assert m.model_dump() == {"items": [3, 1, 2]}

    def test_pydantic_optional(self):
        class Model(BaseModel):
            items: UnorderedList[int] | None = None

        m = Model(items=[3, 1, 2])
        assert m.items == [3, 1, 2]

    def test_ne_different_types(self):
        a = UnorderedList([1, 2, 3])
        assert a != "not a list"
        assert a != 123
        assert a != None
        assert a != {"a": 1}

    def test_ne_different_lengths(self):
        a = UnorderedList([1, 2, 3])
        b = UnorderedList([1, 2])
        assert a != b

    def test_ne_with_duplicates(self):
        a = UnorderedList([1, 1, 2])
        b = UnorderedList([1, 2, 2])
        assert a != b

    def test_eq_with_duplicates(self):
        a = UnorderedList([1, 2, 1])
        b = UnorderedList([2, 1, 1])
        assert a == b

    def test_ne_vs_plain_list_different(self):
        a = UnorderedList([1, 2, 3])
        b = [1, 2, 4]
        assert a != b
