from __future__ import annotations
from typing import Type
import balder

from balderhub.data.lib.utils import SingleDataItem


class AbstractDataItemRelatedFeature(balder.Feature):
    _features_by_data_item_type = {}

    @property
    def data_item_type(self) -> Type[SingleDataItem]:
        if not hasattr(self.__class__, '_for_data_item_type'):
            raise ValueError(
                f'data item related feature `{self.__class__}` was not registered for a specific data item'
            )
        return self.__class__._for_data_item_type

    @classmethod
    def set_data_item_type(cls, data_item_type: Type[SingleDataItem]):
        cls._for_data_item_type = data_item_type
        cls.register_feature_with_data_item_type(feature_cls=cls, data_item_type=data_item_type)

    @classmethod
    def register_feature_with_data_item_type(
            cls,
            feature_cls: type[AbstractDataItemRelatedFeature],
            data_item_type: Type[SingleDataItem]
    ):
        if cls not in AbstractDataItemRelatedFeature._features_by_data_item_type.keys():
            AbstractDataItemRelatedFeature._features_by_data_item_type[cls] = {}

        if data_item_type not in AbstractDataItemRelatedFeature._features_by_data_item_type[cls]:
            AbstractDataItemRelatedFeature._features_by_data_item_type[cls][data_item_type] = []

        #: only add it if it was not added before
        if feature_cls not in AbstractDataItemRelatedFeature._features_by_data_item_type[cls][data_item_type]:
            AbstractDataItemRelatedFeature._features_by_data_item_type[cls][data_item_type].append(feature_cls)

        # now register that for all parent classes that are based on :class:`AbstractDataItemRelatedFeature` too
        for cur_base in cls.__bases__:
            if issubclass(cur_base, AbstractDataItemRelatedFeature):
                cur_base.register_feature_with_data_item_type(feature_cls=feature_cls, data_item_type=data_item_type)

    @classmethod
    def get_specific_feature_for(cls, data_item_type: Type[SingleDataItem], **vdevice_mapping):

        available_feature_classes = \
            AbstractDataItemRelatedFeature._features_by_data_item_type.get(cls, {}).get(data_item_type, [])

        if len(available_feature_classes) == 0:
            raise KeyError(f'can not find a registered feature for data item `{data_item_type}` in `{cls.__name__}`')
        if len(available_feature_classes) > 1:
            raise KeyError(f'found more than one possible features for data item `{data_item_type}` in '
                           f'`{cls.__name__}`')
        return available_feature_classes[0](**vdevice_mapping)
