# Security Policy

## Supported Versions

The CROSSFIRE registry operates as a continuous, rolling database of canonical hashes. Only the `main` branch is actively supported and updated.

| Branch | Supported          |
| -------| ------------------ |
| `main` | :white_check_mark: |
| others | :x:                |

## Threat Model & Security Posture

This repository (`crossfire-registry`) distributes canonical hashes for high-value software targets. Because it is hosted on GitHub, it inherently leverages GitHub's Fastly CDN, placing it outside the reach of typical localized ISP interception (which would require blocking all of `raw.githubusercontent.com`, causing massive collateral damage).

**Key Defenses:**
1. **Air-Gapped Private Key (ED25519):** Every entry in `registry.json` is cryptographically signed. The private key never touches the internet, CI/CD, or GitHub.
2. **Continuous Integrity Audit (CIA):** GitHub Actions automatically and continuously verify the signatures against the `registry.pub.pem` public key. If an adversary compromises this GitHub account and tampers with the JSON payload, the workflow will fail immediately.
3. **No-Trust Fallback:** The CROSSFIRE daemon running on user machines always validates the ED25519 signature before trusting any hash from this repository. If GitHub serves a tampered file, the user client rejects it.

## Reporting a Vulnerability

We take the security of this infrastructure extremely seriously, as it protects at-risk individuals (journalists, activists, NGOs) against state-sponsored DPI interception.

If you discover a vulnerability (e.g., a bypass in the signature scheme, or a compromise of the offline key), please DO NOT open a public issue.

Instead, report it via encrypted channels:
- Email (PGP key to be provided upon initial contact)
- Signal (contact core maintainers directly)

We will acknowledge receipt within 24 hours.

## Key Rotation

If the root private key is ever compromised, a revocation notice will be pushed here, and a new root key will be issued with an updated `registry.pub.pem`. All CROSSFIRE clients will require an update to the new trust anchor.
