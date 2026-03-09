from typing import Type

from balderhub.data.lib.scenario_features.accessible_initial_data_config import AccessibleInitialDataConfig

from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib.utils.single_data_item_collection import SingleDataItemCollection


class AutoAccessibleInitialDataConfigFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded scenario-based config-feature :class:`AccessibleInitialDataConfig`
    """

    @classmethod
    def _define_class(cls, data_item_cls: Type[SingleDataItem], **kwargs):

        class AutoAccessibleInitialDataConfig(AccessibleInitialDataConfig):
            """inner factory-created feature class"""

            @property
            def data_list(self) -> SingleDataItemCollection:
                raise NotImplementedError()

        return AutoAccessibleInitialDataConfig
