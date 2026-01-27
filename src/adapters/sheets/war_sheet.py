from __future__ import annotations

import logging
from typing import Any

import google.auth
from googleapiclient.discovery import build

from domain.model import REQUIRED_HEADERS

logger = logging.getLogger(__name__)


class WarSheetAdapter:
    def __init__(self, sheet_id: str, sheet_name: str) -> None:
        self._sheet_id = sheet_id
        self._sheet_name = sheet_name
        self._service = _build_service()

    def read_header_map(self) -> dict[str, int]:
        values = self._read_range(f"{self._sheet_name}!1:1")
        if not values:
            raise RuntimeError("Sheet header row is empty")
        header_row = values[0]
        header_map: dict[str, int] = {}
        for index, name in enumerate(header_row):
            header_map[name] = index
        return header_map

    def validate_required_headers(self, header_map: dict[str, int]) -> None:
        missing = [name for name in REQUIRED_HEADERS if name not in header_map]
        if missing:
            raise RuntimeError(f"Missing required headers: {missing}")
        logger.info("header validated", extra={"header_count": len(header_map)})

    def append_row(self, values_by_header: dict[str, str], header_map: dict[str, int]) -> None:
        row = [""] * len(header_map)
        for header, value in values_by_header.items():
            index = header_map.get(header)
            if index is None:
                raise RuntimeError(f"Header not found in sheet: {header}")
            row[index] = value
        body = {"values": [row]}
        self._service.spreadsheets().values().append(
            spreadsheetId=self._sheet_id,
            range=self._sheet_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    def read_rows_for_cache(self) -> list[dict[str, str]]:
        values = self._read_range(self._sheet_name)
        if not values:
            return []
        headers = values[0]
        rows = []
        for row_values in values[1:]:
            row_dict: dict[str, str] = {}
            for index, header in enumerate(headers):
                row_dict[header] = row_values[index] if index < len(row_values) else ""
            rows.append(row_dict)
        return rows

    def _read_range(self, range_name: str) -> list[list[str]]:
        result = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self._sheet_id, range=range_name)
            .execute()
        )
        return result.get("values", [])


def _build_service():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)
