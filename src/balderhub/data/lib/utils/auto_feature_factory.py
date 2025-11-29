from abc import ABC, abstractmethod

from balderhub.data.lib.scenario_features import AbstractDataItemRelatedFeature
from balderhub.data.lib.utils.single_data_item import SingleDataItem


class AutoFeatureFactory(ABC):
    """
    Base factory class for creating data-item bounded factories.
    """
    _classes = {}

    @classmethod
    def get_for(cls, data_item_cls: type[SingleDataItem], **kwargs) -> type[AbstractDataItemRelatedFeature]:
        """
        Defines a new feature for the specific data-item class given by attribute `data_item_cls`.

        :param data_item_cls: the single data-item class
        :param kwargs: optional further attributes that will be forwarded to internal method
                       :meth:`AutoFeatureFactory.register_cls` and  :meth:`AutoFeatureFactory._define_class`.
        :return: the feature type class
        """
        if cls not in cls._classes.keys():
            cls._classes[cls] = {}
        if data_item_cls not in cls._classes[cls]:
            cls.register_cls(data_item_cls, **kwargs)
        return cls._classes[cls][data_item_cls]

    @classmethod
    @abstractmethod
    def _define_class(cls, data_item_cls: type[SingleDataItem], **kwargs) -> type[AbstractDataItemRelatedFeature]:
        """
        Abstract method that needs to be implemented in subclasses. It instantiates the new specific data-item bounded
        feature class.

        :param data_item_cls: the data item type for which the feature should be defined
        :param kwargs: further attributes that are forwarded from :meth:`AutoFeatureFactory.get_for`
        :return: the new data-item bounded feature class
        """

    @classmethod
    def register_cls(cls, data_item_cls: type[SingleDataItem], **kwargs) -> None:
        """
        Method to register a new data-item bounded feature class. This method ensures that the feature class is defined.

        :param data_item_cls: the data item type for which the feature should be defined
        :param kwargs: further attributes that are forwarded from :meth:`AutoFeatureFactory.get_for`
        """
        if cls not in cls._classes.keys():
            cls._classes[cls] = {}
        cls._classes[cls][data_item_cls] = cls._define_class(data_item_cls, **kwargs)
