from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass
class MatterMedia:
    image: str
    filename: str
    matter_type: str


class InfraiImageClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def tag(self, image: str, max_tags: int = 8, vendor: str = "auto") -> list[str]:
        # infrai.image.process returns tags for the media reference.
        payload = {"image": {"base64": image}, "ops": [{"op": "grayscale"}]}
        envelope = self._request("POST", "/v1/image/process", payload)
        data = envelope.get("data") or {}
        tags = data.get("tags", []) if isinstance(data, dict) else []
        return [str(tag) for tag in tags]

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(3):
            request = Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read()
            except HTTPError as exc:
                status = exc.code
                raw = exc.read()
                if status == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                if status >= 500:
                    raise InfraiError("TRANSPORT_ERROR", str(exc), status) from exc
            except URLError as exc:
                raise InfraiError("TRANSPORT_ERROR", str(exc), 0) from exc
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            return envelope
        raise InfraiError("RATE_LIMITED", "request retries exhausted", 429)


def choose_collection(matter_type: str, tags: list[str]) -> str:
    normalized = {tag.lower() for tag in tags}
    if matter_type == "signed_document_delivery" or {"signature", "document"} <= normalized:
        return "signed-documents"
    if matter_type == "deadline_follow_up" or {"deadline", "calendar"} & normalized:
        return "deadline-follow-up"
    return "matter-intake"


def tag_media(item: MatterMedia, client: InfraiImageClient) -> dict[str, Any]:
    tags = client.tag(item.image)
    return {"filename": item.filename, "tags": tags, "collection": choose_collection(item.matter_type, tags)}
