import pytest
from hasher import generate_hash, verify_hash
from hashing_utils import format_hash


@pytest.fixture
def sample_file(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("integrity matters")
    return str(p)


def test_same_file_same_hash(sample_file):
    assert generate_hash(sample_file) == generate_hash(sample_file)


def test_different_files_different_hash(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("hello")
    b = tmp_path / "b.txt"; b.write_text("world")
    assert generate_hash(str(a)) != generate_hash(str(b))


def test_one_byte_change_changes_hash(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("aaaaaaaa")
    h1 = generate_hash(str(p))
    p.write_text("aaaaaaab")  # flip one byte
    h2 = generate_hash(str(p))
    assert h1 != h2


def test_verify_intact_returns_true(sample_file):
    h = generate_hash(sample_file)
    assert verify_hash(sample_file, h) is True


def test_verify_modified_returns_false(sample_file):
    assert verify_hash(sample_file, "0" * 64) is False


def test_known_sha256_value(tmp_path):
    # SHA-256 of the bytes "abc" is a well-known constant.
    p = tmp_path / "abc.txt"
    p.write_bytes(b"abc")
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert generate_hash(str(p)) == expected


def test_format_hash_shortens():
    full = "a3f9c2d1" + "0" * 50 + "b7e4abcd"
    assert format_hash(full) == "a3f9...abcd"
