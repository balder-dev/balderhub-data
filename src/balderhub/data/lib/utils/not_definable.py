

class _NOT_DEFINABLE_TYPE(object):

    def __eq__(self, other):
        return isinstance(other, _NOT_DEFINABLE_TYPE)

NOT_DEFINABLE = _NOT_DEFINABLE_TYPE()
