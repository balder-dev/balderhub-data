from __future__ import annotations


class BaseResponseMessage:
    """
    Base Response message object, that is used for validating responses from data interactions.
    """

    def __eq__(self, other):
        raise NotImplementedError('this needs to be implemented within subclass')
