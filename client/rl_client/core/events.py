from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import threading
from typing import Any, Callable

EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: str, handler: EventHandler) -> Callable[[], None]:
        with self._lock:
            self._handlers[event_type].append(handler)
        def unsubscribe() -> None:
            with self._lock:
                if handler in self._handlers.get(event_type, []):
                    self._handlers[event_type].remove(handler)
        return unsubscribe

    def publish(self, event_type: str, **payload: Any) -> None:
        event = {"type": event_type, **payload}
        with self._lock:
            handlers = list(self._handlers.get(event_type, ())) + list(self._handlers.get("*", ()))
        for handler in handlers:
            handler(event)
