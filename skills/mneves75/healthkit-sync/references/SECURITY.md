# Security Architecture

iOS Health Sync implements defense-in-depth security for health data transfer.

## Threat Model

- **Network eavesdropping** - Mitigated by TLS encryption
- **MITM attacks** - Mitigated by certificate pinning (TOFU)
- **Token theft** - Mitigated by Keychain storage
- **SSRF attacks** - Mitigated by local network host validation
- **Replay attacks** - Mitigated by time-limited pairing codes

## TLS Certificate Management

### iOS Server (CertificateService.swift)

Self-signed ECDSA P-256 certificate generated on first run:

```swift
struct TLSIdentity {
    let identity: SecIdentity
    let certificateData: Data
    let fingerprint: String  // SHA256 hex
}

// Keychain storage
private static let keyTag = "org.mvneves.healthsync.tlskey"
private static let certLabel = "HealthSync Local TLS"
```

**Key generation priority:**
1. Secure Enclave (if available) - hardware-backed
2. Software keychain - `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`

**Certificate fields:**
- Subject: `CN=HealthSync Local`
- Validity: 365 days from generation
- Algorithm: ECDSA with SHA256

### macOS Client (Certificate Pinning)

SHA256 fingerprint pinning via `URLSessionDelegate`:

```swift
final class PinnedSessionDelegate: NSObject, URLSessionDelegate {
    private let expectedFingerprint: String

    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard let trust = challenge.protectionSpace.serverTrust,
              let certificate = (SecTrustCopyCertificateChain(trust) as? [SecCertificate])?.first else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        let data = SecCertificateCopyData(certificate) as Data
        let fingerprint = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()

        if fingerprint == expectedFingerprint {
            completionHandler(.useCredential, URLCredential(trust: trust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

## Token Storage

### iOS Server (SwiftData)

Tokens are **hashed** (SHA256) and stored in SwiftData, NOT Keychain:

```swift
// PairedDevice model (SwiftData)
@Model
final class PairedDevice {
    var tokenHash: String      // SHA256 of token (never plaintext)
    var expiresAt: Date
    var isActive: Bool
    var lastSeenAt: Date?
}

// Token hashing in PairingService
private static func hashToken(_ token: String) -> String {
    let digest = SHA256.hash(data: Data(token.utf8))
    return digest.map { String(format: "%02x", $0) }.joined()
}
```

**Note:** Keychain is used for TLS private key storage (CertificateService), not tokens.

### macOS CLI (Keychain)

```swift
enum KeychainStore {
    private static let service = "org.mvneves.healthsync.cli"

    static func saveToken(_ token: String, for host: String) throws {
        let account = "token-\(host)"
        let addQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: tokenData,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlocked
        ]
        // ...
    }
}
```

## Local Network Validation

Prevents SSRF by restricting hosts to local network:

```swift
func isLocalNetworkHost(_ host: String) -> Bool {
    // Allow: localhost, *.local domains
    // Allow: 192.168.*, 10.*, 172.16-31.*
    // Allow: ::1, fe80::*
    // Reject: all others
}
```

## Pairing Security

### QR Code Payload

```json
{
  "version": "1",
  "host": "192.168.1.42",
  "port": 8443,
  "code": "random-one-time-code",
  "expiresAt": "2026-01-07T12:05:00Z",
  "certificateFingerprint": "sha256-hex"
}
```

**Validations performed:**
1. Version check (forward compatibility)
2. Host must be local network
3. Code must not be expired (5 min TTL)
4. Fingerprint stored for future connections

### Token Exchange

```
POST /api/v1/pair
{
  "code": "one-time-code",
  "clientName": "MacBook Pro"
}

Response:
{
  "token": "bearer-token",
  "expiresAt": "2026-01-14T00:00:00Z"
}
```

## Audit Logging

All health data access is logged via AuditService:

```swift
actor AuditService {
    private static let retentionDays: Int = 90

    func record(eventType: String, details: [String: String]) async {
        // Persisted to SwiftData
        // Auto-purged after 90 days
    }
}
```

**Logged events:**
- `health.read` - Data fetch requests
- `health.types` - Type enumeration
- `pairing.request` - New pairing attempts
- `pairing.success` - Successful pairings

**Privacy rules:**
- No PII in logs
- Request IDs for correlation
- os.Logger with privacy annotations
