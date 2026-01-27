//! Command baseline tracking.
//! Flags "never seen before" commands as potential anomalies.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::SystemTime;

/// Statistics for a single command
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct CommandStats {
    /// Unix timestamp of first execution
    pub first_seen: u64,
    /// Unix timestamp of last execution
    pub last_seen: u64,
    /// Total execution count
    pub count: u64,
}

/// Alert generated when a new command is seen
#[derive(Debug, Clone)]
pub struct BaselineAlert {
    pub command: String,
    pub first_seen: u64,
    pub message: String,
}

/// Tracks command baseline - which commands are "normal" vs first-time.
#[derive(Debug, Default, Serialize, Deserialize)]
pub struct CommandBaseline {
    /// Command name → stats
    commands: HashMap<String, CommandStats>,
    /// Path to persist baseline (not serialized)
    #[serde(skip)]
    path: Option<PathBuf>,
    /// Whether baseline has been modified since last persist
    #[serde(skip)]
    dirty: bool,
}

impl CommandBaseline {
    /// Create new empty baseline (in-memory only)
    pub fn new() -> Self {
        Self {
            commands: HashMap::new(),
            path: None,
            dirty: false,
        }
    }

    /// Load baseline from file, or create new if file doesn't exist
    pub fn with_path(path: PathBuf) -> std::io::Result<Self> {
        if path.exists() {
            let content = std::fs::read_to_string(&path)?;
            let mut baseline: Self = serde_json::from_str(&content)
                .unwrap_or_else(|_| Self::new());
            baseline.path = Some(path);
            baseline.dirty = false;
            Ok(baseline)
        } else {
            // Create parent directories if needed
            if let Some(parent) = path.parent() {
                if !parent.exists() {
                    std::fs::create_dir_all(parent)?;
                }
            }
            let mut baseline = Self::new();
            baseline.path = Some(path);
            Ok(baseline)
        }
    }

    /// Record a command execution.
    /// Returns Some(alert) if command was never seen before.
    pub fn record(&mut self, command: &str) -> Option<BaselineAlert> {
        let now = current_timestamp();
        let is_new = !self.commands.contains_key(command);

        let stats = self.commands.entry(command.to_string()).or_insert_with(|| {
            CommandStats {
                first_seen: now,
                last_seen: now,
                count: 0,
            }
        });
        stats.last_seen = now;
        stats.count += 1;
        self.dirty = true;

        if is_new {
            Some(BaselineAlert {
                command: command.to_string(),
                first_seen: now,
                message: format!("First time seeing command: {}", command),
            })
        } else {
            None
        }
    }

    /// Check if command is known (without recording it)
    pub fn is_known(&self, command: &str) -> bool {
        self.commands.contains_key(command)
    }

    /// Get stats for a command
    pub fn get_stats(&self, command: &str) -> Option<&CommandStats> {
        self.commands.get(command)
    }

    /// Get total number of known commands
    pub fn known_count(&self) -> usize {
        self.commands.len()
    }

    /// Get all known commands
    pub fn known_commands(&self) -> Vec<&str> {
        self.commands.keys().map(|s| s.as_str()).collect()
    }

    /// Persist baseline to disk (call periodically, not on every event)
    pub fn persist(&mut self) -> std::io::Result<()> {
        if let Some(path) = &self.path {
            if self.dirty {
                let content = serde_json::to_string_pretty(self)?;
                std::fs::write(path, content)?;
                self.dirty = false;
            }
        }
        Ok(())
    }

    /// Force persist regardless of dirty flag
    pub fn force_persist(&self) -> std::io::Result<()> {
        if let Some(path) = &self.path {
            let content = serde_json::to_string_pretty(self)?;
            std::fs::write(path, content)?;
        }
        Ok(())
    }

    /// Check if there are unsaved changes
    pub fn is_dirty(&self) -> bool {
        self.dirty
    }

    /// Clear all baseline data
    pub fn clear(&mut self) {
        self.commands.clear();
        self.dirty = true;
    }

    /// Get path where baseline is stored
    pub fn storage_path(&self) -> Option<&PathBuf> {
        self.path.as_ref()
    }
}

/// Get current Unix timestamp
fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn temp_path(suffix: &str) -> PathBuf {
        let dir = std::env::temp_dir();
        dir.join(format!("clauditor_baseline_test_{}_{}.json", std::process::id(), suffix))
    }

    #[test]
    fn test_new_command_returns_alert() {
        let mut baseline = CommandBaseline::new();
        let alert = baseline.record("curl");
        assert!(alert.is_some());
        let a = alert.unwrap();
        assert_eq!(a.command, "curl");
        assert!(a.first_seen > 0);
    }

    #[test]
    fn test_known_command_returns_none() {
        let mut baseline = CommandBaseline::new();
        baseline.record("curl"); // First time
        let alert = baseline.record("curl"); // Second time
        assert!(alert.is_none());
    }

    #[test]
    fn test_count_increments() {
        let mut baseline = CommandBaseline::new();
        baseline.record("wget");
        baseline.record("wget");
        baseline.record("wget");
        let stats = baseline.get_stats("wget").unwrap();
        assert_eq!(stats.count, 3);
    }

    #[test]
    fn test_timestamps_recorded() {
        let mut baseline = CommandBaseline::new();
        baseline.record("ssh");
        let stats = baseline.get_stats("ssh").unwrap();
        assert!(stats.first_seen > 0);
        assert!(stats.last_seen >= stats.first_seen);
    }

    #[test]
    fn test_is_known() {
        let mut baseline = CommandBaseline::new();
        assert!(!baseline.is_known("nc"));
        baseline.record("nc");
        assert!(baseline.is_known("nc"));
    }

    #[test]
    fn test_known_count() {
        let mut baseline = CommandBaseline::new();
        assert_eq!(baseline.known_count(), 0);
        baseline.record("cmd1");
        baseline.record("cmd2");
        baseline.record("cmd1"); // Duplicate
        assert_eq!(baseline.known_count(), 2);
    }

    #[test]
    fn test_known_commands() {
        let mut baseline = CommandBaseline::new();
        baseline.record("alpha");
        baseline.record("beta");
        let cmds = baseline.known_commands();
        assert!(cmds.contains(&"alpha"));
        assert!(cmds.contains(&"beta"));
    }

    #[test]
    fn test_persist_and_load() {
        let path = temp_path("persist_load");
        
        // Cleanup from previous runs
        let _ = fs::remove_file(&path);

        // Create and save
        {
            let mut baseline = CommandBaseline::with_path(path.clone()).unwrap();
            baseline.record("test_cmd");
            baseline.record("test_cmd"); // Count = 2
            baseline.persist().unwrap();
        }

        // Load and verify
        {
            let baseline = CommandBaseline::with_path(path.clone()).unwrap();
            assert!(baseline.is_known("test_cmd"));
            assert_eq!(baseline.get_stats("test_cmd").unwrap().count, 2);
        }

        // Cleanup
        let _ = fs::remove_file(&path);
    }

    #[test]
    fn test_load_missing_file_creates_new() {
        let path = temp_path("missing");
        let _ = fs::remove_file(&path); // Ensure doesn't exist
        
        let baseline = CommandBaseline::with_path(path.clone()).unwrap();
        assert!(baseline.commands.is_empty());
        assert_eq!(baseline.known_count(), 0);
        
        // Cleanup
        let _ = fs::remove_file(&path);
    }

    #[test]
    fn test_dirty_flag() {
        let mut baseline = CommandBaseline::new();
        assert!(!baseline.is_dirty());
        baseline.record("cmd");
        assert!(baseline.is_dirty());
    }

    #[test]
    fn test_persist_clears_dirty() {
        let path = temp_path("dirty");
        let _ = fs::remove_file(&path);

        let mut baseline = CommandBaseline::with_path(path.clone()).unwrap();
        baseline.record("cmd");
        assert!(baseline.is_dirty());
        baseline.persist().unwrap();
        assert!(!baseline.is_dirty());

        let _ = fs::remove_file(&path);
    }

    #[test]
    fn test_clear_resets_baseline() {
        let mut baseline = CommandBaseline::new();
        baseline.record("cmd1");
        baseline.record("cmd2");
        assert_eq!(baseline.known_count(), 2);
        baseline.clear();
        assert_eq!(baseline.known_count(), 0);
    }

    #[test]
    fn test_last_seen_updates() {
        let mut baseline = CommandBaseline::new();
        baseline.record("cmd");
        let first_last_seen = baseline.get_stats("cmd").unwrap().last_seen;
        
        std::thread::sleep(std::time::Duration::from_millis(10));
        baseline.record("cmd");
        
        let new_last_seen = baseline.get_stats("cmd").unwrap().last_seen;
        // Last seen should be same or newer (time resolution is 1 second)
        assert!(new_last_seen >= first_last_seen);
    }

    #[test]
    fn test_serialization_format() {
        let mut baseline = CommandBaseline::new();
        baseline.record("test");
        
        let json = serde_json::to_string(&baseline).unwrap();
        assert!(json.contains("\"commands\""));
        assert!(json.contains("\"test\""));
        assert!(json.contains("\"first_seen\""));
        assert!(json.contains("\"last_seen\""));
        assert!(json.contains("\"count\""));
    }

    #[test]
    fn test_multiple_commands_independent() {
        let mut baseline = CommandBaseline::new();
        baseline.record("cmd_a");
        baseline.record("cmd_a");
        baseline.record("cmd_b");
        
        assert_eq!(baseline.get_stats("cmd_a").unwrap().count, 2);
        assert_eq!(baseline.get_stats("cmd_b").unwrap().count, 1);
    }

    #[test]
    fn test_corrupt_file_falls_back_to_new() {
        let path = temp_path("corrupt");
        
        // Write corrupt JSON
        fs::write(&path, "{ invalid json }}}").unwrap();
        
        let baseline = CommandBaseline::with_path(path.clone()).unwrap();
        assert!(baseline.commands.is_empty()); // Should be empty, not error
        
        let _ = fs::remove_file(&path);
    }
}
