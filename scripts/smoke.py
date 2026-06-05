from ecom_agent.config import get_settings
from ecom_agent.domain.types import Message
from ecom_agent.providers.factory import build_provider

provider = build_provider(get_settings())
print(provider.send([Message.user("Say hello in one short sentence.")]).text)