from balderhub.data.lib.scenario_features import AbstractDataItemRelatedFeature
import balderhub.data.lib.scenario_features.factories
from balderhub.data.lib.utils import SingleDataItem
from balderhub.data.lib.utils.auto_feature_factory import AutoFeatureFactory


class AutoDataParamProviderFactory(AutoFeatureFactory):
    """
    Represents a factory for creating parameter providers related to data items for auto-generated features.

    The `AutoDataParamProviderFactory` is responsible for defining and constructing data item parameter
    providers dynamically for use with auto-generated features. It creates data item bounded setup-level features
    of :class:`balderhub.auth.contrib.data.setup_features.DataItemParamProvider`.

    """
    @classmethod
    def _define_class(cls, data_item_cls: type[SingleDataItem], **kwargs) -> type[AbstractDataItemRelatedFeature]:
        # pylint: disable-next=import-outside-toplevel
        from ..data_item_param_provider import DataItemParamProvider

        class AutoDataItemParamProvider(DataItemParamProvider):
            """
            auto created data item bounded setup-level feature of
            :class:`balderhub.auth.contrib.data.setup_features.DataItemParamProvider`
            """
            class Server(DataItemParamProvider.Server):
                """
                server vdevice with data-item bounded setup-level feature implementation of
                :class:`balderhub.data.lib.scenario_features.InitialDataConfig`.
                """
                all_data = \
                    balderhub.data.lib.scenario_features.factories.AutoInitialDataConfigFactory.get_for(data_item_cls)

        return AutoDataItemParamProvider  # TODO
