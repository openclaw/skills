use chrono::{DateTime, Utc};
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use sha2::Sha256;
use subtle::ConstantTimeEq;

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventKind {
	Start,
	Stop,
	Message,
	Error,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Event {
	pub timestamp: DateTime<Utc>,
	pub pid: u32,
	pub uid: u32,
	pub event_kind: EventKind,
	pub session_id: String,
	pub prev_hash: Option<[u8; 32]>,
	pub hash: [u8; 32],
}

/// Chain anchor for detecting truncation.
/// Store this externally (e.g., remote server) to verify chain completeness.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ChainAnchor {
	/// Number of events in the chain
	pub length: usize,
	/// Hash of the last event
	pub last_hash: [u8; 32],
	/// HMAC of (length || last_hash) for tamper detection
	pub anchor_mac: [u8; 32],
}

impl ChainAnchor {
	/// Create an anchor for a chain of events.
	pub fn create(events: &[Event], key: &[u8]) -> Option<Self> {
		let length = events.len();
		let last_hash = events.last().map(|e| e.hash).unwrap_or([0u8; 32]);
		
		let anchor_mac = Self::compute_anchor_mac(key, length, &last_hash);
		
		Some(Self {
			length,
			last_hash,
			anchor_mac,
		})
	}
	
	/// Verify that the chain matches this anchor.
	/// Uses constant-time comparison to prevent timing attacks.
	pub fn verify(&self, events: &[Event], key: &[u8]) -> Result<(), AnchorError> {
		if events.len() != self.length {
			return Err(AnchorError::LengthMismatch {
				expected: self.length,
				found: events.len(),
			});
		}
		
		// Verify the anchor MAC (including empty chains)
		let expected_mac = Self::compute_anchor_mac(key, self.length, &self.last_hash);
		if !constant_time_eq(&expected_mac, &self.anchor_mac) {
			return Err(AnchorError::AnchorMacInvalid);
		}
		
		if events.is_empty() {
			return Ok(());
		}
		
		let last = events.last().unwrap();
		
		// Constant-time comparison for last hash
		if !constant_time_eq(&last.hash, &self.last_hash) {
			return Err(AnchorError::LastHashMismatch);
		}
		
		Ok(())
	}
	
	fn compute_anchor_mac(key: &[u8], length: usize, last_hash: &[u8; 32]) -> [u8; 32] {
		let length_u64 = u64::try_from(length)
			.expect("anchor length must fit in u64");
		let mut mac = HmacSha256::new_from_slice(key)
			.expect("HMAC can take key of any size");
		mac.update(b"clauditor:anchor:v1:");
		mac.update(&length_u64.to_le_bytes());
		mac.update(last_hash);
		
		let digest = mac.finalize().into_bytes();
		let mut out = [0u8; 32];
		out.copy_from_slice(&digest);
		out
	}
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AnchorError {
	LengthMismatch { expected: usize, found: usize },
	LastHashMismatch,
	AnchorMacInvalid,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum VerifyError {
	HashMismatch { index: usize },
	GenesisPrevHashMustBeNone { found: Option<[u8; 32]> },
	Gap {
		index: usize,
		expected_prev_hash: [u8; 32],
		found_prev_hash: Option<[u8; 32]>,
	},
}

/// Constant-time comparison for two byte arrays.
fn constant_time_eq(a: &[u8; 32], b: &[u8; 32]) -> bool {
	bool::from(a.ct_eq(b))
}

impl Event {
	pub fn new_genesis(
		key: &[u8],
		timestamp: DateTime<Utc>,
		pid: u32,
		uid: u32,
		event_kind: EventKind,
		session_id: impl Into<String>,
	) -> Self {
		let mut event = Self {
			timestamp,
			pid,
			uid,
			event_kind,
			session_id: session_id.into(),
			prev_hash: None,
			hash: [0u8; 32],
		};
		event.hash = event.compute_hash(key);
		event
	}

	pub fn new_next(
		key: &[u8],
		prev: &Event,
		timestamp: DateTime<Utc>,
		pid: u32,
		uid: u32,
		event_kind: EventKind,
		session_id: impl Into<String>,
	) -> Self {
		let mut event = Self {
			timestamp,
			pid,
			uid,
			event_kind,
			session_id: session_id.into(),
			prev_hash: Some(prev.hash),
			hash: [0u8; 32],
		};
		event.hash = event.compute_hash(key);
		event
	}

	pub fn compute_hash(&self, key: &[u8]) -> [u8; 32] {
		#[derive(Serialize)]
		struct HashInput<'a> {
			timestamp: &'a DateTime<Utc>,
			pid: u32,
			uid: u32,
			event_kind: &'a EventKind,
			session_id: &'a str,
			prev_hash: &'a Option<[u8; 32]>,
		}

		let input = HashInput {
			timestamp: &self.timestamp,
			pid: self.pid,
			uid: self.uid,
			event_kind: &self.event_kind,
			session_id: &self.session_id,
			prev_hash: &self.prev_hash,
		};

		// Note: serde_json serialization is deterministic for this struct
		let payload = serde_json::to_vec(&input).expect("hash input must serialize");

		let mut mac =
			HmacSha256::new_from_slice(key).expect("HMAC can take key of any size");
		mac.update(b"clauditor:event:v1:");
		mac.update(&payload);
		let digest = mac.finalize().into_bytes();

		let mut out = [0u8; 32];
		out.copy_from_slice(&digest);
		out
	}
}

pub fn verify_chain(events: &[Event], key: &[u8]) -> Result<(), VerifyError> {
	if events.is_empty() {
		return Ok(());
	}

	let first = &events[0];
	if first.prev_hash.is_some() {
		return Err(VerifyError::GenesisPrevHashMustBeNone {
			found: first.prev_hash,
		});
	}
	
	// Use constant-time comparison for hash verification
	if !constant_time_eq(&first.compute_hash(key), &first.hash) {
		return Err(VerifyError::HashMismatch { index: 0 });
	}

	for (idx, window) in events.windows(2).enumerate() {
		let prev = &window[0];
		let current = &window[1];
		let current_index = idx + 1;

		if current.prev_hash != Some(prev.hash) {
			return Err(VerifyError::Gap {
				index: current_index,
				expected_prev_hash: prev.hash,
				found_prev_hash: current.prev_hash,
			});
		}
		
		// Use constant-time comparison
		if !constant_time_eq(&current.compute_hash(key), &current.hash) {
			return Err(VerifyError::HashMismatch {
				index: current_index,
			});
		}
	}

	Ok(())
}

#[cfg(test)]
mod tests {
	use super::*;
	use chrono::TimeZone;

	const KEY: &[u8] = b"test-key";
	const WRONG_KEY: &[u8] = b"wrong-key";

	fn sample_chain() -> Vec<Event> {
		let session_id = "sess-1";
		let e0 = Event::new_genesis(
			KEY,
			Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
			123,
			1000,
			EventKind::Start,
			session_id,
		);
		let e1 = Event::new_next(
			KEY,
			&e0,
			Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 1).unwrap(),
			123,
			1000,
			EventKind::Message,
			session_id,
		);
		let e2 = Event::new_next(
			KEY,
			&e1,
			Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 2).unwrap(),
			123,
			1000,
			EventKind::Stop,
			session_id,
		);
		vec![e0, e1, e2]
	}

	#[test]
	fn serialization_round_trip() {
		let events = sample_chain();
		let json = serde_json::to_string(&events).unwrap();
		let decoded: Vec<Event> = serde_json::from_str(&json).unwrap();
		assert_eq!(events, decoded);
	}

	#[test]
	fn hash_chain_continuity() {
		let events = sample_chain();
		verify_chain(&events, KEY).unwrap();
	}

	#[test]
	fn tamper_detection() {
		let mut events = sample_chain();
		events[1].pid += 1;
		let err = verify_chain(&events, KEY).unwrap_err();
		assert_eq!(err, VerifyError::HashMismatch { index: 1 });
	}

	#[test]
	fn gap_detection() {
		let mut events = sample_chain();
		events.remove(1);
		let err = verify_chain(&events, KEY).unwrap_err();
		match err {
			VerifyError::Gap { index, .. } => assert_eq!(index, 1),
			other => panic!("expected Gap, got {other:?}"),
		}
	}

	// NEW TESTS for code review concerns
	
	#[test]
	fn wrong_key_fails_verification() {
		let events = sample_chain();
		let err = verify_chain(&events, WRONG_KEY).unwrap_err();
		assert_eq!(err, VerifyError::HashMismatch { index: 0 });
	}

	#[test]
	fn single_event_chain() {
		let e0 = Event::new_genesis(
			KEY,
			Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
			123,
			1000,
			EventKind::Start,
			"sess-1",
		);
		verify_chain(&[e0], KEY).unwrap();
	}

	#[test]
	fn empty_chain() {
		verify_chain(&[], KEY).unwrap();
	}

	#[test]
	fn genesis_with_prev_hash_fails() {
		let mut e0 = Event::new_genesis(
			KEY,
			Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
			123,
			1000,
			EventKind::Start,
			"sess-1",
		);
		// Force a prev_hash on genesis (should fail)
		e0.prev_hash = Some([1u8; 32]);
		let err = verify_chain(&[e0], KEY).unwrap_err();
		match err {
			VerifyError::GenesisPrevHashMustBeNone { .. } => {}
			other => panic!("expected GenesisPrevHashMustBeNone, got {other:?}"),
		}
	}

	#[test]
	fn tamper_prev_hash_detection() {
		let mut events = sample_chain();
		// Tamper with prev_hash of event 2
		events[2].prev_hash = Some([0u8; 32]);
		let err = verify_chain(&events, KEY).unwrap_err();
		match err {
			VerifyError::Gap { index, .. } => assert_eq!(index, 2),
			other => panic!("expected Gap, got {other:?}"),
		}
	}

	// Chain anchor tests
	
	#[test]
	fn anchor_creation_and_verification() {
		let events = sample_chain();
		let anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		assert_eq!(anchor.length, 3);
		assert_eq!(anchor.last_hash, events[2].hash);
		
		// Verification should pass
		anchor.verify(&events, KEY).unwrap();
	}

	#[test]
	fn anchor_detects_truncation() {
		let events = sample_chain();
		let anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		// Truncate the chain
		let truncated = &events[..2];
		let err = anchor.verify(truncated, KEY).unwrap_err();
		assert_eq!(err, AnchorError::LengthMismatch { expected: 3, found: 2 });
	}

	#[test]
	fn anchor_detects_tail_replacement() {
		let events = sample_chain();
		let anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		// Replace the last event with a different one
		let mut tampered = events.clone();
		tampered[2] = Event::new_next(
			KEY,
			&tampered[1],
			Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 3).unwrap(), // Different timestamp
			123,
			1000,
			EventKind::Stop,
			"sess-1",
		);
		
		let err = anchor.verify(&tampered, KEY).unwrap_err();
		assert_eq!(err, AnchorError::LastHashMismatch);
	}

	#[test]
	fn anchor_wrong_key_fails() {
		let events = sample_chain();
		let anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		// Try to verify with wrong key
		let err = anchor.verify(&events, WRONG_KEY).unwrap_err();
		assert_eq!(err, AnchorError::AnchorMacInvalid);
	}

	#[test]
	fn anchor_tamper_detection() {
		let events = sample_chain();
		let mut anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		// Tamper with the anchor's length
		anchor.length = 5;
		let err = anchor.verify(&events, KEY).unwrap_err();
		match err {
			AnchorError::LengthMismatch { .. } | AnchorError::AnchorMacInvalid => {}
			other => panic!("expected LengthMismatch or AnchorMacInvalid, got {other:?}"),
		}
	}

	#[test]
	fn anchor_empty_chain() {
		let events: Vec<Event> = Vec::new();
		let anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		assert_eq!(anchor.length, 0);
		assert_eq!(anchor.last_hash, [0u8; 32]);
		anchor.verify(&events, KEY).unwrap();
	}

	#[test]
	fn anchor_serialization_round_trip() {
		let events = sample_chain();
		let anchor = ChainAnchor::create(&events, KEY).unwrap();
		
		let json = serde_json::to_string(&anchor).unwrap();
		let decoded: ChainAnchor = serde_json::from_str(&json).unwrap();
		assert_eq!(anchor, decoded);
		
		// Decoded anchor should still verify
		decoded.verify(&events, KEY).unwrap();
	}
}
