from __future__ import annotations
from typing import List
from .response_message import ResponseMessage


class ResponseMessageList:
    """
    holds a list of :class:`ResponseMessage` objects
    """
    def __init__(self, responses: List[ResponseMessage | str] = None):
        self._responses = []
        if responses is not None:
            for elem in responses:
                self.append(elem)

    def __str__(self):
        if len(self._responses) == 0:
            return f"{ResponseMessageList.__name__}([])"
        inner_text = '", "'.join([str(response) for response in self._responses])
        return f'["{inner_text}"]'

    def __bool__(self):
        return bool(self._responses)

    def __len__(self):
        return len(self._responses)

    def __iter__(self):
        return iter(self._responses)

    def append(self, elem: ResponseMessage | str) -> None:
        """
        This method adds a Response Message object to the list
        :param elem: the message that should be added
        """
        if isinstance(elem, str):
            self._responses.append(ResponseMessage(elem))
        elif isinstance(elem, ResponseMessage):
            self._responses.append(elem)
        else:
            raise TypeError('detect unexpected type for parameter `elem`')

    def copy(self):
        """
        This method copies the list. Note: The inner items will not be copied.
        :return: returns a copies list
        """
        return ResponseMessageList(self._responses.copy())

    def compare(self, other_list: ResponseMessageList) -> bool:
        """
        This method compares two response-message lists with each other.
        :param other_list: the other response-message list
        :return: True if both lists are equal, False otherwise
        """
        if len(self) != len(other_list):
            return False
        self_responses_copy = self._responses.copy()

        for other in other_list:
            if other not in self_responses_copy:
                return False
            self_responses_copy.remove(other)

        if len(self_responses_copy) > 0:
            return False
        return True
