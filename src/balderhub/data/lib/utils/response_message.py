from __future__ import annotations
import dataclasses


@dataclasses.dataclass
class ResponseMessage:
    text: str
    body: str = None

    def __str__(self):
        return self.text

    def __eq__(self, other):
        # TODO allow regular expressions?
        return self.text == other.text and self.body == other.body
