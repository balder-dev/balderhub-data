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

    def __str__(self):
        return '__'.join(self._field_keys)

    def __eq__(self, other):
        if not isinstance(other, (LookupFieldString, str)):
            return False
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))
