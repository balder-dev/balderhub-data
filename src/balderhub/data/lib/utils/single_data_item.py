from __future__ import annotations

import logging
import types
import typing
from abc import ABC, abstractmethod
from typing import List, TypeVar, Any, Union, get_args, get_origin, Optional

import pydantic

from .exceptions import MisconfiguredDataItemError
from .functions import convert_field_lookups_to_dict_structure
from .lookup_field_string import LookupFieldString
from .not_definable import NOT_DEFINABLE


logger = logging.getLogger(__name__)

class SingleDataItemMetaclass(type(pydantic.BaseModel)):
    """metaclass for data item"""
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        __pydantic_generic_metadata__: pydantic.PydanticGenericMetadata = None,
        __pydantic_reset_parent_namespace__: bool = True,
        _create_model_module: str | None = None,
        **kwargs: Any,
    ):
        # go though annotations
        for field_name, cur_field_annotation in namespace.get('__annotations__', {}).items():
            mcs._validate_element(cur_field_annotation)
            if field_name in namespace:
                # field has a default value
                raise ValueError("no default values allowed for balderhub-data type definitions")

            if '__' in field_name:
                raise KeyError('no double underscores are allowed in field names')

            # additional make sure that every field can always have the type `NON_DEFINABLE`
            namespace['__annotations__'][field_name] = Union[cur_field_annotation, type(NOT_DEFINABLE)]

        return super().__new__(mcs, cls_name, bases, namespace, **kwargs)

    @classmethod
    def _validate_element(mcs, type_def, allow_nesting=True):
        none_type = type(None)

        # now check the type
        if isinstance(type_def, type):
            # references a type
            return
        if not allow_nesting:
            raise MisconfiguredDataItemError('nesting typing is only allowed for list')
        # references another type definition
        if get_origin(type_def) in [list, List]:
            inner_args = get_args(type_def)
            if len(inner_args) != 1:
                raise MisconfiguredDataItemError('list type definition can only have one argument for '
                                                  'balderhub-data dataclasses')
            mcs._validate_element(inner_args[0])
        elif get_origin(type_def) is Optional:
            inner_args = get_args(type_def)
            if len(inner_args) != 1:
                raise MisconfiguredDataItemError('Option type definition can only have one argument for '
                                                  'balderhub-data dataclasses')
            mcs._validate_element(inner_args[0], allow_nesting=False)
        elif get_origin(type_def) is Union:
            inner_args = list(get_args(type_def))
            if len(inner_args) == 1:
                mcs._validate_element(inner_args[0], allow_nesting=False)
            elif len(inner_args) == 2 and none_type in inner_args:
                # make sure that `None` is part of it
                inner_args.remove(none_type)
                mcs._validate_element(inner_args[0], allow_nesting=False)
            else:
                raise MisconfiguredDataItemError('Union type definition with multiple inner arguments '
                                                  '(except None) is not allowed in balderhub-data dataclasses')
        else:
            raise MisconfiguredDataItemError(f'type definition `{type_def}` are not possible in balderhub-data '
                                              f'dataclasses')


class SingleDataItem(pydantic.BaseModel, ABC, metaclass=SingleDataItemMetaclass):
    """
    This is a base class for data items. Data items are pydantic `BaseModel` classes that are used for defining the
    model to test.
    """
    # make the whole model strict
    # do not allow non-declared data
    # do validate types also during assignment
    model_config = pydantic.ConfigDict(strict=True, extra='forbid', validate_assignment=True)

    @abstractmethod
    def get_unique_identification(self):
        """
        Individual method that returns a unique identifier for the data item.
        :return: a unique identifier for the specific data item object
        """
        raise NotImplementedError

    @classmethod
    def create_as_nested(cls, **kwargs):
        """
        Class method for create a data item out of field-lookups (attribute name)
        :param kwargs: the field lookups with its value
        :return: the instantiated data item
        """
        json_dict = convert_field_lookups_to_dict_structure(kwargs, nested=False)
        return cls(**json_dict)

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
    def get_field(cls, field_lookup: str | LookupFieldString) -> pydantic.fields.FieldInfo:
        """
        Returns the specific data class field by its field lookup name

        :param field_lookup: the field lookup string
        :return: the pydantic field
        """

        field_lookup = LookupFieldString(field_lookup)

        split_field_str = field_lookup.split_field_keys

        first_field_part = split_field_str.pop(0)
        field_info = cls.__pydantic_fields__.get(first_field_part)
        if field_info is None:
            raise KeyError(f'can not find a field `{first_field_part}` in data item `{cls.__name__}`')


        if len(split_field_str) > 0:
            # go deeper
            subtype = cls.get_field_data_type(first_field_part)
            if not issubclass(subtype, SingleDataItem):
                raise KeyError(f'the subkey `{first_field_part}` does not reference a data item type in data '
                               f'item `{cls.__name__}`')
            return subtype.get_field(LookupFieldString(*split_field_str))
        return field_info

    @classmethod
    def is_optional_field(cls, field_lookup: str | LookupFieldString, consider_upper_optionals_too=True) -> bool:
        """
        This method checks if the field is optional. If `consider_upper_optionals_too=True` it will check the type
        definitions of any field in the field chain too and returns Ture as soon as one element is defined as optional.

        :param field_lookup: the field lookup string
        :param consider_upper_optionals_too:
        :return: True if the field is optional, False otherwise
        """
        none_type = type(None)

        field_lookup = LookupFieldString(field_lookup)
        field_info = cls.get_field(field_lookup)
        # check for usage of `typing.Optional[xx]`
        if get_origin(field_info.annotation) is Optional:
            return True
        # check for usage of `typing.Union[xx, None]`
        if get_origin(field_info.annotation) is Union:
            inner_args = set(get_args(field_info.annotation))
            if type(NOT_DEFINABLE) in inner_args:
                inner_args.remove(type(NOT_DEFINABLE))
            if len(inner_args) == 2 and none_type in inner_args:
                return True
        if consider_upper_optionals_too and len(field_lookup.split_field_keys) > 1:
            return cls.is_optional_field(LookupFieldString(*field_lookup.split_field_keys[:-1]))
        return False

    @classmethod
    def get_element_type_for_list(cls, field_lookup: str | LookupFieldString) -> type:
        """
        This method returns the inner element type for the requested field. It will recheck that the provided field
        references a list before.

        :param field_lookup: the field lookup string
        :return: the data type the list items should have
        """
        cleaned_type = cls.get_cleaned_field_data_type(field_lookup)
        if get_origin(cleaned_type) != list:
            raise TypeError(f'the referenced field `{field_lookup}` is no list (is from type `{cleaned_type}`)')
        # check inner type
        inner_args = get_args(cleaned_type)
        if len(inner_args) == 1:
            return inner_args[0]
        if len(inner_args) == 0:
            raise TypeError('list needs to have exactly one item type definition -> none detected')
        raise TypeError(f"list needs to have exactly one item type definition -> multiple detected: `{inner_args}`")

    @classmethod
    def get_all_fields_for(
            cls,
            subkey: str | LookupFieldString | None = None,
            nested = True,
            except_fields: list[str | LookupFieldString]=None
    ) -> list[str]:
        """
        This method returns a list with all field names, that matches the requested filter.

        :param subkey: all fields that belongs to this subkey are returned - if this is None, all fields of this data
                       item are returned.
        :param nested: True if the method should return all nested fields and not only the direct fields
        :param except_fields: a list of fields to exclude from the returned list (if subkey is given, they are
                              relative to this subkey, otherwise they are relative to this data item)
        :return: a list of fields as strings in lookup syntax (concat with `__`)
        """
        except_fields = [] if except_fields is None else except_fields

        # make except-fields absolute
        if subkey is not None:
            subkey = LookupFieldString(subkey)
            abs_except_fields = [subkey.add_sub_field(f) for f in except_fields]
            data_item_type = cls.get_field_data_type(subkey)
        else:
            abs_except_fields = [LookupFieldString(f) for f in except_fields]
            data_item_type = cls

        rel_field_list = []

        if not issubclass(data_item_type, SingleDataItem):
            # it is not a nested item -> return subkey as the only possibility (needs to be set, because otherwise
            # this can not be a SingleDataItem)
            return [str(subkey)]

        for cur_field_name in data_item_type.__pydantic_fields__.keys():
            cur_field_type = data_item_type.get_field_data_type(cur_field_name)
            if nested and issubclass(cur_field_type, SingleDataItem):
                nested_fields = cur_field_type.get_all_fields_for(subkey=None, nested=True, except_fields=None)

                # finally add these fields with the cur_field_name as prefix
                rel_field_list.extend([LookupFieldString(cur_field_name).add_sub_field(f) for f in nested_fields])
            else:
                rel_field_list.append(cur_field_name)

        # now convert these relative field-lookups into absolute (based on this)
        if subkey is None:
            # rel is absolute
            result = rel_field_list
        else:
            result = [str(LookupFieldString(subkey).add_sub_field(rel_field)) for rel_field in rel_field_list]

        # filter all except-fields
        for cur_except_field in abs_except_fields:
            if cur_except_field not in result:
                raise KeyError(f'can not find except_field `{cur_except_field}` in possible data: {result}')
        return [str(f) for f in result if f not in abs_except_fields]

    @classmethod
    def get_cleaned_field_data_type(cls, field_lookup: LookupFieldString | str) -> type | types.GenericAlias:
        """
        This method returns the specific data type of a field. It automatically resolves subscripted type definitions.
        :param field_lookup: the field lookup string
        :return: the cleared type spec (can be a normal type, `Optional[type]` or `list[type]`)
        """

        def get_data_item_type(field_info: pydantic.fields.FieldInfo) -> type:
            """
            returns the usable type for this field and a boolean value if this type can be optional or not

            .. note::
                It can also return a list type!

            :param field_info: the pydantic `FieldInfo` object method should be applied too
            """
            none_type = type(None)

            if field_info.annotation is None:
                raise TypeError(f'no type is specified for {field_info}')

            # now check the type
            if isinstance(field_info.annotation, (type, types.GenericAlias)):
                # references a type
                return field_info.annotation

            # references another type definition
            if get_origin(field_info.annotation) in [list, List]:
                inner_args = set(get_args(field_info.annotation))
                if len(inner_args) != 1:
                    raise TypeError(f'unsupported type {field_info.annotation}')
                return list[inner_args.pop()]

            if get_origin(field_info.annotation) is Union:
                inner_args = set(get_args(field_info.annotation))

                # make sure that only `None` or `NOT_DEFINABLE` are mentioned within Union arguments
                cleared_args = set(inner_args) - {none_type, type(NOT_DEFINABLE)}
                if len(cleared_args) != 1:
                    raise TypeError(f'unsupported union type {field_info.annotation}')
                if none_type in inner_args:
                    return Optional[cleared_args.pop()]

                return cleared_args.pop()

            raise TypeError(f'type definition `{field_info.annotation}` are not possible in balderhub-data dataclasses')

        return get_data_item_type(cls.get_field(field_lookup))

    @classmethod
    def get_field_data_type(cls, field_lookup: LookupFieldString | str) -> type:
        """
        This method returns the specific data type of a field. It automatically resolves subscripted type definitions.
        :param field_lookup: the field lookup string
        :return: the unsubscripted field type
        """
        cleaned_field_type = cls.get_cleaned_field_data_type(field_lookup)

        if isinstance(cleaned_field_type, type) and not isinstance(cleaned_field_type, types.GenericAlias):
            # references a type
            return cleaned_field_type

        if get_origin(cleaned_field_type) in [list, List]:
            return list

        if get_origin(cleaned_field_type) is Optional:
            return get_args(cleaned_field_type)[0]

        if get_origin(cleaned_field_type) is typing.Union:
            inner_args = set(get_args(cleaned_field_type))
            cleaned_inner_args = set(inner_args) - {type(None)}
            if len(cleaned_inner_args) != 1:
                raise TypeError(f'get unexpected type definition `{cleaned_field_type}`')
            return cleaned_inner_args.pop()

        raise TypeError(f'got unexpected type {cleaned_field_type}')

    def get_field_value(self, field_lookup: str):
        """
        This method returns the value of the provided field.

        :param field_lookup: the field lookup string
        :return: the field value
        """
        item = self
        for cur_splitted_name in LookupFieldString(field_lookup).split_field_keys:
            if item == NOT_DEFINABLE:
                return NOT_DEFINABLE
            if not hasattr(item, cur_splitted_name):
                raise KeyError(f'can not find field `{cur_splitted_name}` in `{item}`')
            item = getattr(item, cur_splitted_name)
        return item

    def set_field_value(self, field_lookup: str, value: Any, only_change_this_value=False) -> None:
        """
        This method sets a specific value in the data item. It sets the value that is provided as `field_name` inside
        the data item. In case the field_name is a nested lookup field, it will overwrite the nested items by setting a
        new data item for the nested field. In case the value is a dictionary matching the definition of the data item
        type of the nested field, it will set all values that are provided in this dict. Any other value will be set
        with `NOT_DEFINABLE`.

        :param field_lookup: the name of the field (nested lookup field allowed)
        :param value: the value that should be set (dicts for nested structures are allowed)
        :param only_change_this_value: this value is given in case that the method should not recreate all nested data
                                       items and set their undefined values to `NOT_DEFINABLE`
        """
        item = self

        # first resolve all nested lookup fields
        split_field_name = LookupFieldString(field_lookup).split_field_keys

        # -> go through all nested fields and create new empty sub data item if necessary
        for cur_field_name in split_field_name[:-1]:
            new_item = getattr(item, cur_field_name)
            new_item_type = item.get_field_data_type(cur_field_name)

            if not issubclass(new_item_type, SingleDataItem):
                raise KeyError(f'the field `{cur_field_name}` of data item type `{item.__class__}` is no data item'
                               f' - can not set nested value here')

            # always create new object for nested value (if `only_change_this_value is False` or if field is empty)!
            if not only_change_this_value or new_item in [None, NOT_DEFINABLE]:
                new_item = new_item_type.create_non_definable(nested=False)
                setattr(item, cur_field_name, new_item)
            item = new_item

        setattr(item, split_field_name[-1], value)

    def all_fields_are_not_definable(self) -> bool:
        """
        :return: returns true in case all fields have the value `NOT_DEFINABLE`.
        """
        for cur_field_name, _ in self.__pydantic_fields__.items():

            cur_computed_value = getattr(self, cur_field_name)
            raw_type = self.get_field_data_type(cur_field_name)
            # TODO what is with lists?
            if issubclass(raw_type, SingleDataItem) and isinstance(cur_computed_value, SingleDataItem):
                # overwrite value only if it is really a data item
                cur_computed_value = NOT_DEFINABLE \
                    if cur_computed_value.all_fields_are_not_definable() else cur_computed_value
                # otherwise it is already usable for this method
            if cur_computed_value != NOT_DEFINABLE:
                return False
        return True

    @classmethod
    def all_field_lookups_are_within(
            cls,
            field_lookup: str | LookupFieldString,
            within_list_of_lookups: list[str|LookupFieldString]
    ) -> bool:
        """
        Helper method that returns True if the provided single-data-item field is within the provided lookup
        list. Both needs to be relative to this single-data-item.

        .. note::
            It also returns True if the field given by `field_lookup` is from type `SingleDataItem` too and all
            their resolved lookups are contained within the `within_list_of_lookups` list.


        :param field_lookup: the field lookup of the field that should be checked
        :param within_list_of_lookups: a list of fully resolved lookups
        :return: True if the `field_lookup` is within the `within_list_of_lookups` list
        """
        # execute it here for validation if the field_lookup is part of this data item
        field_type = cls.get_field_data_type(field_lookup)

        if field_lookup in within_list_of_lookups:
            return True

        if not issubclass(field_type, SingleDataItem):
            return False
        all_fields_of_field = [
            LookupFieldString(field_lookup).add_sub_field(f)
            for f in field_type.get_all_fields_for(nested=True)
        ]
        for cur_sub_field in all_fields_of_field:
            if cur_sub_field not in within_list_of_lookups:
                return False
        return True

    def compare(
            self,
            other: SingleDataItemTypeT,
            ignore_field_lookups: List[str] | None = None,
            allow_non_definable: bool = False,
            validate_unique_identification_separately=True
    ) -> bool:
        """
        This method compares a data item with another data item from same type.
        :param other: the other data item to compare with
        :param ignore_field_lookups: a list with field lookups that should be ignored
        :param allow_non_definable: True if the method should ignore fields for which one data item has the value
                                    `NOT_DEFINABLE`
        :param validate_unique_identification_separately: True if the method should validate the unique-identification
                                                          value (provided with
                                                          :meth:`SingleDataItem.get_unique_identification`) separately
        :return: True if the data of both data item objects are equal
        """
        error_msgs = self.get_difference_error_messages(
            other=other, ignore_field_lookups=ignore_field_lookups, allow_non_definable=allow_non_definable,
            validate_unique_identification_separately=validate_unique_identification_separately)
        return len(error_msgs) == 0

    # pylint: disable-next=too-many-locals,too-many-branches
    def get_difference_error_messages(
            self,
            other: SingleDataItemTypeT,
            ignore_field_lookups: List[str] | None = None,
            allow_non_definable: bool = False,
            validate_unique_identification_separately=True
    ) -> List[str]:
        """

        :param other: the other data item to compare with
        :param ignore_field_lookups: a list with field lookups that should be ignored
        :param allow_non_definable: True if the method should ignore fields for which one data item has the value
                                    `NOT_DEFINABLE`
        :param validate_unique_identification_separately: True if the method should validate the unique-identification
                                                          value (provided with
                                                          :meth:`SingleDataItem.get_unique_identification`) separately
        :return: A list with detected error messages
        """
        fully_flatted_ignore_fields = []
        #: flatten the ignore field (add all absolute flatten fields if the given ignore-field is nested)
        if ignore_field_lookups:
            for cur_ignore_field in ignore_field_lookups:
                fully_flatted_ignore_fields.extend(self.__class__.get_all_fields_for(cur_ignore_field))

        if allow_non_definable and (self.all_fields_are_not_definable() or other == NOT_DEFINABLE):
            return []

        if not isinstance(other, self.__class__):
            raise TypeError(f'`other` must be a `{self.__class__}` instance (is `{other}`)')

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
            self_unique_id = self.get_unique_identification()
            other_unique_id = other.get_unique_identification()
            if needs_to_be_checked(self_unique_id, other_unique_id) and self_unique_id != other_unique_id:
                error_list.append(f"detect different unique identification key - "
                                  f"self: `{self_unique_id}` | other: `{other_unique_id}`")

        for cur_field_name in self.__class__.get_all_fields_for(subkey=None, nested=True):
            if cur_field_name in fully_flatted_ignore_fields:
                #logger.warning(f'field `{cur_field.name}` will not be validated because it is on ignore list')
                continue
            self_value = self.get_field_value(cur_field_name)
            other_value = other.get_field_value(cur_field_name)

            if not needs_to_be_checked(self_value, other_value):
                continue

            if self.get_field_data_type(cur_field_name) is list:
                if allow_non_definable and self_value == NOT_DEFINABLE or other_value is NOT_DEFINABLE:
                    # ignore
                    continue
                inner_type = self.get_element_type_for_list(cur_field_name)

                # make sure that both lists have the same length
                if len(self_value) != len(other_value):
                    error_list.append(f"detect different list length for dataclass field `{cur_field_name}`: "
                                      f"self={len(self_value)}, other={len(other_value)}")
                else:
                    # both lists have the same length -> start comparing items
                    for cur_self_item, cur_other_item in zip(self_value, other_value):
                        if not needs_to_be_checked(cur_self_item, cur_other_item):
                            continue
                        if not allow_non_definable and cur_self_item == NOT_DEFINABLE:
                            error_list.append(f'detect not allowed NON_DEFINABLE value in list item '
                                              f'`{cur_field_name}`: self={self_value} | other={other_value}')
                            continue
                        # a sub SingleDataItem was expected and make sure that it is one
                        if issubclass(inner_type, SingleDataItem) and isinstance(cur_self_item, SingleDataItem):
                            error_list.extend(cur_self_item.get_difference_error_messages(cur_other_item))
                            continue
                        # normal item -> compare values
                        one_is_not_def = cur_self_item == NOT_DEFINABLE or cur_other_item is NOT_DEFINABLE
                        if allow_non_definable and one_is_not_def:
                            # okay
                            continue
                        if cur_self_item != cur_other_item:
                            error_list.append(
                                f"detect different value for dataclass field `{cur_field_name}` - "
                                f"self: `{self_value}` | other: `{other_value}`")
            elif self_value != other_value:
                error_list.append(f"detect different value for dataclass field `{cur_field_name}` - "
                                  f"self: `{self_value}` | other: `{other_value}`")

        return error_list

SingleDataItemTypeT = TypeVar("SingleDataItemTypeT", bound=SingleDataItem)
