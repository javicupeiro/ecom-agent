import json

from ecom_agent.domain.types import Response, TextBlock
from ecom_agent.memory.store import JSONFileStore
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


def test_turn_extraction_accumulates_across_messages() -> None:
    script = [
        Response(blocks=[TextBlock(text="Can you tell me what happened?")]),
        Response(
            blocks=[
                TextBlock(
                    text=(
                        '{"order_number":"ORD-100200","problem_category":null,'
                        '"problem_description":null,"frustration":0.2,'
                        '"urgency_level":null}'
                    )
                )
            ]
        ),
        Response(blocks=[TextBlock(text="Understood. I am checking the delivery issue.")]),
        Response(
            blocks=[
                TextBlock(
                    text=(
                        '{"order_number":null,"problem_category":"shipping",'
                        '"problem_description":"Order not delivered.",'
                        '"frustration":0.7,"urgency_level":"high"}'
                    )
                )
            ]
        ),
    ]
    conv = Conversation(MockProvider(script=script))

    first = conv.send("My order number is ORD-100200.")
    second = conv.send("It still has not arrived and I need it today.")

    assert first.trace.extraction.order_number == "ORD-100200"
    assert first.trace.extraction.problem_category is None

    assert second.reply == "Understood. I am checking the delivery issue."
    assert second.trace.extraction.order_number == "ORD-100200"
    assert second.trace.extraction.problem_category == "shipping"
    assert second.trace.extraction.problem_description == "Order not delivered."
    assert second.trace.extraction.frustration == 0.7
    assert second.trace.extraction.urgency_level == "high"


def test_turn_extraction_persists_structured_case_snapshot(tmp_path) -> None:
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
    store = JSONFileStore(tmp_path)
    conv = Conversation(MockProvider(script=script), store=store, session_id="case-1")

    result = conv.send("My ORD-100200 still has not arrived and I need it today.")

    log_data = json.loads((tmp_path / "case-1.json").read_text(encoding="utf-8"))
    case_data = json.loads((tmp_path / "cases" / "case-1.json").read_text(encoding="utf-8"))

    assert result.trace.extraction.order_number == "ORD-100200"
    assert [entry["role"] for entry in log_data] == ["user", "assistant"]
    assert case_data["session_id"] == "case-1"
    assert case_data["record"] == {
        "order_number": "ORD-100200",
        "problem_category": "shipping",
        "problem_description": "Order not delivered.",
        "frustration": 0.8,
        "urgency_level": "high",
    }
