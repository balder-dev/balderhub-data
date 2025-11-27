from dataclasses import Field
from typing import List, Union, Optional, get_origin, get_args

import dataclasses


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

def get_data_item_type(field: dataclasses.Field) -> tuple[type, bool]:
    """
    returns the usable type for this field and a boolean value if this type can be optional or not

    .. note::
        It can also return a list type!

    :param field: the dataclass field the method should be applied
    :return: a tuple with the type of the field and a boolean value if this type can be optional or not
    """
    none_type = type(None)

    # now check the type
    if isinstance(field.type, type):
        # references a type
        return field.type, False

    # references another type definition
    if get_origin(field.type) in [list, List]:
        return list[get_data_item_type(get_args(field.type)[0])], False

    if get_origin(field.type) is Optional:
        inner_args = get_args(field.type)
        result_type, _ = get_data_item_type(inner_args[0])
        return result_type, True

    if get_origin(field.type) is Union:
        inner_args = list(get_args(field.type))

        if len(inner_args) == 1:
            return inner_args[0], False

        if len(inner_args) == 2 and none_type in inner_args:
            # make sure that `None` is part of it
            inner_args.remove(none_type)
            return inner_args[0], True

        raise TypeError('unsupported union type')

    raise TypeError(f'type definition `{field.type}` are not possible in balderhub-data dataclasses')


def get_inner_type_of_list_type(definition: type) -> type:
    """
    This method returns the inner list type of a list definition type.

    :param definition: the type statement, needs to be a list type

    :return: the inner type definition
    """
    if get_origin(definition) is not list:
        raise TypeError(f'unsupported type definition `{definition}` - expected list type')
    # check inner type
    inner_args = get_args(definition)
    if len(inner_args) == 0:
        raise TypeError('list needs to have exactly one item type definition -> none detected')
    if len(inner_args) != 1:
        raise TypeError(f"list needs to have exactly one item type definition -> multiple detected: `{inner_args}`")
    return inner_args[0]


def field_contained_in(field: Field, list_of_resolved_field):
    from .single_data_item import SingleDataItem  # pylint: disable=import-outside-toplevel

    if field.name in list_of_resolved_field:
        return True
    # now also check case if this is a sub-data-item field
    field_data_type, _ = get_data_item_type(field)
    if get_origin(field_data_type):
        # todo
        return False
    if issubclass(field_data_type, SingleDataItem):
        all_sub_fields = [
            f"{field.name}__{sub_field}" for sub_field in field_data_type.get_all_fields_for(nested=True)
        ]
        # only if all of these sub fields are in the non_fillable_fields -> this is non_fillable too
        for cur_sub_field in all_sub_fields:
            if cur_sub_field not in list_of_resolved_field:
                return False
        return True
    return False
