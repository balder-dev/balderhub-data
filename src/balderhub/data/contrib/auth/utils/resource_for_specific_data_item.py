from abc import ABC, abstractmethod
from typing import Type

import dataclasses
from balderhub.data.lib.utils import SingleDataItem


from balderhub.auth.lib.utils import Resource
from balderhub.auth.lib.utils import UnresolvedResource


class ResourceForSpecificDataItem(UnresolvedResource, ABC):
    """
    This class represents an unresolved resource that is specific for a certain data item type.
    """

    @dataclasses.dataclass
    class Parameter(UnresolvedResource.Parameter):
        """
        The parameter class for the `ResourceForSpecificDataItem` class.
        """
        data_item: SingleDataItem

    def __init__(
            self,
            data_item_type: Type[SingleDataItem],
            **kwargs
    ):
        """
        :param data_item_type: the type of the data item
        :param kwargs: additional keyword arguments for the `UnresolvedResource` constructor
        """
        super().__init__(**kwargs)
        self._data_item_type = data_item_type

    def __str__(self):
        return f"{super().__str__()}({self._data_item_type.__name__})"

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.data_item_type == other.data_item_type

    def __hash__(self):
        return hash(self.__class__) + hash(self._data_item_type)

    @property
    def data_item_type(self) -> Type[SingleDataItem]:
        """returns the data item type of this resource"""
        return self._data_item_type

    @abstractmethod
    def get_resolved_resource(self, param: Parameter) -> Resource:
        """
        Resolves the resource with the given parameter.

        :param param: the parameter for the unresolved resource
        :return: the resolved resource
        """
