# Project Architecture

iOS Health Sync is a Swift 6 project for secure HealthKit data transfer.

## Repository Structure

```
ai-health-sync-ios-clawdbot/
├── iOS Health Sync App/              # Xcode project
│   ├── iOS Health Sync App/
│   │   ├── App/
│   │   │   ├── iOS_Health_Sync_AppApp.swift  # @main entry
│   │   │   └── AppState.swift                # @Observable state
│   │   ├── Core/
│   │   │   ├── Models/
│   │   │   │   ├── HealthDataType.swift      # Enum of health types
│   │   │   │   ├── PersistenceModels.swift   # SwiftData models
│   │   │   │   └── SchemaVersions.swift      # Migration schemas
│   │   │   ├── DTO/
│   │   │   │   └── HealthSampleDTO.swift     # Network transfer object
│   │   │   └── Utilities/
│   │   │       ├── DEREncoder.swift          # X.509 certificate builder
│   │   │       └── Loggers.swift             # os.Logger instances
│   │   ├── Features/
│   │   │   ├── ContentView.swift             # Main UI
│   │   │   ├── QRCodeView.swift              # Pairing QR display
│   │   │   ├── PrivacyPolicyView.swift       # Privacy disclosure
│   │   │   └── AboutView.swift               # App info
│   │   └── Services/
│   │       ├── HealthKit/
│   │       │   ├── HealthKitService.swift    # HealthKit queries
│   │       │   ├── HealthStoreProtocol.swift # Testability protocol
│   │       │   └── HealthSampleMapper.swift  # HKSample -> DTO
│   │       ├── Security/
│   │       │   ├── CertificateService.swift  # TLS cert generation
│   │       │   ├── KeychainStore.swift       # Secure storage
│   │       │   └── PairingService.swift      # Device pairing
│   │       ├── Network/
│   │       │   ├── NetworkServer.swift       # HTTPS server
│   │       │   └── HTTPTypes.swift           # Request/response types
│   │       └── Audit/
│   │           └── AuditService.swift        # Access logging
│   └── iOS Health Sync AppTests/
│       ├── DEREncoderTests.swift
│       ├── NetworkServerTests.swift
│       └── HealthKitServiceTests.swift
├── macOS/
│   └── HealthSyncCLI/                        # Swift Package
│       ├── Package.swift
│       ├── Sources/HealthSyncCLI/
│       │   └── main.swift                    # CLI implementation
│       └── Tests/HealthSyncCLITests/
│           └── HealthSyncCLITests.swift
└── DOCS/
    ├── GUIDELINES-REF/                       # Shared guidelines (symlink)
    └── CLAWDBOT-SKILL-PLAN.md
```

## Key Components

### iOS App

**AppState** (@Observable):
- Manages sharing state, paired clients, server lifecycle
- Holds references to services

**HealthKitService**:
- Requests HealthKit authorization
- Queries samples by type and date range
- Maps to DTO format

**NetworkServer**:
- NWListener with TLS configuration
- Routes: `/api/v1/pair`, `/api/v1/status`, `/api/v1/health/types`, `/api/v1/health/data`
- Uses SecIdentity for TLS

**CertificateService**:
- Generates self-signed ECDSA P-256 certificate
- Stores in Keychain
- Prefers Secure Enclave when available

**AuditService** (actor):
- Records all health data access
- SwiftData persistence
- 90-day retention with auto-purge

### macOS CLI

Single-file implementation with:
- Bonjour discovery (NWBrowser)
- QR code scanning (Vision framework)
- Certificate pinning (URLSessionDelegate)
- Keychain token storage

## Data Flow

### Pairing

```
iOS App                          macOS CLI
   │                                │
   ├─ Generate TLS cert ───────────►│
   ├─ Generate pairing code         │
   ├─ Display QR code               │
   │                                │
   │◄─────── User copies QR ────────┤
   │                                ├─ Parse QR payload
   │                                ├─ Validate host (local)
   │                                ├─ Validate expiration
   │◄──────── POST /pair ───────────┤
   ├─ Verify code                   │
   ├─ Generate token                │
   ├─ Record audit event            │
   ├──────── Return token ─────────►│
   │                                ├─ Store fingerprint
   │                                ├─ Store token (Keychain)
```

### Health Data Fetch

```
iOS App                          macOS CLI
   │                                │
   │◄───── POST /health/data ───────┤
   ├─ Verify Bearer token           │
   ├─ Query HealthKit               │
   ├─ Map to DTOs                   │
   ├─ Record audit event            │
   ├─────── Return samples ────────►│
   │                                ├─ Format as CSV/JSON
   │                                ├─ Output to stdout
```

## Key Patterns

### Protocol-Oriented Testing

```swift
protocol HealthStoreProtocol {
    func requestAuthorization(...) async throws
    func samples(for type: HealthDataType, ...) async throws -> [HealthSampleDTO]
}

// Production
class HealthKitService: HealthStoreProtocol { ... }

// Tests
class MockHealthStore: HealthStoreProtocol { ... }
```

### Actor for Audit

```swift
actor AuditService {
    // Thread-safe, no data races
    func record(eventType: String, details: [String: String]) async { ... }
}
```

### SwiftData Models

```swift
@Model
final class AuditEventRecord {
    var id: UUID
    var eventType: String
    var detailJSON: String
    var timestamp: Date

    // No deletedAt - audit records are immutable until retention expires
}
```

## Build & Test

```bash
# iOS App
xcodebuild -project "iOS Health Sync App/iOS Health Sync App.xcodeproj" \
  -scheme "iOS Health Sync App" build

# iOS Tests
xcodebuild test -scheme "iOS Health Sync App" \
  -destination 'platform=iOS Simulator,name=iPhone 16'

# macOS CLI
cd macOS/HealthSyncCLI
swift build
swift test  # 39 tests
```
