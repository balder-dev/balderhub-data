from typing import Type

from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.scenario_features.single_data_config import SingleDataConfig
from balderhub.data.lib.utils.single_data_item import SingleDataItem


class AutoSingleDataConfigScenarioFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded scenario-based config-feature :class:`SingleDataConfig`
    """

    @classmethod
    def _define_class(cls, data_item_cls: Type[SingleDataItem], **kwargs):

        class AutoSingleDataConfig(SingleDataConfig):
            """inner factory-created feature class"""

            @property
            def data_item(self) -> SingleDataItem:
                raise NotImplementedError()

        return AutoSingleDataConfig
