"""ExtractInput: keyword-only discriminated union for file_data | file_path | file_url | document_id."""  # noqa: E501

import pytest

from talonic._types.extract_input import (
    ExtractInputError,
    normalize_extract_input,
)


def test_file_data_with_filename():
    out = normalize_extract_input(file_data=b"%PDF-1.4", filename="invoice.pdf")
    assert out == {"file_data": b"%PDF-1.4", "filename": "invoice.pdf"}


def test_file_path():
    out = normalize_extract_input(file_path="/tmp/invoice.pdf")
    assert out == {"file_path": "/tmp/invoice.pdf"}


def test_file_url():
    out = normalize_extract_input(file_url="https://example.com/i.pdf")
    assert out == {"file_url": "https://example.com/i.pdf"}


def test_document_id():
    out = normalize_extract_input(document_id="doc_abc")
    assert out == {"document_id": "doc_abc"}


def test_two_sources_raises():
    with pytest.raises(ExtractInputError, match="exactly one"):
        normalize_extract_input(file_path="/tmp/x", file_url="https://x")


def test_no_source_raises():
    with pytest.raises(ExtractInputError, match="exactly one"):
        normalize_extract_input()


def test_file_data_without_filename_raises():
    with pytest.raises(ExtractInputError, match="filename"):
        normalize_extract_input(file_data=b"%PDF-1.4")


def test_filename_without_file_data_raises():
    with pytest.raises(ExtractInputError, match="file_data"):
        normalize_extract_input(filename="invoice.pdf")
