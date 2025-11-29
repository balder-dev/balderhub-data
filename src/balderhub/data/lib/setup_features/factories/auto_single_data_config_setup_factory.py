from typing import Type

from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.scenario_features import DataEnvironmentFeature
from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib.scenario_features.factories import AutoSingleDataConfigScenarioFactory


class AutoSingleDataConfigSetupFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded setup-based config-feature :class:`AllMultipleDataConfig` by using the
    defined data within a :class:`DataEnvironmentFeature`.
    """

    @classmethod
    def _define_class(cls, data_item_cls: Type[SingleDataItem], **kwargs):

        class AutoSingleDataConfig(AutoSingleDataConfigScenarioFactory.get_for(data_item_cls)):
            """inner factory-created feature class"""
            env = DataEnvironmentFeature()

            @property
            def data_item(self) -> SingleDataItem:
                """
                :return: the specific data item
                """
                return self.env.get_all_for(data_item_cls)[0]

        return AutoSingleDataConfig
