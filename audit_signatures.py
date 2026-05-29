import base64
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

def canonical_payload(entry: dict) -> bytes:
    doc = {
        "url_pattern": entry["url_pattern"],
        "sha256": entry["sha256"],
        "sha512": entry["sha512"],
        "blake3": entry["blake3"],
        "size_bytes": entry["size_bytes"],
        "signed_at": entry["signed_at"],
    }
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

def main():
    registry_file = Path("registry.json")
    key_file = Path("registry.pub.pem")

    if not registry_file.exists() or not key_file.exists():
        print("Missing registry.json or registry.pub.pem")
        sys.exit(1)

    pub_key_pem = key_file.read_bytes()
    trusted_pubkey = load_pem_public_key(pub_key_pem)

    if not isinstance(trusted_pubkey, Ed25519PublicKey):
        print("Expected ED25519 public key")
        sys.exit(1)

    entries = json.loads(registry_file.read_text())
    print(f"Auditing {len(entries)} entries...")

    failed = 0
    for entry in entries:
        sig = base64.b64decode(entry["signature_b64"])
        payload = canonical_payload(entry)
        try:
            trusted_pubkey.verify(sig, payload)
        except InvalidSignature:
            print(f"INVALID SIGNATURE for {entry['url_pattern']}")
            failed += 1

    if failed > 0:
        print(f"AUDIT FAILED: {failed} signatures are invalid!")
        sys.exit(1)

    print("AUDIT SUCCESS: All signatures are valid and cryptographically secure.")
    sys.exit(0)

if __name__ == "__main__":
    main()
