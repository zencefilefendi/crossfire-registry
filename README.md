# CROSSFIRE Registry

**ED25519-signed download integrity hashes for CROSSFIRE — protection against DPI watering-hole injection.**

[![Registry entries](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fzencefilefendi%2Fcrossfire-registry%2Fmain%2Fregistry.json&query=%24.length&label=signed%20entries&color=2ea043)](registry.json)
[![License](https://img.shields.io/badge/license-research%20%2F%20defensive-blue)](LICENSE)
[![Citizen Lab](https://img.shields.io/badge/threat%20model-Citizen%20Lab%202018%2F2023-red)](https://citizenlab.ca/2018/03/bad-traffic-sandvines-packetlogic-devices/)

---

## What is this?

This repository distributes **cryptographically signed SHA-256/SHA-512 hashes** of official software installers.

[CROSSFIRE](https://github.com/zencefilefendi/CROSSFIRE) uses these hashes to detect when a nation-state actor or compromised ISP has replaced a software download in transit — an attack documented by Citizen Lab against **Türk Telekom** (Sandvine PacketLogic, 2018) and **Egyptian ISPs** (Intellexa Predator, 2023).

### The attack (Türk Telekom 2018)

```
User clicks "Download 7-Zip"
        │
        ▼
[ISP Backbone — Sandvine PacketLogic box]
        │
        ├── Inspects HTTP stream
        ├── Sees GET /a/7z1900-x64.exe
        └── Replaces response with FinFisher payload
                │
                ▼
        User receives trojanized binary
        (same filename, same size, HTTP 200)
```

### The defense (CROSSFIRE)

```
File received → hash locally
        │
        ▼
Fetch reference hash from this registry
via Tor circuit (ISP-blind path)
        │
        ▼
Compare → MISMATCH → INJECTION DETECTED
```

Because this registry is served via **GitHub's CDN (Fastly)**, it arrives through a completely different autonomous system than the user's ISP. A Sandvine box cannot simultaneously inject the download and forge the reference hash over a separate TLS-protected path.

---

## How entries are signed

Every entry in [`registry.json`](registry.json) is signed with an **offline ED25519 private key** (air-gapped, never touches a network). Clients embed only the public key.

```
[Air-gapped machine]
    python3 crossfire.py crawl --key registry.key.pem
    ↓
    Downloads official binary
    Computes SHA-256 + SHA-512 + BLAKE3
    Signs with ED25519
    ↓
registry.json (committed here)
    ↓
[Client machine via Tor]
    Verifies ED25519 signature
    Compares local hash
    CLEAN or INJECTED
```

Even if GitHub is legally compelled to serve modified content, the ED25519 signatures cannot be forged without the private key. Clients reject unsigned or incorrectly-signed entries.

---

## Covered software

Software targeted in documented ISP injection attacks is prioritized:

| Software | Publisher | First Targeted |
|----------|-----------|----------------|
| 7-Zip | Igor Pavlov | Türk Telekom 2018 |
| CCleaner | Piriform/Avast | Türk Telekom 2018 |
| Opera Browser | Opera Software | Türk Telekom 2018 |
| WinRAR | RARlab | Türk Telekom 2018 |
| Avast Free Antivirus | Avast | Türk Telekom 2018 |
| VLC Media Player | VideoLAN | General high-value |
| Signal Desktop | Signal Foundation | High-value target |
| Tor Browser | Tor Project | High-value target |

---

## Registry format

`registry.json` is a JSON array. Each entry:

```json
{
  "url_pattern": "https://www.7-zip.org/a/7z*.exe",
  "sha256": "bdd1a33de78618d16ee4ce148b849932c05d0015491c34887846d431d29f308e",
  "sha512": "2e8b746c51132f933cc526db661c2cb8...",
  "blake3": null,
  "size_bytes": 1637343,
  "signed_at": 1780082817,
  "signer_pubkey_b64": "...",
  "signature_b64": "..."
}
```

- `url_pattern` — glob pattern matched against the download URL
- `sha256` / `sha512` — hex-encoded digests of the official binary
- `signed_at` — Unix timestamp of when the crawler ran
- `signature_b64` — ED25519 signature over the canonical JSON payload

---

## Fetching this registry

### Direct HTTPS
```
https://raw.githubusercontent.com/zencefilefendi/crossfire-registry/main/registry.json
```

### Via Tor (recommended — ISP-blind)
```python
from channels.tor_channel import fetch_hash_via_tor
data = await fetch_hash_via_tor(
    "https://raw.githubusercontent.com/zencefilefendi/crossfire-registry/main/registry.json"
)
```

### CROSSFIRE verifier (automatic)
```python
from core.verifier import DownloadVerifier
verifier = DownloadVerifier()  # registry URL pre-configured
result = await verifier.verify(url=url, local_path=path)
# result.verdict → CLEAN / INJECTED / SUSPICIOUS
```

---

## Update cadence

Registry is updated when:
- A new version of covered software is released
- A new high-value target is added
- A crawl run detects changed official hashes

All updates are signed with the same offline key. Unsigned PRs to this repository are rejected.

---

## Threat model

| Scenario | Protected? |
|---------|-----------|
| ISP replaces download (HTTP) | ✓ Hash mismatch detected |
| ISP blocks this registry | ✓ Tor circuit + DoH fallback |
| GitHub legally compelled to serve modified JSON | ✓ ED25519 signature verification fails |
| Private key compromised | ✗ All entries must be re-signed |
| Both ISP path AND Tor compromised simultaneously | ✗ Out of scope |

---

## Related

- [CROSSFIRE](https://github.com/zencefilefendi/CROSSFIRE) — Main project (detection engine, browser extension, daemon)
- [Citizen Lab: Bad Traffic](https://citizenlab.ca/2018/03/bad-traffic-sandvines-packetlogic-devices/) — Türk Telekom / Sandvine (2018)
- [Citizen Lab: Predator in the Wires](https://citizenlab.ca/2023/09/predator-in-the-wires-ahmed-eltantawy/) — Egypt / Intellexa (2023)

---

## License

Research and defensive use only.
Hash values and signatures are facts; their publication is protected speech.
