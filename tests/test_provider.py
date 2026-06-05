from ecom_agent.domain.types import Message, Response, TextBlock
from ecom_agent.providers.mock import MockProvider


def test_mock_provider_returns_scripted_text() -> None:
    provider = MockProvider(script=[Response(blocks=[TextBlock(text="hi there")])])
    assert provider.send([Message.user("hello")], tools=[]).text() == "hi there"


def test_set_model_changes_model() -> None:
    provider = MockProvider()
    provider.set_model("mock-2")
    assert provider.model == "mock-2"