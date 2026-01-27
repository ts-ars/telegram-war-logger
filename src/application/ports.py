from __future__ import annotations

from typing import Protocol

from domain.model import ProcessedKey


class WarSheetPort(Protocol):
    def read_header_map(self) -> dict[str, int]:
        ...

    def validate_required_headers(self, header_map: dict[str, int]) -> None:
        ...

    def append_row(self, values_by_header: dict[str, str], header_map: dict[str, int]) -> None:
        ...

    def read_rows_for_cache(self) -> list[dict[str, str]]:
        ...


class ProcessedStorePort(Protocol):
    def load_processed(self) -> set[ProcessedKey]:
        ...

    def append_processed(self, key: ProcessedKey) -> None:
        ...


class SekcjaResolverPort(Protocol):
    def resolve(self, chat_id: int, thread_id: int | None) -> str | None:
        ...
