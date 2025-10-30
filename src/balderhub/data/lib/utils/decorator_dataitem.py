import dataclasses
from typing import List, Optional, Union, get_args, get_origin

from .exceptions import MisconfiguredDataclassError

# TODO also forbid loops

def dataitem(cls=None, /, *, init=True, repr=True, eq=True, order=False,
             unsafe_hash=False, frozen=False, match_args=True,
             kw_only=False, slots=False):
    """
    This decorator is specially for data classes in the balderhub data environment. It uses the normal
    `@dataclasses.dataclass` decorator but extend the functionality to be compatible with this balderhub project.

    .. note::
        Compared to the normal `dataclasses.dataclass` decorator, this decorator ensures additionally that:
        * no default values are present
        * the typing does not allow different types for one field (except None)
        * no nested types except ``Union[X, None]`` or ``Optional[X]`` are used
        * only Union, Optional, list, List are used

    :param init: if true, an __init__() method is added to the class
    :param repr: if true, a __repr__() method is added to the class
    :param eq: if true, an __eq__() method is added to the class
    :param order: if true, rich comparison dunder methods are added
    :param unsafe_hash: if true, an __hash__() method is added to the class
    :param frozen: if true, fields may not be assigned to after instance creation
    :param match_args: if true, the __match_args__ tuple is added
    :param kw_only: if true, then by default all fields are keyword-only
    :param slots: if true, an __slots__ attribute is added.
    """
    none_type = type(None)

    wrapped_cls = dataclasses.dataclass(
        cls,
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
        match_args=match_args,
        kw_only=kw_only,
        slots=slots
    )

    def _validate_element(type_def, allow_nesting=True):
        # now check the type
        if isinstance(type_def, type):
            # references a type
            return
        elif allow_nesting:
            # references another type definition
            if get_origin(type_def) in [list, List]:
                inner_args = get_args(type_def)
                if len(inner_args) != 1:
                    raise MisconfiguredDataclassError('list type definition can only have one argument for '
                                                      'balderhub-data dataclasses')
                _validate_element(inner_args[0])
            elif get_origin(type_def) is Optional:
                inner_args = get_args(type_def)
                if len(inner_args) != 1:
                    raise MisconfiguredDataclassError('Option type definition can only have one argument for '
                                                      'balderhub-data dataclasses')
                _validate_element(inner_args[0], allow_nesting=False)
            elif get_origin(type_def) is Union:
                inner_args = list(get_args(type_def))
                if len(inner_args) == 1:
                    _validate_element(inner_args[0], allow_nesting=False)
                elif len(inner_args) == 2 and none_type in inner_args:
                    # make sure that `None` is part of it
                    inner_args.remove(none_type)
                    _validate_element(inner_args[0], allow_nesting=False)
                else:
                    raise MisconfiguredDataclassError('Union type definition with multiple inner arguments '
                                                      '(except None) is not allowed in balderhub-data dataclasses')
            else:
                raise MisconfiguredDataclassError(f'type definition `{type_def}` are not possible in balderhub-data dataclasses')
        else:
            raise MisconfiguredDataclassError(f'nesting typing is only allowed for list')

    # validate used fields
    for cur_field in dataclasses.fields(wrapped_cls):
        if cur_field.default is not dataclasses.MISSING and cur_field.default_factory is not dataclasses.MISSING:
            raise MisconfiguredDataclassError(f"{cur_field.name} has default value which is not allowed for "
                                              f"balderhub-data dataclasses")
        _validate_element(cur_field.type)
    return wrapped_cls
