# Encrypted File Sharing

A command-line tool for end-to-end encrypted file transfer with compression and integrity verification. A file is hashed, compressed, encrypted with AES-256-GCM, and uploaded to a relay server as an opaque blob. The decryption key never touches the server — it travels separately, embedded in the share link's URL fragment. The recipient downloads the blob, decrypts it, decompresses it, and verifies the result against the original hash.

Built in Python as a portfolio project to demonstrate applied cryptography, authenticated encryption, and threat-model reasoning.

## How it works

```
SENDER                                        RECEIVER
------                                        --------
file                                          share link
  |                                             |
  | SHA-256 hash (fingerprint original)         | parse file_id, key, hash
  | gzip compress (skipped if already           |
  |   a compressed format)                      | download encrypted blob
  | AES-256-GCM encrypt (fresh random key)      | AES-256-GCM decrypt
  | upload blob to server  ------> [ server ] -->   (fails if tampered)
  | build link: .../<id>#<key>:<hash>           | bounded gzip decompress
  v                                             | verify SHA-256 == original
share link (key lives here, not on server)     v
                                              recovered file
```

The server only ever stores an encrypted blob. It cannot read file contents because it never sees the key.

## Project structure

The project is built as six standalone mini-modules. Each runs and tests independently; the final module wires them into one pipeline.

| Module | Responsibility |
|--------|----------------|
| `mini1_compression` | gzip compress / decompress, skip already-compressed formats |
| `mini2_hashing` | SHA-256 generation and verification |
| `mini3_keygen` | AES-256 key generation, PBKDF2 password derivation, key storage |
| `mini4_encryption` | AES-256-GCM authenticated encryption |
| `mini5_transfer` | Flask upload/download server, client, share-link builder |
| `mini6_final` | CLI that chains all modules + bounded-decompress safety guard |

## Setup

Requires Python 3.12+ (developed on 3.14).

```bash
# clone, then:
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

The server and the client run in separate terminals.

**Terminal 1 — start the relay server (leave running):**

```bash
cd mini5_transfer
python server.py
```

**Terminal 2 — send a file:**

```bash
python mini6_final/main.py send /path/to/file.pdf
```

This prints a share link containing the file id, key, and hash.

**Receive a file:**

```bash
python mini6_final/main.py receive "PASTE_LINK_HERE" --output recovered.pdf
```

You'll see each pipeline stage run, ending with an integrity check. If it prints `SUCCESS: File is intact`, the recovered file is byte-for-byte identical to the original — for any format (text, PDF, ZIP, images, etc.).

### Optional: convenience commands

You can register short commands so you don't type the full path each time. Create executables in a directory on your `PATH` (e.g. `~/bin`):

```bash
mkdir -p ~/bin
# add ~/bin to PATH in your shell config if it isn't already:
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc

cat > ~/bin/share << 'EOF'
#!/bin/zsh
exec "$HOME/path/to/encrypted_file_share/venv/bin/python" \
     "$HOME/path/to/encrypted_file_share/mini6_final/main.py" "$@"
EOF
chmod +x ~/bin/share
```

Then `share send file.pdf` works from anywhere.

### Optional: remote transfer between networks

By default the server binds to `localhost` only — it is not reachable from other machines, which is the safe default. To transfer between two different networks, you can expose the local server through a tunneling service (e.g. ngrok) and point the client at it with an environment variable:

```bash
export SHARE_SERVER="https://your-tunnel-url"
```

**Only do this for short-lived, trusted transfers, and shut the tunnel down afterward.** See Security limitations below — exposing the server publicly changes the threat model significantly.

## Design decisions

**Why hash before compressing and encrypting.** The hash must fingerprint the *original* bytes. Compression and encryption both transform the data, and encryption output differs every run (fresh nonce), so hashing afterward would be meaningless. The receiver re-hashes only after fully recovering the original, giving an end-to-end integrity check independent of the crypto.

**Why compress before encrypting, not after.** Encrypted data is indistinguishable from random noise and does not compress. Compression must happen on the plaintext. (This ordering has a known side-channel tradeoff — see limitations.)

**Why AES-256-GCM over AES-CBC.** GCM is authenticated encryption (AEAD): it provides confidentiality *and* integrity in one primitive. Any tampering with the ciphertext causes decryption to fail with an `InvalidTag` error rather than returning corrupted plaintext. CBC provides no integrity on its own and is the classic target of padding-oracle attacks. With GCM, a single flipped bit is detected before any plaintext is produced.

**Why a fresh key per file.** Each file is encrypted with a brand-new random 256-bit key and a fresh random 96-bit nonce. This sidesteps GCM's nonce-reuse failure mode entirely: reusing a `(key, nonce)` pair under GCM is catastrophic — it can leak the authentication secret and allow forgery. One key per file means nonce collisions are not a practical concern.

**Why the key travels in the link fragment.** Browsers never transmit the URL fragment (everything after `#`) to the server, so a server compromise never exposes the key. The server holds only ciphertext. The tradeoff: the link itself becomes the secret (see limitations).

## Security limitations

This is a learning project. It demonstrates correct use of authenticated encryption, but it is **not** a hardened production system. The following are known, deliberate boundaries:

- **The link is the secret.** The decryption key lives in the share link. Anyone who sees the link — via clipboard history, chat logs, a screenshare, or an insecure channel — can decrypt the file. Channel separation only helps if the link and the blob travel by different paths. Sending both in the same email defeats it.

- **No sender authentication.** SHA-256 proves a file wasn't *corrupted*, but it is unkeyed — anyone can compute it. The design provides no proof of *who* sent a file. Authenticating origin would require an HMAC or a digital signature (e.g. RSA/Ed25519), which this project does not implement.

- **The server is unauthenticated.** Anyone who can reach the server's port can upload or download blobs. File contents stay protected by encryption, but an attacker on the same network (or the public internet, if tunneled) could spam uploads to exhaust disk — a denial-of-service. A 100 MB upload cap and a 1-hour auto-delete reaper blunt this but do not eliminate it. Production use would need auth tokens, HTTPS, and rate limiting.

- **The compress flag is unauthenticated.** A one-character marker in the link tells the receiver whether to decompress. It lives outside the encrypted, authenticated payload, so an attacker who can rewrite the link could flip it and break that one transfer. This is a denial-of-service only — it cannot break confidentiality. The clean fix is to move the flag inside the encrypted payload so GCM authenticates it.

- **Encryption loads the whole file into memory.** The `cryptography` library's one-shot AES-GCM API needs the full plaintext to compute its tag, so very large files are constrained by available RAM. A streaming/chunked AEAD construction would remove this ceiling.

- **PBKDF2, not Argon2.** The password-derivation path uses PBKDF2-HMAC-SHA256 (480,000 iterations). This is standard and acceptable, but PBKDF2 is GPU-friendly; a memory-hard KDF like Argon2id or scrypt resists offline cracking far better. Note that the main pipeline uses random per-file keys, so password derivation only applies if a password-protected mode is added.

## Running the tests

```bash
python -m pytest -v
```

Each module has its own test file; key coverage includes the encrypt/decrypt round-trip, tamper detection (modifying the ciphertext must raise `InvalidTag`), wrong-key rejection, path-traversal rejection on the server, and the bounded-decompress guard refusing a decompression bomb.

## License

MIT (or your choice).
