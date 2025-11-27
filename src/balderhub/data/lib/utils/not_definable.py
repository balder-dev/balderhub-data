

# pylint: disable-next=invalid-name
class _NOT_DEFINABLE_TYPE:
    """
    Type for NON_DEFINABLE values. This object is assigned for all fields that are unable to define either by user or
    by data interacting features.
    """

    def __eq__(self, other):
        return isinstance(other, _NOT_DEFINABLE_TYPE)

NOT_DEFINABLE = _NOT_DEFINABLE_TYPE()
