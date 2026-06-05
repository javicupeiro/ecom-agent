"""Permission gateway for side-effecting tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable


class PermissionPolicy(ABC):
    @abstractmethod
    def allows(self, tool_name: str, tool_input: dict) -> bool: ...


class AlwaysAllow(PermissionPolicy):
    def allows(self, tool_name: str, tool_input: dict) -> bool:
        return True


class AllowList(PermissionPolicy):
    def __init__(self, names) -> None:
        self.names = set(names)

    def allows(self, tool_name: str, tool_input: dict) -> bool:
        return tool_name in self.names


class AlwaysAsk(PermissionPolicy):
    """Delegates the decision to a callback (e.g. a confirm dialog in the UI)."""

    def __init__(self, confirm: Callable[[str, dict], bool]) -> None:
        self.confirm = confirm

    def allows(self, tool_name: str, tool_input: dict) -> bool:
        return bool(self.confirm(tool_name, tool_input))