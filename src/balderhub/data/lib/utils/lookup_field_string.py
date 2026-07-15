from __future__ import annotations


class LookupFieldString:
    """
    Helper class to represent a lookup field string
    """

    def __init__(self, *args: str | LookupFieldString):
        self._field_keys = []
        if len(args) == 0 or len(args) == 1 and args[0] == '':
            raise ValueError('empty lookup field string are not possible')
        for arg in args:
            if not isinstance(arg, (str, LookupFieldString)):
                raise TypeError('Argument must be a string')
            if len(args) == 1:
                self._field_keys = arg.split_field_keys if isinstance(arg, LookupFieldString) else arg.split('__')
            elif len(args) > 1:
                # make sure that there is no inner Lookup-Field String
                if '__' in str(arg):
                    raise ValueError('lookup strings and non lookup strings can not be mixed - double underscores in '
                                     'attribute names are not allowed')

                self._field_keys.append(str(arg))

    @property
    def split_field_keys(self) -> list[str]:
        """
        :return: returns a list of nested field names
        """
        return self._field_keys.copy()

    @property
    def nested_level(self) -> int:
        """
        :return: returns the number of nested field names (:meth:`LookupFieldString.split_field_keys`)
        """
        return len(self.split_field_keys)

    def add_sub_field(self, field: str | LookupFieldString):
        """
        Adds another lookup field to this lookup field string
        :param field: the field or lookup field that should be added
        :return: a new lookup field string with the appended sub-field / sub-lookup field
        """
        field = LookupFieldString(field)
        return self.__class__(*self.split_field_keys, *field.split_field_keys)

    def startswith(self, value: str | LookupFieldString) -> bool:
        """
        Check if the string representation of the instance starts with the specified value.

        :param value: The string or LookupFieldString to compare against the start of the instance's
            string representation.
        :return: True if the instance's string representation starts with the given lookup parts,
            otherwise False.
        """
        value_parts = LookupFieldString(value).split_field_keys
        return self.split_field_keys[:len(value_parts)] ==  value_parts

    def relative_to(self, value: str | LookupFieldString) -> LookupFieldString | None:
        """
        Returns a new `LookupFieldString` object representing the path relative to the provided `value`,
        or `None` if the provided `value` is an empty string. If the provided `value` is not a part of
        the current `LookupFieldString`, a `ValueError` is raised.

        :param value: The base `LookupFieldString` or string against which the relative path is calculated.
        :return: A new `LookupFieldString` object representing the relative path, or `None` if the input
            `value` is an empty string.
        :raises ValueError: If `value` is not part of the current `LookupFieldString`.
        """
        if value == '':
            return self
        if not self.startswith(value):
            raise ValueError(f'given `{value}` is not part of this `{self}`')
        start_idx = len(LookupFieldString(value).split_field_keys)
        relative_field_parts = self.split_field_keys[start_idx:]
        return LookupFieldString(*relative_field_parts) if relative_field_parts else None

    def __str__(self):
        return '__'.join(self._field_keys)

    def __repr__(self):
        return f"LookupFieldString('{self._field_keys}')"

    def __eq__(self, other):
        if not isinstance(other, (LookupFieldString, str)):
            return False
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))
