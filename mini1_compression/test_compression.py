import os
import gzip
import pytest
from compressor import compress_file, decompress_file, compression_ratio
from compression_utils import get_file_size, should_compress


@pytest.fixture
def text_file(tmp_path):
    p = tmp_path / "sample.txt"
    # Repetitive content compresses well — guarantees a positive ratio.
    p.write_text("The quick brown fox. " * 500)
    return str(p)


def test_compress_creates_smaller_file(text_file):
    out = text_file + ".gz"
    compress_file(text_file, out)
    assert get_file_size(out) < get_file_size(text_file)


def test_roundtrip_matches_original(text_file):
    gz = text_file + ".gz"
    restored = text_file + ".restored"
    compress_file(text_file, gz)
    decompress_file(gz, restored)
    with open(text_file, 'rb') as a, open(restored, 'rb') as b:
        assert a.read() == b.read()


def test_compression_ratio_positive(text_file):
    out = text_file + ".gz"
    compress_file(text_file, out)
    assert compression_ratio(text_file, out) > 0


def test_should_compress_skips_jpg():
    assert should_compress("photo.jpg") is False
    assert should_compress("photo.JPG") is False  # case-insensitive


def test_should_compress_allows_txt():
    assert should_compress("notes.txt") is True


def test_large_file(tmp_path):
    big = tmp_path / "big.txt"
    big.write_text("data line\n" * 200_000)  # ~2MB
    out = str(big) + ".gz"
    compress_file(str(big), out)
    assert os.path.exists(out)
