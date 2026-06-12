import os
import sys

ROOT = os.path.dirname(__file__)
# Put the project root and every mini package dir on sys.path so tests can
# import both their own modules (encryptor) and sibling packages (mini3_keygen).
sys.path.insert(0, ROOT)
for d in os.listdir(ROOT):
    full = os.path.join(ROOT, d)
    if os.path.isdir(full) and d.startswith("mini"):
        sys.path.insert(0, full)
