from typing import Callable, Union

import balder

from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory
from balderhub.data.lib.utils import SingleDataItemCollection
from balderhub.data.lib.utils.single_data_item import SingleDataItem
from balderhub.data.lib import scenario_features
from balderhub.data.lib.utils.filter import Filter


class AutoAccessibleInitialDataConfigFactory(AutoFeatureFactory):
    """
    Factory for creating data-item bounded scenario-based config-feature :class:`MultipleDataConfig` by using the
    defined data within a :class:`DataEnvironmentFeature`.
    """
    @classmethod
    def get_for(
            cls,
            data_item_cls: type[SingleDataItem],
            filter_func: Union[Callable[[SingleDataItem], bool], None] = None,
            **kwargs
    ):
        return super().get_for(data_item_cls, filter_func=filter_func)

    @classmethod
    def _define_class(cls, data_item_cls: type[SingleDataItem], **kwargs):
        filter_func = kwargs['filter_func']

        class AutoAccessibleInitialDataConfig(
            scenario_features.factories.AutoAccessibleInitialDataConfigFactory.get_for(data_item_cls)
        ):
            """inner factory-created feature class"""
            class Master(balder.VDevice):
                """inner vdevice referencing the master device that provides the full initial data config"""
                full_initial_config = scenario_features.factories.AutoInitialDataConfigFactory.get_for(data_item_cls)()

            class Filter(Filter):
                """filter that filters the initial data"""
                def apply(self, item: SingleDataItem) -> bool:
                    return filter_func(item)

            @property
            def data_list(self) -> SingleDataItemCollection:
                """returns the accessible data according to the provided filter"""
                if filter_func is None:
                    return self.Master.full_initial_config.data_list
                return self.Master.full_initial_config.data_list.filter(self.Filter())

        return AutoAccessibleInitialDataConfig
