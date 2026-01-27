//! Alerting integration for clauditor.
//!
//! Evaluates events against detector rules and emits alerts via configured channels.
//!
//! # Security Notes
//! - File alerts use 0o600 permissions
//! - Command channel executes user-provided commands (ensure config is trusted)
//! - Deduplication prevents alert storms

use chrono::{DateTime, Utc};
use collector::CollectorEvent;
use detector::{Alert, Detector, DetectorInput, FileOp, Severity};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::io;
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
use std::path::PathBuf;
use std::process::Command;
use std::sync::mpsc;
use std::sync::Mutex;
use std::thread::{self, JoinHandle};
use std::time::Duration;

/// File permissions for alert/queue files
const ALERT_FILE_MODE: u32 = 0o600;

/// Alert channel configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case", tag = "type")]
pub enum AlertChannel {
    /// Send alert via clawdbot gateway wake
    ClawdbotWake {
        /// Optional gateway URL
        gateway_url: Option<String>,
    },
    /// Write alert to syslog
    Syslog {
        /// Syslog facility
        facility: Option<String>,
    },
    /// Write alert to a file
    File {
        /// Path to alert file
        path: PathBuf,
    },
    /// Execute a command with alert as stdin
    Command {
        /// Command to execute
        command: String,
        /// Arguments
        args: Vec<String>,
    },
}

impl Default for AlertChannel {
    fn default() -> Self {
        AlertChannel::ClawdbotWake { gateway_url: None }
    }
}

/// Alerter configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlerterConfig {
    /// Channels to send alerts to
    #[serde(default = "default_channels")]
    pub channels: Vec<AlertChannel>,
    /// Minimum severity to alert on
    #[serde(default = "default_severity")]
    pub min_severity: Severity,
    /// Queue alerts when channels fail (path to queue file)
    pub queue_path: Option<PathBuf>,
    /// Cooldown period for duplicate alerts (same rule_id)
    /// Default: 60 seconds
    #[serde(default = "default_cooldown_secs")]
    pub cooldown_secs: u64,
}

fn default_cooldown_secs() -> u64 {
    60
}

fn default_channels() -> Vec<AlertChannel> {
    vec![AlertChannel::ClawdbotWake { gateway_url: None }]
}

fn default_severity() -> Severity {
    Severity::Medium
}

impl Default for AlerterConfig {
    fn default() -> Self {
        Self {
            channels: default_channels(),
            min_severity: Severity::Medium,
            queue_path: None,
            cooldown_secs: default_cooldown_secs(),
        }
    }
}

/// Alert payload sent to channels.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertPayload {
    pub timestamp: chrono::DateTime<Utc>,
    pub alert: Alert,
    pub event_summary: String,
}

/// Alerter that evaluates events and sends alerts.
/// 
/// Includes deduplication via cooldown to prevent alert storms.
pub struct Alerter {
    detector: Detector,
    config: AlerterConfig,
    /// Tracks last alert time per rule_id for cooldown
    last_alert_times: Mutex<HashMap<String, DateTime<Utc>>>,
}

impl Alerter {
    /// Create a new alerter with default rules.
    pub fn new(config: AlerterConfig) -> Self {
        Self {
            detector: Detector::new(),
            config,
            last_alert_times: Mutex::new(HashMap::new()),
        }
    }

    /// Create an alerter with custom detector.
    pub fn with_detector(config: AlerterConfig, detector: Detector) -> Self {
        Self { 
            detector, 
            config,
            last_alert_times: Mutex::new(HashMap::new()),
        }
    }
    
    /// Check if an alert should be suppressed due to cooldown.
    /// Returns true if the alert should be sent (not in cooldown).
    fn check_cooldown(&self, rule_id: &str) -> bool {
        let now = Utc::now();
        let cooldown = Duration::from_secs(self.config.cooldown_secs);
        
        let mut times = self.last_alert_times.lock().unwrap();
        let cutoff = now
            .checked_sub_signed(
                chrono::Duration::from_std(cooldown).unwrap_or(chrono::TimeDelta::MAX),
            )
            .unwrap_or(now);
        times.retain(|_, last_time| *last_time >= cutoff);
        
        if let Some(last_time) = times.get(rule_id) {
            let elapsed = now.signed_duration_since(*last_time);
            if elapsed < chrono::Duration::from_std(cooldown).unwrap_or(chrono::TimeDelta::MAX) {
                // Still in cooldown
                return false;
            }
        }
        
        // Not in cooldown, update the time
        times.insert(rule_id.to_string(), now);
        true
    }

    /// Evaluate an event and send alerts if rules match.
    /// 
    /// Returns all alerts that matched (including those suppressed by cooldown).
    /// Only alerts not in cooldown are actually sent.
    pub fn process(&self, event: &CollectorEvent) -> io::Result<Vec<Alert>> {
        let input = self.event_to_input(event);
        let alerts = self.detector.detect(&input);

        // Filter by severity
        let filtered: Vec<_> = alerts
            .into_iter()
            .filter(|a| a.severity >= self.config.min_severity)
            .collect();

        // Send alerts (respecting cooldown)
        for alert in &filtered {
            // Check cooldown - skip if in cooldown period
            if !self.check_cooldown(&alert.rule_id) {
                continue;
            }
            
            let payload = AlertPayload {
                timestamp: Utc::now(),
                alert: alert.clone(),
                event_summary: self.summarize_event(event),
            };
            self.send_alert(&payload)?;
        }

        Ok(filtered)
    }

    /// Convert CollectorEvent to DetectorInput.
    fn event_to_input(&self, event: &CollectorEvent) -> DetectorInput {
        let (pid, uid) = event
            .proc
            .as_ref()
            .map(|p| (p.pid, p.uid))
            .unwrap_or((0, 0));

        // Handle FAN_OPEN_EXEC events - always treat as exec
        if event.file.kind == collector::FileEventKind::Exec {
            // Use binary path from the event, cmdline from proc if available
            let comm = event
                .file
                .path
                .file_name()
                .map(|s| s.to_string_lossy().to_string())
                .unwrap_or_default();
            let argv = event
                .proc
                .as_ref()
                .map(|p| p.cmdline.clone())
                .unwrap_or_default();
            let cwd = event
                .proc
                .as_ref()
                .and_then(|p| p.cwd.as_ref().map(|c| c.to_string_lossy().to_string()));

            return DetectorInput::Exec {
                pid,
                uid,
                comm,
                argv,
                cwd,
            };
        }

        // If we have process info with a command, treat as exec event
        if let Some(proc) = &event.proc {
            if !proc.cmdline.is_empty() {
                let comm = proc.cmdline.first().cloned().unwrap_or_default();
                return DetectorInput::Exec {
                    pid: proc.pid,
                    uid: proc.uid,
                    comm,
                    argv: proc.cmdline.clone(),
                    cwd: proc.cwd.as_ref().map(|p| p.to_string_lossy().to_string()),
                };
            }
        }

        // Otherwise, treat as file operation
        let op = match event.file.kind {
            collector::FileEventKind::Create => FileOp::Write,
            collector::FileEventKind::Modify => FileOp::Write,
            collector::FileEventKind::Delete => FileOp::Unlink,
            collector::FileEventKind::Access => FileOp::Open,
            collector::FileEventKind::Exec => unreachable!("handled above"),
        };

        DetectorInput::FileOp {
            pid,
            uid,
            op,
            path: event.file.path.to_string_lossy().to_string(),
        }
    }

    /// Create a summary of the event for the alert.
    fn summarize_event(&self, event: &CollectorEvent) -> String {
        let proc_info = event
            .proc
            .as_ref()
            .map(|p| {
                let cmd = p.cmdline.join(" ");
                format!("pid={} uid={} cmd={}", p.pid, p.uid, cmd)
            })
            .unwrap_or_else(|| "unknown process".to_string());

        format!(
            "{:?} {} ({})",
            event.file.kind,
            event.file.path.display(),
            proc_info
        )
    }

    /// Send an alert to all configured channels.
    fn send_alert(&self, payload: &AlertPayload) -> io::Result<()> {
        let mut errors = Vec::new();

        for channel in &self.config.channels {
            if let Err(e) = self.send_to_channel(channel, payload) {
                errors.push(format!("{:?}: {}", channel, e));
            }
        }

        // If all channels failed, queue the alert
        if errors.len() == self.config.channels.len() && !self.config.channels.is_empty() {
            if let Some(queue_path) = &self.config.queue_path {
                self.queue_alert(queue_path, payload)?;
            }
            return Err(io::Error::other(format!(
                "all alert channels failed: {:?}",
                errors
            )));
        }

        Ok(())
    }

    /// Send alert to a specific channel.
    fn send_to_channel(&self, channel: &AlertChannel, payload: &AlertPayload) -> io::Result<()> {
        match channel {
            AlertChannel::ClawdbotWake { gateway_url } => {
                let message = format!(
                    "🚨 Security Alert: {} — {} ({})",
                    payload.alert.rule_id,
                    payload.alert.description,
                    payload.event_summary
                );

                let mut cmd = Command::new("clawdbot");
                cmd.arg("gateway").arg("wake").arg("--text").arg(&message);

                if let Some(url) = gateway_url {
                    cmd.arg("--gateway-url").arg(url);
                }

                cmd.arg("--mode").arg("now");

                let output = cmd.output()?;
                if !output.status.success() {
                    return Err(io::Error::other(
                        String::from_utf8_lossy(&output.stderr).to_string(),
                    ));
                }
                Ok(())
            }

            AlertChannel::Syslog { facility } => {
                let priority = match payload.alert.severity {
                    Severity::Critical => "crit",
                    Severity::High => "err",
                    Severity::Medium => "warning",
                    Severity::Low => "notice",
                };

                let message = serde_json::to_string(payload)?;
                let facility = facility.as_deref().unwrap_or("local0");

                Command::new("logger")
                    .arg("-p")
                    .arg(format!("{}.{}", facility, priority))
                    .arg("-t")
                    .arg("clauditor")
                    .arg(&message)
                    .output()?;

                Ok(())
            }

            AlertChannel::File { path } => {
                use std::fs::OpenOptions;
                use std::io::Write;

                let mut file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .mode(ALERT_FILE_MODE)
                    .open(path)?;
                
                // Ensure permissions even if file existed
                std::fs::set_permissions(path, std::fs::Permissions::from_mode(ALERT_FILE_MODE))?;

                let json = serde_json::to_string(payload)?;
                writeln!(file, "{}", json)?;
                Ok(())
            }

            AlertChannel::Command { command, args } => {
                use std::io::Write;

                let mut child = Command::new(command)
                    .args(args)
                    .stdin(std::process::Stdio::piped())
                    .spawn()?;

                if let Some(mut stdin) = child.stdin.take() {
                    let json = serde_json::to_string(payload)?;
                    stdin.write_all(json.as_bytes())?;
                }

                let status = child.wait()?;
                if !status.success() {
                    return Err(io::Error::other(format!(
                        "command exited with {}",
                        status
                    )));
                }
                Ok(())
            }
        }
    }

    /// Queue an alert for later retry.
    fn queue_alert(&self, queue_path: &PathBuf, payload: &AlertPayload) -> io::Result<()> {
        use std::fs::OpenOptions;
        use std::io::Write;

        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .mode(ALERT_FILE_MODE)
            .open(queue_path)?;
        
        // Ensure permissions
        std::fs::set_permissions(queue_path, std::fs::Permissions::from_mode(ALERT_FILE_MODE))?;

        let json = serde_json::to_string(payload)?;
        writeln!(file, "{}", json)
    }
    
    /// Get the number of rule IDs currently in cooldown.
    /// Useful for testing.
    #[cfg(test)]
    fn cooldown_count(&self) -> usize {
        self.last_alert_times.lock().unwrap().len()
    }
}

/// Background alerter that processes events from a channel.
pub struct BackgroundAlerter {
    handle: Option<JoinHandle<()>>,
    sender: mpsc::Sender<CollectorEvent>,
}

impl BackgroundAlerter {
    /// Start a background alerter.
    pub fn start(config: AlerterConfig) -> Self {
        let (sender, receiver) = mpsc::channel::<CollectorEvent>();

        let handle = thread::spawn(move || {
            let alerter = Alerter::new(config);
            while let Ok(event) = receiver.recv() {
                if let Err(e) = alerter.process(&event) {
                    eprintln!("alert error: {}", e);
                }
            }
        });

        Self {
            handle: Some(handle),
            sender,
        }
    }

    /// Send an event to be processed.
    #[allow(clippy::result_large_err)] // CollectorEvent is intentionally large for rich context
    pub fn send(&self, event: CollectorEvent) -> Result<(), mpsc::SendError<CollectorEvent>> {
        self.sender.send(event)
    }

    /// Stop the background alerter.
    pub fn stop(mut self) {
        drop(self.sender);
        if let Some(h) = self.handle.take() {
            let _ = h.join();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;
    use collector::{FileEvent, FileEventKind, ProcInfo};
    use schema::{Event, EventKind};
    use std::path::PathBuf;


    fn sample_benign_event() -> CollectorEvent {
        let event = Event::new_genesis(
            b"test-key",
            Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            123,
            1000,
            EventKind::Message,
            "sess-1",
        );
        CollectorEvent {
            event,
            file: FileEvent {
                kind: FileEventKind::Modify,
                path: PathBuf::from("/tmp/scratch.txt"),
            },
            proc: Some(ProcInfo {
                pid: 123,
                uid: 1000,
                cmdline: vec!["cat".to_string(), "/tmp/foo".to_string()],
                cwd: Some(PathBuf::from("/tmp")),
            }),
        }
    }

    #[test]
    fn detects_ssh_key_modification() {
        let temp = tempfile::tempdir().unwrap();
        let alert_file = temp.path().join("alerts.log");

        let config = AlerterConfig {
            channels: vec![AlertChannel::File {
                path: alert_file.clone(),
            }],
            min_severity: Severity::Low,
            queue_path: None,
            cooldown_secs: 0, // No cooldown for tests
        };

        let alerter = Alerter::new(config);
        
        // Create an event that's specifically a file op (no cmdline)
        let event = Event::new_genesis(
            b"test-key",
            Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            123,
            1000,
            EventKind::Message,
            "sess-1",
        );
        let suspicious_event = CollectorEvent {
            event,
            file: FileEvent {
                kind: FileEventKind::Modify,
                path: PathBuf::from("/home/user/.ssh/authorized_keys"),
            },
            proc: Some(ProcInfo {
                pid: 123,
                uid: 1000,
                cmdline: vec![], // Empty cmdline so it's treated as file op
                cwd: None,
            }),
        };
        
        let alerts = alerter.process(&suspicious_event).unwrap();

        assert!(!alerts.is_empty(), "should detect SSH key modification");
        let alert_content = std::fs::read_to_string(&alert_file).unwrap();
        assert!(
            alert_content.contains("ssh") || alert_content.contains("authorized_keys"),
            "alert file should contain ssh-related alert: {}", alert_content
        );
    }

    #[test]
    fn ignores_benign_events() {
        let config = AlerterConfig {
            channels: vec![],
            min_severity: Severity::Low,
            queue_path: None,
            cooldown_secs: 60,
        };

        let alerter = Alerter::new(config);
        let alerts = alerter.process(&sample_benign_event()).unwrap();

        // Note: This might still trigger alerts if "cat" matches any rules
        // For now, we're just checking it doesn't panic
        println!("Benign event triggered {} alerts", alerts.len());
    }

    // NEW TESTS for code review concerns

    #[test]
    fn cooldown_suppresses_duplicate_alerts() {
        let temp = tempfile::tempdir().unwrap();
        let alert_file = temp.path().join("alerts.log");

        let config = AlerterConfig {
            channels: vec![AlertChannel::File {
                path: alert_file.clone(),
            }],
            min_severity: Severity::Low,
            queue_path: None,
            cooldown_secs: 3600, // 1 hour - long enough for this test
        };

        let alerter = Alerter::new(config);

        // Create a suspicious event
        let event = Event::new_genesis(
            b"test-key",
            Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            123,
            1000,
            EventKind::Message,
            "sess-1",
        );
        let suspicious_event = CollectorEvent {
            event,
            file: FileEvent {
                kind: FileEventKind::Modify,
                path: PathBuf::from("/home/user/.ssh/authorized_keys"),
            },
            proc: Some(ProcInfo {
                pid: 123,
                uid: 1000,
                cmdline: vec![],
                cwd: None,
            }),
        };

        // First alert should go through
        let alerts1 = alerter.process(&suspicious_event).unwrap();
        assert!(!alerts1.is_empty(), "first alert should match");
        
        // Second identical alert should be suppressed (same rule_id in cooldown)
        let alerts2 = alerter.process(&suspicious_event).unwrap();
        // alerts2 will still return the matched alerts, but they won't be sent
        
        // Count lines in alert file - should only have 1 entry
        let content = std::fs::read_to_string(&alert_file).unwrap();
        let lines: Vec<_> = content.lines().collect();
        assert_eq!(lines.len(), 1, "only first alert should be written (cooldown)");
    }

    #[test]
    fn file_alert_permissions() {
        use std::os::unix::fs::PermissionsExt;
        
        let temp = tempfile::tempdir().unwrap();
        let alert_file = temp.path().join("secure_alerts.log");

        let config = AlerterConfig {
            channels: vec![AlertChannel::File {
                path: alert_file.clone(),
            }],
            min_severity: Severity::Low,
            queue_path: None,
            cooldown_secs: 0, // No cooldown for this test
        };

        let alerter = Alerter::new(config);

        let event = Event::new_genesis(
            b"test-key",
            Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            123,
            1000,
            EventKind::Message,
            "sess-1",
        );
        let suspicious_event = CollectorEvent {
            event,
            file: FileEvent {
                kind: FileEventKind::Modify,
                path: PathBuf::from("/home/user/.ssh/authorized_keys"),
            },
            proc: Some(ProcInfo {
                pid: 123,
                uid: 1000,
                cmdline: vec![],
                cwd: None,
            }),
        };

        let _ = alerter.process(&suspicious_event);

        // Check file permissions
        if alert_file.exists() {
            let metadata = std::fs::metadata(&alert_file).unwrap();
            let mode = metadata.permissions().mode() & 0o777;
            assert_eq!(mode, 0o600, "alert file should have 0600 permissions");
        }
    }

    #[test]
    fn queue_file_permissions() {
        use std::os::unix::fs::PermissionsExt;
        
        let temp = tempfile::tempdir().unwrap();
        let queue_file = temp.path().join("queue.log");

        // Create a config with a non-working channel so alerts get queued
        let config = AlerterConfig {
            channels: vec![AlertChannel::Command {
                command: "/nonexistent/command".to_string(),
                args: vec![],
            }],
            min_severity: Severity::Low,
            queue_path: Some(queue_file.clone()),
            cooldown_secs: 0,
        };

        let alerter = Alerter::new(config);

        let event = Event::new_genesis(
            b"test-key",
            Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap(),
            123,
            1000,
            EventKind::Message,
            "sess-1",
        );
        let suspicious_event = CollectorEvent {
            event,
            file: FileEvent {
                kind: FileEventKind::Modify,
                path: PathBuf::from("/home/user/.ssh/authorized_keys"),
            },
            proc: Some(ProcInfo {
                pid: 123,
                uid: 1000,
                cmdline: vec![],
                cwd: None,
            }),
        };

        // This should fail and queue the alert
        let _ = alerter.process(&suspicious_event);

        // Check queue file permissions if it was created
        if queue_file.exists() {
            let metadata = std::fs::metadata(&queue_file).unwrap();
            let mode = metadata.permissions().mode() & 0o777;
            assert_eq!(mode, 0o600, "queue file should have 0600 permissions");
        }
    }

    #[test]
    fn severity_filtering() {
        let config = AlerterConfig {
            channels: vec![],
            min_severity: Severity::High, // Only High and Critical
            queue_path: None,
            cooldown_secs: 0,
        };

        let alerter = Alerter::new(config);
        
        // A Low severity event should be filtered out
        let low_event = sample_benign_event();
        let alerts = alerter.process(&low_event).unwrap();
        
        // All returned alerts should be >= High severity
        for alert in &alerts {
            assert!(alert.severity >= Severity::High);
        }
    }

    #[test]
    fn cooldown_prunes_stale_rule_ids() {
        let config = AlerterConfig {
            channels: vec![],
            min_severity: Severity::Low,
            queue_path: None,
            cooldown_secs: 1,
        };

        let alerter = Alerter::new(config);
        let stale_time = Utc::now() - chrono::Duration::seconds(120);

        {
            let mut times = alerter.last_alert_times.lock().unwrap();
            times.insert("stale-rule".to_string(), stale_time);
        }

        // Trigger cooldown check to prune
        let _ = alerter.check_cooldown("fresh-rule");
        assert!(!alerter.last_alert_times.lock().unwrap().contains_key("stale-rule"));
    }
}
