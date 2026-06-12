import os
import pytest
from safe_decompress import bounded_decompress
from compressor import compress_file


def test_bounded_decompress_normal(tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("hello " * 1000)
    gz = str(tmp_path / "in.gz")
    out = str(tmp_path / "out.txt")
    compress_file(str(src), gz)
    bounded_decompress(gz, out, max_bytes=10 * 1024 * 1024)
    assert open(out).read() == "hello " * 1000


def test_bounded_decompress_rejects_bomb(tmp_path):
    # A small .gz that expands past a tiny cap should be refused.
    src = tmp_path / "big.txt"
    src.write_text("A" * 1_000_000)        # 1 MB of highly compressible data
    gz = str(tmp_path / "big.gz")
    out = str(tmp_path / "out.txt")
    compress_file(str(src), gz)
    with pytest.raises(ValueError, match="Decompressed size exceeded"):
        bounded_decompress(gz, out, max_bytes=1000)   # cap far below 1 MB
    assert not os.path.exists(out)          # partial output cleaned upx
