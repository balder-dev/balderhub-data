from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib.utils.not_definable import NOT_DEFINABLE


# Deeply nested data items (depth > 2) for create_non_definable tests
class Level3DataItem(SingleDataItem):
    a: int
    b: int

    def get_unique_identification(self):
        return f"{self.a}-{self.b}"


class Level2DataItem(SingleDataItem):
    lvl3: Level3DataItem
    x: int

    def get_unique_identification(self):
        return self.x


class Level1DataItem(SingleDataItem):
    lvl2: Level2DataItem
    ident: int

    def get_unique_identification(self):
        return self.ident


class RootDeepNestedDataItem(SingleDataItem):
    lvl1: Level1DataItem
    name: str

    def get_unique_identification(self):
        return self.name


class ScenarioUtilsSingleDataItem(ScenarioUnit):
    """Unittests for SingleDataItem class."""

    def test_create_non_definable_nested_true_deep(self):
        item = RootDeepNestedDataItem.create_non_definable(nested=True)
        # top-level fields
        assert isinstance(item, RootDeepNestedDataItem)
        assert item.name == NOT_DEFINABLE
        assert isinstance(item.lvl1, Level1DataItem)
        # level 1
        assert item.lvl1.ident == NOT_DEFINABLE
        assert isinstance(item.lvl1.lvl2, Level2DataItem)
        # level 2
        assert item.lvl1.lvl2.x == NOT_DEFINABLE
        assert isinstance(item.lvl1.lvl2.lvl3, Level3DataItem)
        # level 3 (leaf)
        assert item.lvl1.lvl2.lvl3.a == NOT_DEFINABLE
        assert item.lvl1.lvl2.lvl3.b == NOT_DEFINABLE

        # also verify that get_field works correctly on deep paths
        field_info = RootDeepNestedDataItem.get_field("lvl1__lvl2__lvl3__a")
        assert field_info is not None

    def test_create_non_definable_nested_false_deep(self):
        item = RootDeepNestedDataItem.create_non_definable(nested=False)
        # top-level scalar should be NOT_DEFINABLE
        assert item.name == NOT_DEFINABLE
        # the nested top-level field should be a NOT_DEFINABLE marker, not an instance
        assert item.lvl1 == NOT_DEFINABLE
