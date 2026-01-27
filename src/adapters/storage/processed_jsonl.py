from __future__ import annotations

import json
import logging
from pathlib import Path

from domain.model import ProcessedKey

logger = logging.getLogger(__name__)


class ProcessedJsonlStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)

    def load_processed(self) -> set[ProcessedKey]:
        processed: set[ProcessedKey] = set()
        if not self._path.exists():
            return processed
        with self._path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    processed.add(
                        ProcessedKey(
                            chat_id=int(payload["chat_id"]),
                            message_id=int(payload["message_id"]),
                        )
                    )
                except Exception:
                    logger.warning("failed to parse processed entry", extra={"line": line})
        return processed

    def append_processed(self, key: ProcessedKey) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        record = {"chat_id": key.chat_id, "message_id": key.message_id}
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
