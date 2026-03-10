from __future__ import annotations

from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.response_message import ResponseMessage
from balderhub.data.lib.utils.response_message_list import ResponseMessageList


class ScenarioUtilsResponseMessageList(ScenarioUnit):
    """Unit-like tests for ResponseMessageList class."""

    def test_response_message_list_init_empty(self):
        msg_list = ResponseMessageList()
        assert len(msg_list) == 0
        assert not msg_list

    def test_response_message_list_init_with_strings(self):
        msg_list = ResponseMessageList(["Error 1", "Error 2"])
        assert len(msg_list) == 2
        assert isinstance(msg_list[0], ResponseMessage)
        assert msg_list[0] == ResponseMessage('Error 1')
        assert isinstance(msg_list[1], ResponseMessage)
        assert msg_list[1] == ResponseMessage('Error 2')
        assert bool(msg_list)

    def test_response_message_list_init_with_response_messages(self):
        msg1 = ResponseMessage(text="Error 1")
        msg2 = ResponseMessage(text="Error 2")
        msg_list = ResponseMessageList([msg1, msg2])
        assert len(msg_list) == 2
        assert isinstance(msg_list[0], ResponseMessage)
        assert msg_list[0] == ResponseMessage('Error 1')
        assert isinstance(msg_list[1], ResponseMessage)
        assert msg_list[1] == ResponseMessage('Error 2')
        assert bool(msg_list)

    def test_response_message_list_init_with_mixed_types(self):
        msg1 = ResponseMessage(text="Error 1")
        msg_list = ResponseMessageList([msg1, "Error 2"])
        assert len(msg_list) == 2
        assert isinstance(msg_list[0], ResponseMessage)
        assert msg_list[0] == ResponseMessage('Error 1')
        assert isinstance(msg_list[1], ResponseMessage)
        assert msg_list[1] == ResponseMessage('Error 2')
        assert bool(msg_list)

    def test_response_message_list_str_empty(self):
        msg_list = ResponseMessageList()
        assert str(msg_list) == "ResponseMessageList([])"

    def test_response_message_list_str_single_item(self):
        msg_list = ResponseMessageList(["Error"])
        assert str(msg_list) == '["Error"]'

    def test_response_message_list_str_multiple_items(self):
        msg_list = ResponseMessageList(["Error 1", "Error 2"])
        assert str(msg_list) == '["Error 1", "Error 2"]'

    def test_response_message_list_bool_empty_is_false(self):
        msg_list = ResponseMessageList()
        assert not msg_list

    def test_response_message_list_bool_non_empty_is_true(self):
        msg_list = ResponseMessageList(["Error"])
        assert bool(msg_list)

    def test_response_message_list_len_empty(self):
        msg_list = ResponseMessageList()
        assert len(msg_list) == 0

    def test_response_message_list_len_non_empty(self):
        msg_list = ResponseMessageList(["Error 1", "Error 2", "Error 3"])
        assert len(msg_list) == 3

    def test_response_message_list_iter(self):
        msg_list = ResponseMessageList(["Error 1", "Error 2"])
        assert len(msg_list) == 2
        assert isinstance(msg_list[0], ResponseMessage)
        assert isinstance(msg_list[1], ResponseMessage)
        assert msg_list[0].text == "Error 1"
        assert msg_list[0].body is None
        assert msg_list[1].text == "Error 2"
        assert msg_list[1].body is None

    def test_response_message_list_append_string(self):
        msg_list = ResponseMessageList()
        msg_list.append("Error 1")
        assert len(msg_list) == 1
        assert isinstance(msg_list[0], ResponseMessage)
        assert msg_list[0].text == "Error 1"
        assert msg_list[0].body is None

    def test_response_message_list_append_response_message(self):
        msg_list = ResponseMessageList()
        msg = ResponseMessage(text="Error 1", body="Details")
        msg_list.append(msg)
        assert len(msg_list) == 1
        assert msg_list[0] == msg
        assert msg_list[0].text == "Error 1"
        assert msg_list[0].body == "Details"

    def test_response_message_list_append_invalid_type_raises_type_error(self):
        msg_list = ResponseMessageList()
        try:
            msg_list.append(123)  # type: ignore[arg-type]
            assert False, "TypeError expected for invalid type"
        except TypeError as exc:
            assert exc.args[0] == "detect unexpected type for parameter `elem`", exc

    def test_response_message_list_append_none_raises_type_error(self):
        msg_list = ResponseMessageList()
        try:
            msg_list.append(None)  # type: ignore[arg-type]
            assert False, "TypeError expected for None"
        except TypeError as exc:
            assert exc.args[0] == "detect unexpected type for parameter `elem`", exc

    def test_response_message_list_copy_creates_new_list(self):
        msg_list = ResponseMessageList(["Error 1", "Error 2"])
        copied_list = msg_list.copy()
        assert len(copied_list) == 2
        assert copied_list is not msg_list
        assert copied_list == msg_list

    def test_response_message_list_copy_shares_inner_items(self):
        msg = ResponseMessage(text="Error 1")
        msg_list = ResponseMessageList([msg])
        copied_list = msg_list.copy()
        # Inner items are not copied (as documented)
        assert list(copied_list)[0] is list(msg_list)[0]

    def test_response_message_list_copy_modification_does_not_affect_original(self):
        msg_list = ResponseMessageList(["Error 1"])
        copied_list = msg_list.copy()
        copied_list.append("Error 2")
        assert len(msg_list) == 1
        assert len(copied_list) == 2

    def test_response_message_list_compare_empty_lists(self):
        list1 = ResponseMessageList()
        list2 = ResponseMessageList()
        assert list1.compare(list2)

    def test_response_message_list_compare_identical_single_item(self):
        list1 = ResponseMessageList(["Error"])
        list2 = ResponseMessageList(["Error"])
        assert list1.compare(list2)

    def test_response_message_list_compare_identical_multiple_items(self):
        list1 = ResponseMessageList(["Error 1", "Error 2"])
        list2 = ResponseMessageList(["Error 1", "Error 2"])
        assert list1.compare(list2)

    def test_response_message_list_compare_different_order_same_items(self):
        list1 = ResponseMessageList(["Error 1", "Error 2"])
        list2 = ResponseMessageList(["Error 2", "Error 1"])
        assert list1.compare(list2)

    def test_response_message_list_compare_different_lengths(self):
        list1 = ResponseMessageList(["Error 1"])
        list2 = ResponseMessageList(["Error 1", "Error 2"])
        assert not list1.compare(list2)

    def test_response_message_list_compare_different_items(self):
        list1 = ResponseMessageList(["Error 1"])
        list2 = ResponseMessageList(["Error 2"])
        assert not list1.compare(list2)

    def test_response_message_list_compare_with_duplicates(self):
        list1 = ResponseMessageList(["Error 1", "Error 1"])
        list2 = ResponseMessageList(["Error 1", "Error 1"])
        assert list1.compare(list2)

    def test_response_message_list_compare_with_mismatched_duplicates(self):
        list1 = ResponseMessageList(["Error 1", "Error 1"])
        list2 = ResponseMessageList(["Error 1", "Error 2"])
        assert not list1.compare(list2)

    def test_response_message_list_compare_with_body_differences(self):
        msg1 = ResponseMessage(text="Error", body="Details A")
        msg2 = ResponseMessage(text="Error", body="Details B")
        list1 = ResponseMessageList([msg1])
        list2 = ResponseMessageList([msg2])
        assert not list1.compare(list2)

    def test_response_message_list_compare_with_matching_body(self):
        msg1 = ResponseMessage(text="Error", body="Details")
        msg2 = ResponseMessage(text="Error", body="Details")
        list1 = ResponseMessageList([msg1])
        list2 = ResponseMessageList([msg2])
        assert list1.compare(list2)
