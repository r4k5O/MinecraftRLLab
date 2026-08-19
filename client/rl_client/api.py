from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, token: str = "", timeout: float = 15.0):
        self.host = host.strip() or "127.0.0.1"
        self.port = int(port)
        self.token = token.strip()
        self.timeout = float(timeout)

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/api/v1"

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health", auth=False)

    def info(self) -> dict[str, Any]:
        return self._request("GET", "/info")

    def bind(self, player: str) -> dict[str, Any]:
        return self._request("POST", "/bind", {"player": player})

    def reset(self, goal: str, profile: str = "SURVIVAL", episode: int = 0) -> dict[str, Any]:
        return self._request("POST", "/reset", {"goal": goal, "profile": profile, "episode": int(episode)})

    def state(self) -> dict[str, Any]:
        return self._request("GET", "/state")

    def step(self, action: str) -> dict[str, Any]:
        return self._request("POST", "/step", {"action": action})

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None, auth: bool = True) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if auth:
            headers["X-RL-Token"] = self.token
        request = Request(self.base_url + path, data=body, method=method, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw) if raw else {}
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
                message = data.get("error", raw)
            except json.JSONDecodeError:
                message = raw or str(exc)
            raise ApiError(f"HTTP {exc.code}: {message}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ApiError(f"Could not reach MinecraftRLLab at {self.base_url}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ApiError("Server returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise ApiError("Server returned a non-object JSON response")
        return data
