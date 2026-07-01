from __future__ import annotations
from typing import Optional

from .base_response_message import BaseResponseMessage


class ResponseMessage(BaseResponseMessage):
    """
    Response message object, that is used for validating responses from data interactions.
    """

    def __init__(self, text: str, body: Optional[str] = None):
        self._text = text
        self._body = body

    def __str__(self):
        return f'ResponseMessage<"{self.text}">'

    def __eq__(self, other):
        # TODO allow regular expressions?
        return self.text == other.text and self.body == other.body

    @property
    def text(self) -> str:
        """
        :return: returns the response message main text
        """
        return self._text

    @property
    def body(self) -> Optional[str]:
        """
        :return: returns an optional body of the response message or None otherwise
        """
        return self._body
