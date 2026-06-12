import gzip
import shutil
import os


def compress_file(input_path, output_path):
    """Compress a file using gzip. Streams in chunks so large files
    don't get loaded fully into memory."""
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def decompress_file(input_path, output_path):
    """Reverse compress_file: gzip -> original bytes."""
    with gzip.open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def compression_ratio(original_path, compressed_path):
    """Percentage size reduction. Positive = smaller after compression."""
    orig = os.path.getsize(original_path)
    comp = os.path.getsize(compressed_path)
    if orig == 0:
        return 0.0
    return round((1 - comp / orig) * 100, 2)


if __name__ == "__main__":
    path = input("Enter file path to compress: ").strip()
    out = path + ".gz"
    compress_file(path, out)
    ratio = compression_ratio(path, out)
    print(f"Done! Saved as {out} | Reduced by {ratio}%")
