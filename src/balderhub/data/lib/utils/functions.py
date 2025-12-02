from typing import Union, Any

from .not_definable import NOT_DEFINABLE
from .lookup_field_string import LookupFieldString


def convert_field_lookups_to_dict_structure(dictionary: Union[dict, list], nested=True) -> Union[dict, list]:
    """
    This method converts filed-lookups into a dictionary structure.

    Example:

    .. code-block:: python
        >>> convert_field_lookups_to_dict_structure({'a__d': 3.2, 'a__b__c': 2, 'a__b__d': 3, 'a__c': 'H', 'b': 3})
        {'a': {'d': 3.2, 'b': {'c': 2, 'd': 3}, 'c': 'H'}, 'b': 3}

    :param dictionary: a flat dictionary with field-lookups as keys and their values as values.
    :param nested: False if the function should only return the first level - True if it should return nested
                   directories.
    :return: the converted (nested) dictionary
    """
    if isinstance(dictionary, list):
        return [convert_field_lookups_to_dict_structure(cur_item) for cur_item in dictionary]

    result = {}
    # sort by first-part-key
    for cur_lookup_key, cur_value in dictionary.items():
        # if there is already another dict structure inside it - make sure that this one is already converted
        if isinstance(cur_value, dict) and nested:
            cur_value = convert_field_lookups_to_dict_structure(cur_value, nested)

        if '__' in cur_lookup_key:
            first_part_of_key, remaining_part_of_key = cur_lookup_key.split('__', 1)

            # this is a nested key
            if first_part_of_key not in result.keys():
                result[first_part_of_key] = {}
            # TODO work around -> FIX IT!!!
            if result[first_part_of_key] is None:
                result[first_part_of_key] = {}
            # add subkey
            result[first_part_of_key][remaining_part_of_key] = cur_value
        else:
            result[cur_lookup_key] = cur_value

    if not nested:
        return result

    for cur_key, cur_value in result.items():
        if isinstance(cur_value, dict):
            result[cur_key] = convert_field_lookups_to_dict_structure(result[cur_key], nested=True)
    return result


def convert_dict_structure_to_field_lookups(dictionary: Union[dict, list]) -> Union[dict, list]:
    """
    This method converts the nested dictionary structure to a flat dictionary by using lookup-fields as key:

    .. code-block:: python
        >>> convert_dict_structure_to_field_lookups({'a': {'d': 3.2, 'b': {'c': 2, 'd': 3}, 'c': 'H'}, 'b': 3})
        {'a__d': 3.2, 'a__b__c': 2, 'a__b__d': 3, 'a__c': 'H', 'b': 3}

    :param dictionary: the nested dictionary structure
    :return: the flat directory while using lookup-fields as key:
    """

    if isinstance(dictionary, list):
        return [convert_dict_structure_to_field_lookups(cur_item) for cur_item in dictionary]

    result = {}
    for cur_key, cur_value in dictionary.items():
        if isinstance(cur_value, dict):
            for cur_sub_key, cur_sub_value in convert_dict_structure_to_field_lookups(cur_value).items():
                full_key = f'{cur_key}__{cur_sub_key}'
                result[full_key] = cur_sub_value
        elif isinstance(cur_value, list):
            result[cur_key] = convert_dict_structure_to_field_lookups(cur_value)
        else:
            result[cur_key] = cur_value
    return result


def set_lookup_field_in_data_dict(
        data_dict: dict[str, Any],
        field_to_set: Union[LookupFieldString, str],
        value_to_set: Any
) -> None:
    """
    Helper function to set a lookup-field within a nested dictionary structure
    :param data_dict: the nested data dictionary the value should be set
    :param field_to_set: the field lookup
    :param value_to_set: the value that should be set
    """
    field_to_set = LookupFieldString(field_to_set)

    if not isinstance(data_dict, dict):
        raise TypeError(f'the attribute `data_dict` needs to be a dictionary (is `{type(data_dict)}`)')

    cur_dict = data_dict
    for cur_idx, cur_key in enumerate(field_to_set.split_field_keys[:-1]):
        cur_key_chain = field_to_set.split_field_keys[:cur_idx]
        if cur_key not in cur_dict.keys():
            raise KeyError(
                f'can not locate key `{".".join(field_to_set.split_field_keys)}`, because the nested '
                f'subkey `{".".join(cur_key_chain)}` does not exist within dictionary `{data_dict}`'
            )
        cur_dict = cur_dict[cur_key]
        if not isinstance(cur_dict, dict):
            raise ValueError(
                f'can not locate key `{".".join(field_to_set.split_field_keys)}`, because the nested '
                f'element at subkey `{".".join(cur_key_chain)}` is not a dictionary (is: `{type(cur_dict)}`)'
            )

    if field_to_set.split_field_keys[-1] not in cur_dict.keys():
        raise KeyError(f'can not update value at key `{".".join(field_to_set.split_field_keys)}`, because the field '
                       f'`{".".join(field_to_set.split_field_keys)}` does not exist')

    cur_dict[field_to_set.split_field_keys[-1]] = value_to_set


def full_dictionary_is_not_definable(data_dict: dict[str, Any]) -> bool:
    """
    This method checks if the (nested) dictionary's values are `NOT_DEFINABLE` only.

    :param data_dict: the nested data dictionary that should be checked
    :return: Ture if all values are `NOT_DEFINABLE`, False otherwise
    """
    for _, cur_value in data_dict.items():
        if cur_value == NOT_DEFINABLE:
            continue
        if isinstance(cur_value, dict) and full_dictionary_is_not_definable(cur_value):
            continue
        return False
    return True
