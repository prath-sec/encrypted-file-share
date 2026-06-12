import gzip

# Abort if a decompressed file would exceed this — defuses gzip bombs where a
# tiny .gz expands to gigabytes. Tune to your largest legitimate file.
MAX_DECOMPRESSED_BYTES = 500 * 1024 * 1024   # 500 MB
CHUNK = 8192


def bounded_decompress(input_path, output_path, max_bytes=MAX_DECOMPRESSED_BYTES):
    """Decompress a .gz file but stop and raise if output exceeds max_bytes."""
    written = 0
    with gzip.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        while chunk := f_in.read(CHUNK):
            written += len(chunk)
            if written > max_bytes:
                f_out.close()
                import os
                os.remove(output_path)
                raise ValueError(
                    f"Decompressed size exceeded {max_bytes} bytes — "
                    f"aborting (possible decompression bomb)."
                )
            f_out.write(chunk)
