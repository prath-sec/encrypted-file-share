import pytest
from link_generator import build_share_link, parse_share_link
from transfer_utils import validate_file_id, format_link

VALID_UUID = "12345678-1234-4234-8234-123456789abc"


def test_validate_real_uuid():
    assert validate_file_id(VALID_UUID) is True


def test_reject_path_traversal():
    assert validate_file_id("../../etc/passwd") is False
    assert validate_file_id("../../../secret") is False


def test_reject_garbage_ids():
    assert validate_file_id("not-a-uuid") is False
    assert validate_file_id("") is False


def test_build_and_parse_roundtrip():
    link = build_share_link("http://localhost:5000", VALID_UUID, "KEYB64", "HASHSTR")
    fid, key, h = parse_share_link(link)
    assert fid == VALID_UUID
    assert key == "KEYB64"
    assert h == "HASHSTR"


def test_link_contains_fragment():
    link = build_share_link("http://localhost:5000", VALID_UUID, "K", "H")
    assert "#" in link
    assert link.split("#", 1)[1] == "K:H"


def test_format_link_strips():
    assert format_link("  http://x/y#a:b  ") == "http://x/y#a:b"

