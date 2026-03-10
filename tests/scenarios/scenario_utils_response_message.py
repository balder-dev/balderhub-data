from __future__ import annotations

from balderhub.unit.scenarios import ScenarioUnit

from balderhub.data.lib.utils.response_message import ResponseMessage


class ScenarioUtilsResponseMessage(ScenarioUnit):
    """Unit-like tests for ResponseMessage class."""

    def test_response_message_init_with_text_only(self):
        msg = ResponseMessage(text="Error occurred")
        assert msg.text == "Error occurred"
        assert msg.body is None

    def test_response_message_init_with_text_and_body(self):
        msg = ResponseMessage(text="Error occurred", body="Detailed error message")
        assert msg.text == "Error occurred"
        assert msg.body == "Detailed error message"

    def test_response_message_str_returns_text(self):
        msg = ResponseMessage(text="Warning message", body="Extra details")
        assert str(msg) == "Warning message"

    def test_response_message_str_with_text_only(self):
        msg = ResponseMessage(text="Info")
        assert str(msg) == "Info"

    def test_response_message_equality_both_text_and_body_match(self):
        msg1 = ResponseMessage(text="Error", body="Details")
        msg2 = ResponseMessage(text="Error", body="Details")
        assert msg1 == msg2

    def test_response_message_equality_text_only_match(self):
        msg1 = ResponseMessage(text="Warning")
        msg2 = ResponseMessage(text="Warning")
        assert msg1 == msg2

    def test_response_message_inequality_different_text(self):
        msg1 = ResponseMessage(text="Error", body="Details")
        msg2 = ResponseMessage(text="Warning", body="Details")
        assert msg1 != msg2

    def test_response_message_inequality_different_body(self):
        msg1 = ResponseMessage(text="Error", body="Details A")
        msg2 = ResponseMessage(text="Error", body="Details B")
        assert msg1 != msg2

    def test_response_message_inequality_one_has_body_other_none(self):
        msg1 = ResponseMessage(text="Error", body="Details")
        msg2 = ResponseMessage(text="Error")
        assert msg1 != msg2

    def test_response_message_inequality_both_none_body_should_equal(self):
        msg1 = ResponseMessage(text="Error", body=None)
        msg2 = ResponseMessage(text="Error", body=None)
        assert msg1 == msg2
