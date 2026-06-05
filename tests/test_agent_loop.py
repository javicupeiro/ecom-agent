from ecom_agent.domain.types import Response, TextBlock, ToolUseBlock
from ecom_agent.orchestrator import Conversation
from ecom_agent.providers.mock import MockProvider


def test_inner_loop_runs_a_tool_then_replies() -> None:
    script = [
        Response(
            blocks=[ToolUseBlock(id="t1", name="search_products", input={"query": "models"})],
            stop_reason="tool_use",
        ),
        Response(blocks=[TextBlock(text="We have Essential and ProConnect.")]),
    ]
    conv = Conversation(MockProvider(script=script))
    result = conv.send("What models do you sell?")

    assert result.trace.tools_used == ["search_products"]
    assert "ProConnect" in result.reply