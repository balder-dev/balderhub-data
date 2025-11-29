from typing import Type

from balderhub.data.lib.utils import SingleDataItemCollection
from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.scenario_features.all_multiple_data_config import AllMultipleDataConfig
from balderhub.data.lib.utils.single_data_item import SingleDataItem


class AutoMultipleDataConfigScenarioFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded scenario-based config-feature :class:`AllMultipleDataConfig`
    """

    @classmethod
    def _define_class(cls, data_item_cls: Type[SingleDataItem], **kwargs):

        class AutoMultipleDataConfig(AllMultipleDataConfig):
            """inner factory-created feature class"""

            @property
            def data_list(self) -> SingleDataItemCollection:
                raise NotImplementedError()

        return AutoMultipleDataConfig
