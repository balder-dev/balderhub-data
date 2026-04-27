import enum

import balder

import balderhub.data.lib.scenario_features
from balderhub.auth.lib.scenario_features.client import UnresolvedResourceParameterConfig
from balderhub.auth.lib.utils import ResourceRule

from ..utils import ResourceForSpecificDataItem


class DataItemParamProvider(UnresolvedResourceParameterConfig):
    """
    Handles configuration and provides parameters for resolving resources for specific data items.

    This is a setup-level feature implementation for the
    :class:`balderhub.auth.lib.scenario_features.client.UnresolvedResourceParameterConfig`. It uses a
    defined `ResolvingMode` to specify how parameters should be selected out of the remote server feature
    :class:`balderhub.data.lib.scenario_features.InitialDataConfig`.

    """
    class ResolvingMode(enum.Enum):
        """
        Defines modes for resolving entities.

        This class provides an enumeration of possible resolving modes that dictate
        how entities are retrieved or resolved.
        """
        # this will return all existing
        ALL = 'all'
        # will return the first {ENFORCING_PARAMETERS} items (ENFORCING_PARAMETERS needs to be >0)
        MINIMUM = 'minimum'

    #: defines the mode used to resolve parameters. It can either return all existing parameters
    # (``ResolvingMode.ALL``) or enforce a minimum required number of parameters (``ResolvingMode.MINIMUM``).
    RESOLVING_MODE: ResolvingMode = ResolvingMode.ALL
    #: specifies the minimum number of parameters to enforce when in  ``ResolvingMode.MINIMUM``. Must be greater
    #: than 0 for that mode.
    ENFORCING_PARAMETERS = 0

    class Server(balder.VDevice):
        """server vdevice holding the specified initial data configuration feature"""
        all_data = balderhub.data.lib.scenario_features.InitialDataConfig()

    def get_parameters_for(self, resource_rule: ResourceRule) -> list[ResourceForSpecificDataItem.Parameter]:
        data = self.Server.all_data.data_list

        parameters = [ResourceForSpecificDataItem.Parameter(elem) for elem in data]

        if resource_rule.cb_rule is not None:
            # filter parameters
            parameters = [param for param in parameters if resource_rule.cb_rule(param)]

        if self.RESOLVING_MODE == self.ResolvingMode.ALL:
            # do nothing
            pass
        elif self.RESOLVING_MODE == self.ResolvingMode.MINIMUM:
            if self.ENFORCING_PARAMETERS <= 0:
                raise ValueError(
                    f'in resolving mode {self.ResolvingMode.MINIMUM} the ENFORCING_PARAMETERS needs to be >0'
                )
            parameters = parameters[:self.ENFORCING_PARAMETERS]
        else:
            raise ValueError(f'unexpected value for ResolvingMode {self.RESOLVING_MODE}')

        if len(parameters) < self.ENFORCING_PARAMETERS:
            raise ValueError(
                f'{self.__class__.__name__}.ENFORCING_PARAMETERS requires at least {self.ENFORCING_PARAMETERS} '
                f'parameters for every rule - but rule {resource_rule} only has {len(parameters)} possible parameters')

        return parameters
