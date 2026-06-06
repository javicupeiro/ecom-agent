from ecom_agent.compaction.strategy import safe_split_point
from ecom_agent.domain.types import Message, ToolResultBlock, ToolUseBlock


def test_safe_split_does_not_orphan_tool_result() -> None:
    msgs = [
        Message.user("hola"),
        Message(role="assistant", content=[ToolUseBlock(id="a", name="x", input={})]),
        Message(role="user", content=[ToolResultBlock(tool_use_id="a", content="ok")]),
        Message.assistant("done"),
    ]
    assert safe_split_point(msgs, 2) == 1