from __future__ import annotations
import dataclasses


@dataclasses.dataclass
class ResponseMessage:
    """
    Response message object, that is used for validating responses from data interactions.
    """
    # TODO should we make this more flexible by using a base class without elements?
    text: str
    body: str = None

    def __str__(self):
        return self.text

    def __eq__(self, other):
        # TODO allow regular expressions?
        return self.text == other.text and self.body == other.body
