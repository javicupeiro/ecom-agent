from ecom_agent.domain.types import Response, TextBlock
from ecom_agent.orchestrator import Conversation
from ecom_agent.providers.mock import MockProvider


def test_turn_extraction_is_structured() -> None:
    script = [
        Response(blocks=[TextBlock(text="We are checking your order.")]),
        Response(
            blocks=[
                TextBlock(
                    text=(
                        '{"order_number":"ORD-100200","problem_category":"shipping",'
                        '"problem_description":"Order not delivered.",'
                        '"frustration":0.8,"urgency_level":"high"}'
                    )
                )
            ]
        ),
    ]
    conv = Conversation(MockProvider(script=script))

    result = conv.send("My ORD-100200 still has not arrived and I need it today.")

    assert result.reply == "We are checking your order."
    assert result.trace.extraction.order_number == "ORD-100200"
    assert result.trace.extraction.problem_category == "shipping"
    assert result.trace.extraction.problem_description == "Order not delivered."
    assert result.trace.extraction.frustration == 0.8
    assert result.trace.extraction.urgency_level == "high"
