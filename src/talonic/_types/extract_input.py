"""Keyword-only discriminated union of the four file-source kinds accepted by `extract()`.

This mirrors `@talonic/node`'s ExtractParams contract: exactly one of
{file_data + filename, file_path, file_url, document_id}, validated at SDK
layer before any HTTP call.
"""

from __future__ import annotations

import os
from typing import Any

from talonic.errors import TalonicValidationError


class ExtractInputError(TalonicValidationError):
    """Raised when the file-source union is malformed (zero, two, or invalid combo)."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status=0, code="EXTRACT_INPUT_INVALID")


def normalize_extract_input(
    *,
    file_data: bytes | None = None,
    filename: str | None = None,
    file_path: str | os.PathLike[str] | None = None,
    file_url: str | None = None,
    document_id: str | None = None,
) -> dict[str, Any]:
    """Validate that exactly one file-source is provided and return a canonicalised dict.

    Returns:
        A dict containing the validated source fields ready to be embedded
        in the request body or multipart form.

    Raises:
        ExtractInputError: when zero, more than one source, or a partial pair
            (e.g. file_data without filename) is supplied.
    """
    sources_present = sum(
        bool(x)
        for x in (
            file_data is not None,
            file_path is not None,
            file_url is not None,
            document_id is not None,
        )
    )
    if sources_present != 1:
        raise ExtractInputError(
            "extract() requires exactly one of file_data, file_path, file_url, or document_id."
        )

    if file_data is not None and not filename:
        raise ExtractInputError("file_data requires a filename for MIME detection.")
    if filename and file_data is None:
        raise ExtractInputError("filename is only valid alongside file_data.")

    if file_data is not None:
        return {"file_data": file_data, "filename": filename}
    if file_path is not None:
        return {"file_path": os.fspath(file_path)}
    if file_url is not None:
        return {"file_url": file_url}
    return {"document_id": document_id}
