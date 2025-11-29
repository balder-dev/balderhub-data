from __future__ import annotations
from typing import Any, List, Dict, Type
import balder

from balderhub.data.lib.utils.single_data_item import SingleDataItem, SingleDataItemTypeT
from balderhub.data.lib.utils.exceptions import DuplicateDataObjectError


class DataEnvironmentFeature(balder.Feature):
    """
    The Data Environment Feature provides an interface for managing a big data set. It helps to configure your tests
    depending on the selected data sets. You can use it to create a nested data-environment structure and define
    different data sets for different setups.
    """

    # TODO do we need a plausibility check after the `load_data` call, that makes sure, that references between all data
    #  exist?
    # TODO make sure that `unique_identification` is unique everywhere

    class DoesNotExist(Exception):
        """
        error that is thrown if an element does that is requested by some methods does not exist in the environment
        """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # holds the whole data
        self._data: Dict[Type[SingleDataItemTypeT], Dict[Any, SingleDataItemTypeT]] = {}

        self.load_data()

    def load_data(self) -> None:
        """
        This method will be executed to generate / load the data for this environment into the object. You need to
        overwrite it in subclass to fill the data environment with data.
        """

    def get_all_for(self, data_obj_type: Type[SingleDataItemTypeT]) -> List[SingleDataItemTypeT]:
        """
        This method returns all known data-items for a specific data item type.
        :param data_obj_type: the data-item type
        :return: a list of all known data-items
        """
        if data_obj_type not in self._data.keys():
            return []
        return list(self._data[data_obj_type].values())

    def get(self, data_obj_type: Type[SingleDataItemTypeT], unique_identification: Any) -> SingleDataItemTypeT:
        """
        This method returns exactly one element identified by the `unique_identification`.
        It raises an exception if the requested element does not exist in the environment.

        :param data_obj_type: the data-item type
        :param unique_identification: the unique-identification value of the requested data-item type
        :return: the specific data item
        """
        if data_obj_type not in self._data.keys():
            raise self.DoesNotExist(f'no items from type `{data_obj_type}` exist in the environment')
        if unique_identification not in self._data[data_obj_type].keys():
            raise self.DoesNotExist(f'no element with unique-identification `{unique_identification}` of '
                                    f'type `{data_obj_type}` exist in the environment')
        return self._data[data_obj_type][unique_identification]

    def _add_data(self, data_objects: SingleDataItem | List[SingleDataItem]) -> None:
        """
        Method to add a new data set to the internal data set storage.

        :param data_objects: the data item object / objects that should be added
        """
        if isinstance(data_objects, SingleDataItem):
            data_objects = [data_objects]
        for cur_data_object in data_objects:
            if cur_data_object.__class__ not in self._data.keys():
                self._data[cur_data_object.__class__] = {}
            if cur_data_object.get_unique_identification() in self._data[cur_data_object.__class__].keys():
                raise DuplicateDataObjectError(
                    'another data object with the same identifier already exists in environment data'
                )
            self._data[cur_data_object.__class__][cur_data_object.get_unique_identification()] = cur_data_object

    def sync_environment(self) -> None:
        """
        This method executes the transfer of the environment in the related system. It should handle the creation of
        the stored data with the related system.
        It is expected that after calling this method, the environment data and the data within the related system are
        in sync.
        """
        raise NotImplementedError
