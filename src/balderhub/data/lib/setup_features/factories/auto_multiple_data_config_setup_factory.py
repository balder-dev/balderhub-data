from typing import Type

from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.scenario_features import DataEnvironmentFeature
from balderhub.data.lib.utils import SingleDataItemCollection
from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib.scenario_features.factories import AutoMultipleDataConfigScenarioFactory


class AutoMultipleDataConfigSetupFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded scenario-based config-feature :class:`SingleDataConfig` by using the
    defined data within a :class:`DataEnvironmentFeature`.
    """

    @classmethod
    def _define_class(cls, data_item_cls: Type[SingleDataItem], **kwargs):

        class AutoMultipleDataConfig(AutoMultipleDataConfigScenarioFactory.get_for(data_item_cls)):
            """inner factory-created feature class"""
            env = DataEnvironmentFeature()

            @property
            def data_list(self):
                """
                :return: returns the data item collection this config feature describes
                """
                return SingleDataItemCollection(self.env.get_all_for(data_item_cls))

        return AutoMultipleDataConfig
