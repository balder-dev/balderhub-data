from typing import Type

from balderhub.data.lib.utils import SingleDataItemCollection
from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.scenario_features.initial_data_config import InitialDataConfig
from balderhub.data.lib.utils.single_data_item import SingleDataItem


class AutoInitialDataConfigFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded scenario-based config-feature :class:`InitialDataConfig`
    """

    @classmethod
    def _define_class(cls, data_item_cls: Type[SingleDataItem], **kwargs):

        class AutoInitialDataConfig(InitialDataConfig):
            """inner factory-created feature class"""

            @property
            def data_list(self) -> SingleDataItemCollection:
                raise NotImplementedError()

        return AutoInitialDataConfig
