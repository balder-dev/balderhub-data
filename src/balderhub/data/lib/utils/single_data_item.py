from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, TypeVar, Any, Union, get_args, get_origin
import dataclasses
from .functions import (convert_field_lookups_to_dict_structure, convert_dict_structure_to_field_lookups,
                        get_data_item_type, get_inner_type_of_list_type)
from .not_definable import NOT_DEFINABLE


logger = logging.getLogger(__name__)

SingleDataItemTypeT = TypeVar("SingleDataItemTypeT", bound="SingleDataItem")


@dataclasses.dataclass
class SingleDataItem(ABC):

    @abstractmethod
    def get_unique_identification(self):
        raise NotImplementedError

    @classmethod
    def create_as_nested(cls, **kwargs):
        kwargs_splitted = convert_field_lookups_to_dict_structure(kwargs, nested=False)


        dataclass_fields = dataclasses.fields(cls)

        # make sure that all kwargs are available in dataclass
        for cur_key in kwargs_splitted.keys():
            if cur_key not in [f.name for f in dataclass_fields]:
                raise KeyError(f"{cur_key} is not part of the dataclass `{cls.__name__}`")

        # make sure that all data item fields are available in kwargs
        for cur_field in dataclass_fields:
            if cur_field.name not in kwargs_splitted.keys():
                raise KeyError(f"the field `{cur_field.name}` of the dataclass `{cls.__name__}` is not mentioned in "
                               f"provided dict")

        def _resolve_list(list_field_type, list_in_kwargs) -> Union[list, NOT_DEFINABLE]:
            inner_type = get_inner_type_of_list_type(list_field_type)

            if list_in_kwargs == NOT_DEFINABLE:
                return NOT_DEFINABLE

            result = []
            for cur_kwargs_of_list_item in list_in_kwargs:
                if isinstance(inner_type, SingleDataItem):
                    # we expect this type of data item
                    result.append(inner_type.create_as_nested(**cur_kwargs_of_list_item))
                elif get_origin(inner_type) is list:
                    # its another inner list -> call this function again
                    result.append(_resolve_list(cur_kwargs_of_list_item, inner_type))
                else:
                    # it is a normal type -> add it
                    result.append(cur_kwargs_of_list_item)
            return result

        # now created objects
        fields_for_obj = {}
        for cur_field in dataclasses.fields(cls):
            cur_field_type, field_can_be_optional = get_data_item_type(cur_field)

            cur_field_value = kwargs_splitted[cur_field.name]

            if isinstance(cur_field_type, type):
                if get_origin(cur_field_type) is list:
                    # check inner type
                    fields_for_obj[cur_field.name] = _resolve_list(
                        list_field_type=cur_field_type, list_in_kwargs=cur_field_value
                    )
                elif issubclass(cur_field_type, SingleDataItem)  and cur_field_value != NOT_DEFINABLE:
                    if cur_field_value is None:
                        if not field_can_be_optional:
                            raise ValueError(f"{cur_field} is None, should be a {cur_field_type} (non optional)")
                        fields_for_obj[cur_field.name] = None
                    else:
                        # it is nested -> determine it for subitem
                        fields_for_obj[cur_field.name] = cur_field_type.create_as_nested(**cur_field_value)
                else:
                    # it is a normal value -> set it
                    fields_for_obj[cur_field.name] = cur_field_value
            else:
                raise TypeError(f'detect unexpected object as type for `{cur_field_type}`')

        return cls(**fields_for_obj)

    @classmethod
    def create_non_definable(cls, nested=True) -> SingleDataItemTypeT:
        """
        :return: returns instance of this  data item with `NON_DEFINABLE` for every field
        """
        data = {}
        for cur_field in cls.get_all_fields_for(nested=nested):
            data[cur_field] = NOT_DEFINABLE
        return cls.create_as_nested(**data)

    @classmethod
    def get_field(cls, field_lookup_str: str) -> dataclasses.Field:
        splitted_field_str = field_lookup_str.split("__")
        first_field_part = splitted_field_str.pop(0)
        relevant_fields = [field for field in dataclasses.fields(cls) if field.name == first_field_part]
        if len(relevant_fields) == 1:
            if len(splitted_field_str) > 0:
                subtype, _ = cls.get_field_data_type(first_field_part)
                if not issubclass(subtype, SingleDataItem):
                    raise KeyError(f'the subkey `{first_field_part}` does not reference a data item type in data '
                                   f'item `{cls.__name__}`')
                return subtype.get_field('__'.join(splitted_field_str))
            return relevant_fields[0]
        raise KeyError(f'can not find a field `{first_field_part}` in data item `{cls.__name__}`')

    @classmethod
    def get_all_fields_for(cls, subkey=None, nested=True, except_fields: List[str]=None) -> List[str]:
        """
        This method returns a list with all field names, that matches the requested filter.
        :param subkey: all fields that belongs to this subkey are returned - if this is None, all fields of this data
                       item are returned.
        :param nested: True if the method should return all nested fields and not only the direct fields
        :param except_fields: a list of fields to exclude from the returned list (if subkey is given, they are
                              relative to this subkey, otherwise they are relative to this data item)
        :return: a list of fields as strings in lookup syntax (concat with `__`)
        """
        if except_fields is None:
            except_fields = []


        split_subkey = subkey.split('__') if subkey is not None else []
        first_field_of_subkey = split_subkey[0] if len(split_subkey) > 0 else None

        if first_field_of_subkey:
            if first_field_of_subkey not in [k.name for k in dataclasses.fields(cls)]:
                raise KeyError(f'no field with subkey `{first_field_of_subkey}` does exist')

        # generate absolute except_fields
        except_fields = [f"{subkey}__{field}" for field in except_fields] if subkey else except_fields

        all_fields = []
        for cur_field in dataclasses.fields(cls):

            if subkey is not None and first_field_of_subkey != cur_field.name:
                # continue, because this field is not relevant!
                continue

            # TODO what if type is a list??????
            if nested:
                # TODO make this nicer
                raw_type, _ = get_data_item_type(cur_field)
                try:
                    is_nested = issubclass(raw_type, SingleDataItem)
                except TypeError:
                    is_nested = False

                if is_nested:
                    # can return all fields - except-fields will be filtered later
                    all_sub_fields = raw_type.get_all_fields_for(
                        subkey=None if len(split_subkey) <= 1 else '__'.join(split_subkey[1:]),
                        nested=True,
                        # do not add except fields -> will be removed later)
                        except_fields=None)
                    all_fields += [f"{cur_field.name}__{sf}" for sf in all_sub_fields]
                else:
                    all_fields.append(cur_field.name)
            else:
                all_fields.append(cur_field.name)

        # todo optimize that
        for cur_except_field in except_fields:
            if cur_except_field not in all_fields:
                raise KeyError(f'can not find except_field `{cur_except_field}` in possible data: {all_fields}')

        return [field for field in all_fields if field not in except_fields]

    @classmethod
    def get_field_data_type(cls, field_lookup_str: str) -> tuple[type, bool]:
        splitted_field_names = field_lookup_str.split('__')
        cur_splitted_name = splitted_field_names.pop(0)

        all_relevant_fields = [field for field in dataclasses.fields(cls) if field.name == cur_splitted_name]
        if len(all_relevant_fields) != 1:
            raise KeyError(f'can not find field {cur_splitted_name} in data item {cls.__name__}')
        cur_field_type, is_optional = get_data_item_type(all_relevant_fields[0])

        if len(splitted_field_names) == 0:
            # this is the requested data type
            return cur_field_type, is_optional
        if not issubclass(cur_field_type, SingleDataItem):
            raise KeyError(f'can not resolve the field {field_lookup_str} for data item {cls.__name__}, '
                           f'because field is no data item class')
        return cur_field_type.get_field_data_type('__'.join(splitted_field_names))

    def get_field_value(self, field_lookup_str: str):
        item = self
        for cur_splitted_name in field_lookup_str.split('__'):
            if item == NOT_DEFINABLE:
                return NOT_DEFINABLE
            if not hasattr(item, cur_splitted_name):
                raise KeyError(f'can not find field `{cur_splitted_name}` in `{item}`')
            item = getattr(item, cur_splitted_name)
        return item

    def set_field_value(self, field_name: str, value: Any, only_change_this_value=False) -> None:
        """
        This method sets a specific value in the data item. It sets the value that is provided as `field_name` inside
        the data item. In case the field_name is a nested lookup field, it will overwrite the nested items by setting a
        new data item for the nested field. In case the value is a dictionary matching the definition of the data item
        type of the nested field, it will set all values that are provided in this dict. Any other value will be set
        with `NOT_DEFINABLE`.

        :param field_name: the name of the field (nested lookup field allowed)
        :param value: the value that should be set (dicts for nested structures are allowed)
        :param only_change_this_value: this value is given in case that the method should not recreate all nested data
                                       items and set their undefined values to `NOT_DEFINABLE`
        """
        item = self

        # first resolve all nested lookup fields
        splitted_field_name = field_name.split('__')

        # -> go through all nested fields and create new empty sub data item if necessary
        for cur_splitted_name in splitted_field_name[:-1]:
            new_item = getattr(item, cur_splitted_name)
            new_item_type, new_item_type_is_optional = item.get_field_data_type(cur_splitted_name)

            if not issubclass(new_item_type, SingleDataItem):
                raise KeyError(f'the field `{cur_splitted_name}` of data item type `{item.__class__}` is no data item'
                               f' - can not set nested value here')
            # always create new object for nested value!
            if not only_change_this_value or new_item in [None, NOT_DEFINABLE]:
                new_item = new_item_type.create_non_definable(nested=False)
                setattr(item, cur_splitted_name, new_item)
            item = new_item

        # we are now at the last field -> nothing nested anymore
        field_type, is_optional = item.get_field_data_type(splitted_field_name[-1])

        if is_optional and value is None:
            setattr(item, splitted_field_name[-1], None)
        elif value == NOT_DEFINABLE:
            setattr(item, splitted_field_name[-1], NOT_DEFINABLE)
        elif get_origin(field_type) is list:
            inner_type = get_inner_type_of_list_type(field_type)

            if not isinstance(value, list):
                raise TypeError(f'got type for field `{splitted_field_name[-1]}` of data item `{item.__class__}`: '
                                f'`{type(value)}` | expected `{field_type}`')

            if get_origin(inner_type) is list:
                # TODO we need to reimplement that stuff!!
                raise NotImplementedError('need to implement nested lists')
            result = []
            if issubclass(inner_type, SingleDataItem):
                # parse values for every item
                for cur_inner_val in value:
                    new_inner_item = inner_type.create_non_definable(nested=False)
                    for cur_key, cur_val in cur_inner_val.items():
                        new_inner_item.set_field_value(cur_key, cur_val)
                    result.append(new_inner_item)
            else:
                for cur_inner_val in value:
                    if not isinstance(cur_inner_val, inner_type):
                        raise TypeError(f'inner list element has unexpected type `{type(cur_inner_val)}` | '
                                        f'expected {inner_type}')
                    result.append(cur_inner_val)
            setattr(item, splitted_field_name[-1], result)
        # if the value is a dictionary and we have still a data item field -> fill all values of the dictionary
        elif issubclass(field_type, SingleDataItem) and isinstance(value, dict):
            # this is a nested setter -> call it for every single value
            field_item = field_type.create_non_definable(nested=False)
            # converts the flat dictionary into a nested dict
            nested_dict = convert_field_lookups_to_dict_structure(value)
            for cur_key, cur_value in nested_dict.items():
                inner_field_type, _ = field_item.get_field_data_type(cur_key)
                if isinstance(cur_value, dict) and isinstance(inner_field_type, SingleDataItem):
                    # this is another nested item -> call setter for that
                    field_item.set_field_value(cur_key, convert_dict_structure_to_field_lookups(cur_value))
                else:
                    # we can set this value directly
                    field_item.set_field_value(cur_key, cur_value)
            setattr(item, splitted_field_name[-1], field_item)
        else:
            # otherwise: update the specific field with the provided value
            setattr(item, splitted_field_name[-1], value)

    def all_fields_are_not_definable(self) -> bool:
        """
        :return: returns true in case all fields have the value `NOT_DEFINABLE`.
        """
        for cur_field in dataclasses.fields(self.__class__):

            cur_computed_value = getattr(self, cur_field.name)
            raw_type, _ = get_data_item_type(cur_field)
            if get_origin(raw_type) is not list and issubclass(raw_type, SingleDataItem):
                # expect another single data item as child
                if isinstance(cur_computed_value, SingleDataItem):
                    # overwrite value only if it is really a data item
                    cur_computed_value = NOT_DEFINABLE \
                        if cur_computed_value.all_fields_are_not_definable() else cur_computed_value
                # otherwise it is already usable for this method
            if cur_computed_value != NOT_DEFINABLE:
                return False
        return True

    def compare(
            self,
            other: SingleDataItemTypeT,
            ignore_field_lookups: List[str] | None = None,
            allow_non_definable: bool = False,
            validate_unique_identification_separately=True
    ) -> bool:
        error_msgs = self.get_difference_error_messages(
            other=other, ignore_field_lookups=ignore_field_lookups, allow_non_definable=allow_non_definable,
            validate_unique_identification_separately=validate_unique_identification_separately)
        return len(error_msgs) == 0

    def get_difference_error_messages(
            self,
            other: SingleDataItemTypeT,
            ignore_field_lookups: List[str] | None = None,
            allow_non_definable: bool = False,
            validate_unique_identification_separately=True
    ) -> List[str]:

        if allow_non_definable and (self.all_fields_are_not_definable() or other == NOT_DEFINABLE):
            return []

        if not isinstance(other, self.__class__):
            raise TypeError(f'`other` must be a `{self.__class__}` instance (is `{other}`)')

        # TODO rework this
        if ignore_field_lookups is None:
            ignore_field_lookups = []

        def needs_to_be_checked(self_val, other_val):
            if not allow_non_definable:
                return True
            self_val_is_not_definable = self_val == NOT_DEFINABLE or (
                    isinstance(self_val, SingleDataItem) and self_val.all_fields_are_not_definable()
            )
            other_val_is_not_definable = other_val == NOT_DEFINABLE or (
                    isinstance(other_val, SingleDataItem) and other_val.all_fields_are_not_definable()
            )
            if self_val_is_not_definable or other_val_is_not_definable:
                return False
            return True

        error_list = []

        if validate_unique_identification_separately:
            self_unique_identification = self.get_unique_identification()
            other_unqiue_identification = other.get_unique_identification()
            if needs_to_be_checked(self_unique_identification, other_unqiue_identification):
                if self_unique_identification != other_unqiue_identification:
                    error_list.append(f"detect different unique identification key - "
                                      f"self: `{self_unique_identification}` | other: `{other_unqiue_identification}`")

        for cur_field in dataclasses.fields(self.__class__):
            if ignore_field_lookups and cur_field.name in ignore_field_lookups:
                #logger.warning(f'field `{cur_field.name}` will not be validated because it is on ignore list')
                continue
            self_value = getattr(self, cur_field.name)
            other_value = getattr(other, cur_field.name)

            # set NOT_DEFINABLE in case all elements of the current objects are NOT_DEFINABLE
            if isinstance(self_value, SingleDataItem) and self_value.all_fields_are_not_definable():
                self_value = NOT_DEFINABLE
            if isinstance(other_value, SingleDataItem) and other_value.all_fields_are_not_definable():
                other_value = NOT_DEFINABLE

            if needs_to_be_checked(self_value, other_value):
                raw_type, _ = get_data_item_type(cur_field)

                if get_origin(raw_type) is list:
                    if allow_non_definable and self_value == NOT_DEFINABLE or other_value is NOT_DEFINABLE:
                        # ignore
                        continue
                    inner_type = get_args(raw_type)
                    if len(inner_type) != 1:
                        raise TypeError(f'unexpected type `{raw_type}`')
                    if get_origin(inner_type[0]) is None:
                        expect_a_data_item = issubclass(inner_type[0], SingleDataItem)
                    else:
                        expect_a_data_item = False
                    # make sure that both lists have the same length
                    if len(self_value) != len(other_value):
                        error_list.append(f"detect different list length for dataclass field `{cur_field.name}`: "
                                          f"self={len(self_value)}, other={len(other_value)}")
                    else:
                        # both lists have the same length -> start comparing items
                        for cur_self_item, cur_other_item in zip(self_value, other_value):
                            if needs_to_be_checked(cur_self_item, cur_other_item):
                                if not allow_non_definable and cur_self_item == NOT_DEFINABLE:
                                    error_list.append(f'detect not allowed NON_DEFINABLE value in list item '
                                                      f'`{cur_field.name}`: self={self_value} | other={other_value}')
                                    continue
                                if expect_a_data_item and isinstance(cur_self_item, SingleDataItem):
                                    error_list.extend(cur_self_item.get_difference_error_messages(cur_other_item))
                                else:
                                    # normal item -> compare values
                                    one_is_not_def = cur_self_item == NOT_DEFINABLE or cur_other_item is NOT_DEFINABLE
                                    if allow_non_definable and one_is_not_def:
                                        # okay
                                        continue
                                    if cur_self_item != cur_other_item:
                                        error_list.append(
                                            f"detect different value for dataclass field `{cur_field.name}` - "
                                            f"self: `{self_value}` | other: `{other_value}`")
                try:
                    is_nested = issubclass(raw_type, SingleDataItem)
                except TypeError:
                    is_nested = False

                if is_nested and self_value not in [None, NOT_DEFINABLE]:
                    # this is a nested item -> check it here too
                    ignore_fields_for_subfield = [
                        ignore[len(f"{cur_field.name}__"):]
                        for ignore in ignore_field_lookups
                        if ignore.startswith(f"{cur_field.name}__")
                    ]

                    if not self_value.compare(
                            other_value,
                            ignore_field_lookups=ignore_fields_for_subfield,
                            allow_non_definable=allow_non_definable,
                            validate_unique_identification_separately='id' not in ignore_fields_for_subfield):
                        error_list.append(f"detect different value for nested dataclass field `{cur_field.name}` - "
                                          f"self: `{self_value}` | other: `{other_value}`")
                elif allow_non_definable and self_value == NOT_DEFINABLE or other_value == NOT_DEFINABLE:
                    # no error for this field
                    continue
                elif self_value != other_value:
                    error_list.append(f"detect different value for dataclass field `{cur_field.name}` - "
                                      f"self: `{self_value}` | other: `{other_value}`")

        return error_list
