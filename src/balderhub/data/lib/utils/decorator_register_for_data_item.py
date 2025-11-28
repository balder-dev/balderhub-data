from __future__ import annotations
from typing import Type

import inspect

from balderhub.data.lib.scenario_features.abstract_data_item_related_feature import AbstractDataItemRelatedFeature
from balderhub.data.lib.utils import SingleDataItem


def register_for_data_item(
        data_item_type: Type[SingleDataItem],
):
    """
    With the `@register_for_data_item` decorator you can specify the relation of a feature to a data item. This is often
    used for describing setups by SetupFactories.

    :param data_item_type: the data item type the feature should be registered for
    """
    if not (isinstance(data_item_type, type) and issubclass(data_item_type, SingleDataItem)):
        raise TypeError('data_item_type must be a subclass of SingleDataItem')

    class ForDataItemDecorator:
        """decorator class for `@register_for_data_item` decorator"""

        def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
            nonlocal data_item_type

            func = args[0]

            if not inspect.isclass(func):
                raise TypeError('The decorator `@register_for_data_item` may only be used for classes and not for '
                                'functions or methods')
            # it must be a class decorator
            if not issubclass(func, AbstractDataItemRelatedFeature):
                raise TypeError(
                    f"The decorator `@register_for_data_item` may only be used for `AbstractDataItemRelatedFeature` "
                    f"objects. This is not possible for the applied class `{func.__name__}`.")

            func.set_data_item_type(data_item_type)

            # directly return the class -> we do not want to manipulate it
            return func

    return ForDataItemDecorator
