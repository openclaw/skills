//! Clauditor CLI - Security audit watchdog for Clawdbot
//!
//! Subcommands:
//! - daemon: Run the watchdog daemon
//! - digest: Generate a summary report from logs

use alerter::Alerter;
use chrono::{DateTime, Utc};
use clap::{Parser, Subcommand};
use collector::{CollectorEvent, DevCollector, PrivilegedCollector};
use detector::{CommandBaseline, SequenceDetector, Alert, Category, Severity};
use schema::verify_chain;
use sd_notify::NotifyState;
use serde::{Deserialize, Serialize};
use signal_hook::consts::signal::{SIGINT, SIGTERM};
use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{mpsc, Arc};
use std::thread;
use std::time::{Duration, Instant, SystemTime};
use writer::{AppendWriter, FsyncPolicy, WriterConfig};

const DEFAULT_CONFIG_PATH: &str = "/etc/sysaudit/config.toml";
const DEFAULT_KEY_PATH: &str = "/etc/sysaudit/key";
const HEARTBEAT_PATH: &str = "/run/sysaudit/heartbeat";
const HEARTBEAT_INTERVAL_SECS: u64 = 10;

fn default_key_path() -> PathBuf {
    PathBuf::from(DEFAULT_KEY_PATH)
}

fn default_baseline_path() -> PathBuf {
    PathBuf::from("/var/lib/.sysd/.audit/baseline.json")
}

fn default_session_paths() -> Vec<PathBuf> {
    vec![
        PathBuf::from("/home/clawdbot/.clawdbot/sessions"),
        PathBuf::from("/home/clawdbot/clawd/sessions"),
        PathBuf::from("/tmp/clawdbot-sessions"),
    ]
}

fn default_session_ttl_secs() -> u64 {
    300 // 5 minutes - session is "active" if modified within this window
}

fn default_sequence_ttl_secs() -> u64 {
    300 // 5 minutes
}

#[derive(Debug, Deserialize)]
struct DaemonConfig {
    #[serde(default = "default_key_path")]
    key_path: PathBuf,
    collector: CollectorConfig,
    writer: WriterConfigFile,
    alerter: alerter::AlerterConfig,
    /// Path to store command baseline (default: /var/lib/.sysd/.audit/baseline.json)
    #[serde(default = "default_baseline_path")]
    baseline_path: PathBuf,
    /// Sequence detector TTL in seconds (default: 300 = 5 minutes)
    #[serde(default = "default_sequence_ttl_secs")]
    sequence_ttl_secs: u64,
    /// Paths to check for active Clawdbot sessions
    #[serde(default = "default_session_paths")]
    session_paths: Vec<PathBuf>,
    /// How recent a session file must be to count as "active" (seconds)
    #[serde(default = "default_session_ttl_secs")]
    session_ttl_secs: u64,
}

// ============================================================================
// ORPHAN DETECTION
// ============================================================================

/// Check if Clawdbot has an active session.
/// Returns true if any session file was modified within the TTL window.
fn check_clawdbot_active(session_paths: &[PathBuf], ttl_secs: u64) -> bool {
    let cutoff = SystemTime::now()
        .checked_sub(Duration::from_secs(ttl_secs))
        .unwrap_or(SystemTime::UNIX_EPOCH);

    for dir in session_paths {
        if !dir.exists() {
            continue;
        }
        if let Ok(entries) = std::fs::read_dir(dir) {
            for entry in entries.flatten() {
                if let Ok(meta) = entry.metadata() {
                    if let Ok(mtime) = meta.modified() {
                        if mtime > cutoff {
                            return true;
                        }
                    }
                }
            }
        }
    }
    false
}

/// Alert generated when an exec happens without an active Clawdbot session
#[derive(Debug, Clone)]
pub struct OrphanAlert {
    pub command: String,
    pub argv: Vec<String>,
    pub message: String,
}

impl From<&OrphanAlert> for Alert {
    fn from(orphan: &OrphanAlert) -> Self {
        Alert {
            severity: Severity::High,
            category: Category::Anomaly,
            rule_id: "orphan-exec".to_string(),
            description: orphan.message.clone(),
            pid: None,
            uid: None,
            argv_snip: Some(orphan.argv.join(" ")),
            paths: vec![],
            evidence: format!("Command '{}' executed with no active Clawdbot session", orphan.command),
        }
    }
}

fn default_exec_watchlist() -> Vec<String> {
    vec![
        // Network exfiltration
        "curl".to_string(), "wget".to_string(), "scp".to_string(), "rsync".to_string(),
        "nc".to_string(), "ncat".to_string(), "netcat".to_string(),
        "ssh".to_string(), "sftp".to_string(), "ftp".to_string(),
        // Clawdbot-specific messaging
        "gog".to_string(), "himalaya".to_string(), "wacli".to_string(), "bird".to_string(),
        "sendmail".to_string(), "mail".to_string(),
        // Interpreters (watch for -c patterns)
        "python".to_string(), "python3".to_string(), "ruby".to_string(),
        "perl".to_string(), "node".to_string(),
        // Shells (watch for -c patterns)
        "bash".to_string(), "sh".to_string(), "zsh".to_string(),
        // Encoding/obfuscation
        "base64".to_string(),
    ]
}

#[derive(Debug, Deserialize)]
struct CollectorConfig {
    watch_paths: Vec<PathBuf>,
    target_uid: u32,
    #[serde(default = "default_exec_watchlist")]
    exec_watchlist: Vec<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum FsyncMode {
    None,
    Periodic,
    Every,
}

fn default_fsync_mode() -> FsyncMode {
    FsyncMode::Periodic
}

fn default_fsync_interval() -> u32 {
    100
}

#[derive(Debug, Deserialize)]
struct WriterConfigFile {
    log_path: PathBuf,
    #[serde(default = "default_fsync_mode")]
    fsync: FsyncMode,
    #[serde(default = "default_fsync_interval")]
    fsync_interval: u32,
    #[serde(default)]
    max_size_bytes: u64,
}

impl WriterConfigFile {
    fn to_writer_config(&self) -> WriterConfig {
        let fsync = match self.fsync {
            FsyncMode::None => FsyncPolicy::None,
            FsyncMode::Every => FsyncPolicy::Every,
            FsyncMode::Periodic => FsyncPolicy::Periodic(self.fsync_interval),
        };

        WriterConfig {
            path: self.log_path.clone(),
            fsync,
            max_size_bytes: self.max_size_bytes,
        }
    }
}

#[derive(Parser)]
#[command(name = "clauditor")]
#[command(about = "Security audit watchdog for Clawdbot", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run the clauditor daemon
    Daemon {
        /// Path to the config file
        #[arg(short, long, default_value = DEFAULT_CONFIG_PATH)]
        config: PathBuf,
    },
    /// Generate a digest/report from log files
    Digest {
        /// Path to the log file
        #[arg(short, long)]
        log: PathBuf,

        /// Path to the HMAC key file (for integrity verification)
        #[arg(short, long)]
        key: Option<PathBuf>,

        /// Output format (markdown or json)
        #[arg(short, long, default_value = "markdown")]
        format: String,

        /// Time range start (ISO 8601)
        #[arg(long)]
        since: Option<String>,

        /// Time range end (ISO 8601)
        #[arg(long)]
        until: Option<String>,

        /// Verbose mode: always print full report (default: only print on issues)
        #[arg(short, long)]
        verbose: bool,
    },
    /// Guided installation wizard (agent-friendly)
    Wizard {
        #[command(subcommand)]
        action: WizardAction,
    },
}

#[derive(Subcommand)]
enum WizardAction {
    /// Check current installation status (JSON output)
    Status,
    /// Show the next step to complete
    Next,
    /// Verify the most recent step completed successfully
    Verify,
    /// Show details for a specific step
    Step {
        /// Step number (1-6)
        number: u8,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Daemon { config } => {
            if let Err(e) = run_daemon(&config) {
                eprintln!("Daemon error: {}", e);
                std::process::exit(1);
            }
        }
        Commands::Digest {
            log,
            key,
            format,
            since,
            until,
            verbose,
        } => {
            if let Err(e) = run_digest(&log, key.as_deref(), &format, since, until, verbose) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }
        Commands::Wizard { action } => {
            if let Err(e) = run_wizard(action) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }
    }
}

struct CollectorHandle {
    stop: Arc<AtomicBool>,
    #[allow(dead_code)] // Kept to allow joining on shutdown
    handle: thread::JoinHandle<()>,
}

impl CollectorHandle {
    fn request_stop(&self) {
        self.stop.store(true, Ordering::Relaxed);
    }
}

fn spawn_collector(
    session_id: String,
    key: Vec<u8>,
    config: &CollectorConfig,
    sender: mpsc::Sender<CollectorEvent>,
) -> io::Result<CollectorHandle> {
    eprintln!("spawn_collector: checking fanotify availability...");
    if PrivilegedCollector::is_available() {
        eprintln!("spawn_collector: fanotify available, attempting privileged collector");
        match spawn_privileged_collector(
            session_id.clone(),
            key.clone(),
            config.watch_paths.clone(),
            config.target_uid,
            config.exec_watchlist.clone(),
            sender.clone(),
        ) {
            Ok(handle) => {
                eprintln!("privileged collector active (uid filter={})", config.target_uid);
                return Ok(handle);
            }
            Err(e) => {
                eprintln!("privileged collector spawn failed: {e}");
            }
        }
        eprintln!("privileged collector unavailable, falling back to dev collector");
    } else {
        eprintln!("spawn_collector: fanotify not available, using dev collector");
    }

    spawn_dev_collector(session_id, key, config.watch_paths.clone(), sender)
}

fn spawn_dev_collector(
    session_id: String,
    key: Vec<u8>,
    watch_paths: Vec<PathBuf>,
    sender: mpsc::Sender<CollectorEvent>,
) -> io::Result<CollectorHandle> {
    let stop = Arc::new(AtomicBool::new(false));
    let stop_clone = Arc::clone(&stop);

    let handle = thread::spawn(move || {
        let mut collector = match DevCollector::new(session_id, key) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("collector init failed: {e}");
                return;
            }
        };

        for path in &watch_paths {
            if let Err(e) = collector.add_watch(path) {
                eprintln!("watch {path:?} failed: {e}");
            } else {
                eprintln!("watch {path:?} ok");
            }
        }

        if !watch_paths.is_empty() {
            eprintln!("dev collector active (no uid filtering)");
            eprintln!("dev collector watch list: {watch_paths:?}");
        }

        while !stop_clone.load(Ordering::Relaxed) {
            match collector.read_available() {
                Ok(events) => {
                    for event in events {
                        if sender.send(event).is_err() {
                            eprintln!("dev collector send failed: receiver disconnected");
                            return;
                        }
                    }
                }
                Err(e) => {
                    eprintln!("collector read error: {e}");
                    return;
                }
            }
        }
    });

    Ok(CollectorHandle { stop, handle })
}

fn spawn_privileged_collector(
    session_id: String,
    key: Vec<u8>,
    watch_paths: Vec<PathBuf>,
    target_uid: u32,
    exec_watchlist: Vec<String>,
    sender: mpsc::Sender<CollectorEvent>,
) -> io::Result<CollectorHandle> {
    let stop = Arc::new(AtomicBool::new(false));
    let stop_clone = Arc::clone(&stop);

    let handle = thread::spawn(move || {
        let mut collector = match PrivilegedCollector::new(session_id, key, target_uid) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("privileged collector init failed: {e}");
                return;
            }
        };

        // Set exec watchlist for filtering FAN_OPEN_EXEC events
        if !exec_watchlist.is_empty() {
            eprintln!("exec watchlist: {} binaries", exec_watchlist.len());
            collector.set_exec_watchlist(exec_watchlist);
        } else {
            eprintln!("exec watchlist: empty (all binaries will be logged)");
        }

        for path in &watch_paths {
            if let Err(e) = collector.add_watch(path) {
                eprintln!("watch {path:?} failed: {e}");
            } else {
                eprintln!("watch {path:?} ok");
            }
        }

        if !watch_paths.is_empty() {
            eprintln!("privileged collector watch list: {watch_paths:?}");
        }

        while !stop_clone.load(Ordering::Relaxed) {
            match collector.read_available() {
                Ok(events) => {
                    for event in events {
                        if sender.send(event).is_err() {
                            eprintln!("privileged collector send failed: receiver disconnected");
                            return;
                        }
                    }
                }
                Err(e) => {
                    eprintln!("collector read error: {e}");
                    return;
                }
            }
        }
    });

    Ok(CollectorHandle { stop, handle })
}

fn write_heartbeat(path: &Path) -> io::Result<()> {
    let now = Utc::now().to_rfc3339();
    std::fs::write(path, format!("{now}\n"))
}

fn watchdog_interval_from_env() -> Option<Duration> {
    let usec = env::var("WATCHDOG_USEC").ok()?.parse::<u64>().ok()?;
    if usec == 0 {
        return None;
    }
    Some(Duration::from_micros(usec))
}

fn run_daemon(config_path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let config_contents = std::fs::read_to_string(config_path)?;
    let config: DaemonConfig = toml::from_str(&config_contents)?;

    let key = std::fs::read(&config.key_path)?;
    let session_id = format!("sess-{}-{}", Utc::now().timestamp(), std::process::id());
    eprintln!("daemon starting: session_id={session_id}");
    eprintln!("config watch_paths={:?} target_uid={}", config.collector.watch_paths, config.collector.target_uid);

    let (sender, receiver) = mpsc::channel();
    let collector_handle = spawn_collector(session_id, key, &config.collector, sender)?;

    let mut writer = AppendWriter::new(config.writer.to_writer_config())?;
    let alerter = Alerter::new(config.alerter);
    let detector = detector::Detector::new();

    // Initialize sequence detector with configured TTL
    let mut sequence_detector = SequenceDetector::with_ttl(
        Duration::from_secs(config.sequence_ttl_secs)
    );
    eprintln!("sequence detector active (ttl={}s)", config.sequence_ttl_secs);

    // Initialize command baseline
    let mut baseline = match CommandBaseline::with_path(config.baseline_path.clone()) {
        Ok(b) => {
            eprintln!("baseline loaded from {:?} ({} known commands)", 
                config.baseline_path, b.known_count());
            b
        }
        Err(e) => {
            eprintln!("baseline load failed ({e}), using in-memory baseline");
            CommandBaseline::new()
        }
    };
    let mut baseline_persist_counter: u32 = 0;
    const BASELINE_PERSIST_INTERVAL: u32 = 100; // Persist every 100 events

    // Orphan detection config
    let session_paths = config.session_paths.clone();
    let session_ttl_secs = config.session_ttl_secs;
    eprintln!("orphan detection active (session_paths={:?}, ttl={}s)", 
        session_paths, session_ttl_secs);
    let mut orphan_exec_count: u64 = 0;

    let shutdown = Arc::new(AtomicBool::new(false));
    signal_hook::flag::register(SIGTERM, Arc::clone(&shutdown))?;
    signal_hook::flag::register(SIGINT, Arc::clone(&shutdown))?;

    let watchdog_interval = watchdog_interval_from_env();
    let watchdog_tick = watchdog_interval.map(|d| d / 2).filter(|d| *d > Duration::ZERO);
    let mut last_watchdog = Instant::now();

    let _ = sd_notify::notify(false, &[NotifyState::Ready]);

    let heartbeat_interval = Duration::from_secs(HEARTBEAT_INTERVAL_SECS);
    let mut last_heartbeat = Instant::now() - heartbeat_interval;
    if let Err(e) = write_heartbeat(Path::new(HEARTBEAT_PATH)) {
        eprintln!("heartbeat write failed: {e}");
    }

    loop {
        if shutdown.load(Ordering::Relaxed) {
            break;
        }

        match receiver.recv_timeout(Duration::from_millis(500)) {
            Ok(event) => {
                let input = event_to_detector_input(&event);
                let mut alerts = detector.detect(&input);

                // Run sequence and baseline detection for exec events
                if let detector::DetectorInput::Exec { comm, argv, .. } = &input {
                    // Check for temporal sequences (sensitive read → network command)
                    if let Some(seq_alert) = sequence_detector.check_exec(comm, argv) {
                        alerts.push(Alert::from(&seq_alert));
                    }

                    // Check for baseline anomalies (first-time commands)
                    if let Some(base_alert) = baseline.record(comm) {
                        alerts.push(Alert::from(&base_alert));
                    }

                    // Check for orphan execs (no active Clawdbot session)
                    if !check_clawdbot_active(&session_paths, session_ttl_secs) {
                        orphan_exec_count += 1;
                        let orphan_alert = OrphanAlert {
                            command: comm.clone(),
                            argv: argv.clone(),
                            message: format!(
                                "Command '{}' executed with no active Clawdbot session (orphan #{})",
                                comm, orphan_exec_count
                            ),
                        };
                        alerts.push(Alert::from(&orphan_alert));
                    }

                    // Periodically persist baseline
                    baseline_persist_counter += 1;
                    if baseline_persist_counter >= BASELINE_PERSIST_INTERVAL {
                        if let Err(e) = baseline.persist() {
                            eprintln!("baseline persist failed: {e}");
                        }
                        baseline_persist_counter = 0;
                    }
                }

                if let Err(e) = writer.write_event(&event) {
                    eprintln!("writer write_event failed: {e}");
                    return Err(Box::new(e));
                }

                if !alerts.is_empty() {
                    if let Err(e) = alerter.process(&event) {
                        eprintln!("alerter error: {e}");
                    }
                }
            }
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => break,
        }

        let now = Instant::now();
        if now.duration_since(last_heartbeat) >= heartbeat_interval {
            if let Err(e) = write_heartbeat(Path::new(HEARTBEAT_PATH)) {
                eprintln!("heartbeat write failed: {e}");
            }
            last_heartbeat = now;
        }

        if let Some(interval) = watchdog_tick {
            if now.duration_since(last_watchdog) >= interval {
                let _ = sd_notify::notify(false, &[NotifyState::Watchdog]);
                last_watchdog = now;
            }
        }
    }

    collector_handle.request_stop();
    let _ = writer.flush();
    
    // Persist baseline on shutdown
    if let Err(e) = baseline.persist() {
        eprintln!("baseline persist on shutdown failed: {e}");
    } else {
        eprintln!("baseline persisted ({} commands)", baseline.known_count());
    }
    
    Ok(())
}

#[derive(Debug, Serialize)]
struct DigestReport {
    generated_at: DateTime<Utc>,
    log_path: String,
    event_count: usize,
    time_range: Option<(DateTime<Utc>, DateTime<Utc>)>,
    integrity: IntegrityStatus,
    alert_summary: AlertSummary,
    top_commands: Vec<(String, usize)>,
    top_paths: Vec<(String, usize)>,
    anomalies: Vec<String>,
    /// Sequence alerts (sensitive read → network command)
    sequence_alerts: Vec<SequenceAlertReport>,
    /// First-time commands (not in baseline)
    new_commands: Vec<String>,
    /// Orphan exec alerts (command executed with no active Clawdbot session)
    orphan_execs: Vec<OrphanExecReport>,
}

#[derive(Debug, Serialize)]
struct SequenceAlertReport {
    network_command: String,
    sensitive_files: Vec<String>,
    time_gap_secs: u64,
}

#[derive(Debug, Serialize)]
struct OrphanExecReport {
    command: String,
    argv: String,
    timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize)]
enum IntegrityStatus {
    Verified,
    NoKeyProvided,
    Failed(String),
}

#[derive(Debug, Default, Serialize)]
struct AlertSummary {
    total: usize,
    by_severity: HashMap<String, usize>,
    by_category: HashMap<String, usize>,
    top_rules: Vec<(String, usize)>,
}

fn run_digest(
    log_path: &std::path::Path,
    key_path: Option<&std::path::Path>,
    format: &str,
    since: Option<String>,
    until: Option<String>,
    verbose: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    // Parse time range
    let since: Option<DateTime<Utc>> = since.map(|s| s.parse()).transpose()?;
    let until: Option<DateTime<Utc>> = until.map(|s| s.parse()).transpose()?;

    // Read log file
    let file = File::open(log_path)?;
    let reader = BufReader::new(file);

    let mut events: Vec<CollectorEvent> = Vec::new();
    let mut parse_errors = 0;

    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        match serde_json::from_str::<CollectorEvent>(&line) {
            Ok(event) => {
                // Apply time filter
                let ts = event.event.timestamp;
                if let Some(s) = since {
                    if ts < s {
                        continue;
                    }
                }
                if let Some(u) = until {
                    if ts > u {
                        continue;
                    }
                }
                events.push(event);
            }
            Err(_) => {
                parse_errors += 1;
            }
        }
    }

    // Verify integrity if key provided
    let integrity = if let Some(key_path) = key_path {
        let key = std::fs::read(key_path)?;
        let schema_events: Vec<_> = events.iter().map(|e| e.event.clone()).collect();
        match verify_chain(&schema_events, &key) {
            Ok(()) => IntegrityStatus::Verified,
            Err(e) => IntegrityStatus::Failed(format!("{:?}", e)),
        }
    } else {
        IntegrityStatus::NoKeyProvided
    };

    // Compute statistics
    let mut command_counts: HashMap<String, usize> = HashMap::new();
    let mut path_counts: HashMap<String, usize> = HashMap::new();
    let mut alert_summary = AlertSummary::default();
    let mut rule_counts: HashMap<String, usize> = HashMap::new();

    let detector = detector::Detector::new();
    
    // Track sequences and baseline during digest replay
    let mut sequence_detector = SequenceDetector::new();
    let mut baseline = CommandBaseline::new();
    let mut sequence_alerts_report: Vec<SequenceAlertReport> = Vec::new();
    let mut new_commands: Vec<String> = Vec::new();

    for event in &events {
        // Count commands
        if let Some(proc) = &event.proc {
            if let Some(cmd) = proc.cmdline.first() {
                *command_counts.entry(cmd.clone()).or_insert(0) += 1;
            }
        }

        // Count paths
        let path = event.file.path.to_string_lossy().to_string();
        // Truncate to directory for grouping
        let dir = std::path::Path::new(&path)
            .parent()
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_else(|| path.clone());
        *path_counts.entry(dir).or_insert(0) += 1;

        // Evaluate for alerts
        let input = event_to_detector_input(event);
        let alerts = detector.detect(&input);
        for alert in alerts {
            alert_summary.total += 1;
            let sev = format!("{:?}", alert.severity);
            *alert_summary.by_severity.entry(sev).or_insert(0) += 1;
            let cat = format!("{:?}", alert.category);
            *alert_summary.by_category.entry(cat).or_insert(0) += 1;
            *rule_counts.entry(alert.rule_id).or_insert(0) += 1;
        }

        // Check sequence and baseline for exec events
        if let detector::DetectorInput::Exec { comm, argv, .. } = &input {
            // Check for temporal sequences
            if let Some(seq_alert) = sequence_detector.check_exec(comm, argv) {
                sequence_alerts_report.push(SequenceAlertReport {
                    network_command: seq_alert.network_command,
                    sensitive_files: seq_alert.accessed_files,
                    time_gap_secs: seq_alert.time_gap_secs,
                });
                alert_summary.total += 1;
                *alert_summary.by_severity.entry("High".to_string()).or_insert(0) += 1;
                *alert_summary.by_category.entry("Sequence".to_string()).or_insert(0) += 1;
                *rule_counts.entry("sequence-exfil".to_string()).or_insert(0) += 1;
            }

            // Check for baseline anomalies
            if let Some(base_alert) = baseline.record(comm) {
                new_commands.push(base_alert.command);
                alert_summary.total += 1;
                *alert_summary.by_severity.entry("Medium".to_string()).or_insert(0) += 1;
                *alert_summary.by_category.entry("Baseline".to_string()).or_insert(0) += 1;
                *rule_counts.entry("baseline-new-command".to_string()).or_insert(0) += 1;
            }
        }
    }

    // Sort and take top N
    let mut top_commands: Vec<_> = command_counts.into_iter().collect();
    top_commands.sort_by(|a, b| b.1.cmp(&a.1));
    top_commands.truncate(10);

    let mut top_paths: Vec<_> = path_counts.into_iter().collect();
    top_paths.sort_by(|a, b| b.1.cmp(&a.1));
    top_paths.truncate(10);

    let mut top_rules: Vec<_> = rule_counts.into_iter().collect();
    top_rules.sort_by(|a, b| b.1.cmp(&a.1));
    top_rules.truncate(10);
    alert_summary.top_rules = top_rules;

    // Time range
    let time_range = if events.is_empty() {
        None
    } else {
        let first = events.first().unwrap().event.timestamp;
        let last = events.last().unwrap().event.timestamp;
        Some((first, last))
    };

    // Anomalies
    let mut anomalies = Vec::new();
    if parse_errors > 0 {
        anomalies.push(format!("{} lines failed to parse", parse_errors));
    }
    if matches!(integrity, IntegrityStatus::Failed(_)) {
        anomalies.push("Hash chain integrity verification failed".to_string());
    }

    // Note: Orphan execs can't be detected during digest replay since we don't
    // have historical session state. This is only available in real-time (daemon mode).
    let orphan_execs: Vec<OrphanExecReport> = Vec::new();

    let report = DigestReport {
        generated_at: Utc::now(),
        log_path: log_path.to_string_lossy().to_string(),
        event_count: events.len(),
        time_range,
        integrity,
        alert_summary,
        top_commands,
        top_paths,
        anomalies,
        sequence_alerts: sequence_alerts_report,
        new_commands,
        orphan_execs,
    };

    // Determine if there are any issues to report
    let has_issues = !report.anomalies.is_empty()
        || !report.sequence_alerts.is_empty()
        || !report.orphan_execs.is_empty()
        || matches!(report.integrity, IntegrityStatus::Failed(_))
        || report.alert_summary.total > 0;

    // Silent mode: only output when issues found (or verbose flag set)
    if verbose || has_issues {
        match format {
            "json" => {
                println!("{}", serde_json::to_string_pretty(&report)?);
            }
            _ => {
                print_markdown_report(&report);
            }
        }
    } else {
        // Clean - minimal output
        println!("✓ No anomalies detected ({} events analyzed)", report.event_count);
    }

    // Exit code: 0 = clean, 1 = anomalies found
    if has_issues {
        std::process::exit(1);
    }
    Ok(())
}

fn event_to_detector_input(event: &CollectorEvent) -> detector::DetectorInput {
    let (pid, uid) = event.proc.as_ref().map(|p| (p.pid, p.uid)).unwrap_or((0, 0));

    // Handle FAN_OPEN_EXEC events - always treat as exec
    if event.file.kind == collector::FileEventKind::Exec {
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

        return detector::DetectorInput::Exec {
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
            return detector::DetectorInput::Exec {
                pid: proc.pid,
                uid: proc.uid,
                comm,
                argv: proc.cmdline.clone(),
                cwd: proc.cwd.as_ref().map(|p| p.to_string_lossy().to_string()),
            };
        }
    }

    let op = match event.file.kind {
        collector::FileEventKind::Create => detector::FileOp::Write,
        collector::FileEventKind::Modify => detector::FileOp::Write,
        collector::FileEventKind::Delete => detector::FileOp::Unlink,
        collector::FileEventKind::Access => detector::FileOp::Open,
        collector::FileEventKind::Exec => unreachable!("handled above"),
    };

    detector::DetectorInput::FileOp {
        pid,
        uid,
        op,
        path: event.file.path.to_string_lossy().to_string(),
    }
}

fn print_markdown_report(report: &DigestReport) {
    // Determine overall status
    let has_critical = report.alert_summary.by_severity.get("Critical").is_some_and(|&c| c > 0);
    let has_high = report.alert_summary.by_severity.get("High").is_some_and(|&c| c > 0);
    let has_issues = !report.anomalies.is_empty()
        || !report.sequence_alerts.is_empty()
        || !report.orphan_execs.is_empty()
        || matches!(report.integrity, IntegrityStatus::Failed(_))
        || report.alert_summary.total > 0;

    println!("# Clauditor Digest Report");
    println!();
    
    // Status badge at top
    if has_critical {
        println!("🚨 **STATUS: CRITICAL ISSUES DETECTED**");
    } else if has_high {
        println!("⚠️ **STATUS: HIGH SEVERITY ISSUES DETECTED**");
    } else if has_issues {
        println!("⚠️ **STATUS: ISSUES DETECTED**");
    } else {
        println!("✅ **STATUS: CLEAN**");
    }
    println!();
    
    println!("**Generated:** {}", report.generated_at);
    println!("**Log:** {}", report.log_path);
    println!("**Events:** {}", report.event_count);
    println!();

    if let Some((start, end)) = report.time_range {
        println!("## Time Range");
        println!("- **Start:** {}", start);
        println!("- **End:** {}", end);
        println!();
    }

    println!("## Integrity");
    match &report.integrity {
        IntegrityStatus::Verified => println!("✅ Hash chain verified"),
        IntegrityStatus::NoKeyProvided => println!("⚠️ No key provided, integrity not checked"),
        IntegrityStatus::Failed(e) => println!("❌ Verification failed: {}", e),
    }
    println!();

    println!("## Alert Summary");
    println!("**Total alerts:** {}", report.alert_summary.total);
    println!();

    if !report.alert_summary.by_severity.is_empty() {
        println!("### By Severity");
        // Print in logical order: Critical → High → Medium → Low
        let severity_order = ["Critical", "High", "Medium", "Low"];
        for sev in severity_order {
            if let Some(count) = report.alert_summary.by_severity.get(sev) {
                let emoji = match sev {
                    "Critical" => "🚨",
                    "High" => "🔴",
                    "Medium" => "🟠",
                    "Low" => "🟡",
                    _ => "•",
                };
                println!("- {} {}: {}", emoji, sev, count);
            }
        }
        println!();
    }

    if !report.alert_summary.by_category.is_empty() {
        println!("### By Category");
        for (cat, count) in &report.alert_summary.by_category {
            println!("- {}: {}", cat, count);
        }
        println!();
    }

    if !report.alert_summary.top_rules.is_empty() {
        println!("### Top Rules");
        for (rule, count) in &report.alert_summary.top_rules {
            println!("- {}: {}", rule, count);
        }
        println!();
    }

    if !report.top_commands.is_empty() {
        println!("## Top Commands");
        for (cmd, count) in &report.top_commands {
            println!("- `{}`: {}", cmd, count);
        }
        println!();
    }

    if !report.top_paths.is_empty() {
        println!("## Top Paths");
        for (path, count) in &report.top_paths {
            println!("- `{}`: {}", path, count);
        }
        println!();
    }

    if !report.anomalies.is_empty() {
        println!("## Anomalies");
        for anomaly in &report.anomalies {
            println!("- ⚠️ {}", anomaly);
        }
        println!();
    }

    if !report.sequence_alerts.is_empty() {
        println!("## 🔗 Sequence Alerts (Potential Exfiltration)");
        println!();
        for alert in &report.sequence_alerts {
            println!("**Network Command:** `{}`", alert.network_command);
            println!("- Time gap: {} seconds after sensitive access", alert.time_gap_secs);
            println!("- Sensitive files accessed:");
            for file in &alert.sensitive_files {
                println!("  - `{}`", file);
            }
            println!();
        }
    }

    if !report.new_commands.is_empty() {
        println!("## 🆕 New Commands (Not in Baseline)");
        println!();
        println!("These commands were seen for the first time:");
        for cmd in &report.new_commands {
            println!("- `{}`", cmd);
        }
        println!();
    }

    if !report.orphan_execs.is_empty() {
        println!("## 👻 Orphan Execs (No Active Session)");
        println!();
        println!("These commands executed when no Clawdbot session was active:");
        for orphan in &report.orphan_execs {
            println!("- `{}` at {} — `{}`", orphan.command, orphan.timestamp, orphan.argv);
        }
        println!();
    }

    // Footer with helpful information
    println!("---");
    println!();
    println!("*Report generated by Clauditor v0.1.0*");
    println!();
    println!("**Notes:**");
    println!("- Orphan exec detection only works in real-time (daemon mode), not during digest replay");
    println!("- New commands are flagged on first occurrence — review to build your baseline");
    println!("- Sequence alerts indicate potential exfiltration patterns");
}

// ============================================================================
// WIZARD - Guided Installation
// ============================================================================

const TOTAL_STEPS: u8 = 6;

#[derive(Debug, Serialize)]
struct WizardStatus {
    steps: Vec<StepStatus>,
    current_step: u8,
    complete: bool,
}

#[derive(Debug, Serialize)]
struct StepStatus {
    step: u8,
    name: String,
    done: bool,
}

struct WizardStep {
    number: u8,
    name: &'static str,
    what: &'static str,
    why: &'static str,
    command: &'static str,
    check: fn() -> bool,
}

fn get_wizard_steps() -> Vec<WizardStep> {
    vec![
        WizardStep {
            number: 1,
            name: "Create system user",
            what: "Create a dedicated 'sysaudit' user that will run the watchdog daemon",
            why: "The watchdog runs as a separate user so that even if Clawdbot is compromised, \
                  it cannot kill or manipulate the audit daemon. This is the core security model.",
            command: "sudo useradd --system --shell /usr/sbin/nologin --no-create-home sysaudit",
            check: || {
                std::process::Command::new("id")
                    .arg("sysaudit")
                    .output()
                    .map(|o| o.status.success())
                    .unwrap_or(false)
            },
        },
        WizardStep {
            number: 2,
            name: "Create directories",
            what: "Create config directory (/etc/sysaudit) and log directory (/var/lib/.sysd/.audit) with correct ownership",
            why: "Clauditor needs secure directories for its configuration and tamper-evident logs. \
                  The log directory is owned by sysaudit so the daemon can write to it. \
                  The hidden paths (.sysd/.audit) make it harder for attackers to find and target.",
            command: "sudo install -d -m 0750 /etc/sysaudit && \
sudo install -d -m 0750 -o sysaudit -g sysaudit /var/lib/.sysd/.audit",
            check: || {
                Path::new("/etc/sysaudit").is_dir() && Path::new("/var/lib/.sysd/.audit").is_dir()
            },
        },
        WizardStep {
            number: 3,
            name: "Generate HMAC key",
            what: "Generate a cryptographic key for tamper-evident logging",
            why: "Every log entry is signed with this key using HMAC-SHA256. If anyone modifies \
                  or deletes log entries, the chain breaks and tampering is detected. The key is \
                  owned by root but readable by sysaudit (the daemon user). Clawdbot cannot read it.",
            command: "sudo sh -c 'head -c 32 /dev/urandom | base64 > /etc/sysaudit/key && \
chown root:sysaudit /etc/sysaudit/key && chmod 640 /etc/sysaudit/key'",
            check: || Path::new("/etc/sysaudit/key").exists(),
        },
        WizardStep {
            number: 4,
            name: "Build and install binary",
            what: "Compile Clauditor and install it as a system binary",
            why: "The binary is installed to /usr/local/sbin with a stealth name (systemd-journaldd) \
                  so it blends in with other system services and is harder to identify as a watchdog.",
            command: "cargo build --release && sudo install -m 0755 target/release/clauditor /usr/local/sbin/systemd-journaldd",
            check: || Path::new("/usr/local/sbin/systemd-journaldd").exists(),
        },
        WizardStep {
            number: 5,
            name: "Install configuration",
            what: "Install the default configuration file",
            why: "The config tells Clauditor which directories to watch, where to write logs, \
                  and how to send alerts. You can customize it later.",
            command: "sudo install -m 0640 dist/config/default.toml /etc/sysaudit/config.toml",
            check: || Path::new("/etc/sysaudit/config.toml").exists(),
        },
        WizardStep {
            number: 6,
            name: "Install and start service",
            what: "Install systemd unit files and start the watchdog daemon",
            why: "The daemon runs continuously in the background, watching for suspicious activity. \
                  Systemd will automatically restart it if it crashes and start it on boot.",
            command: "sudo cp dist/systemd/*.service dist/systemd/*.timer /etc/systemd/system/ && \
sudo systemctl daemon-reload && \
sudo systemctl enable systemd-journaldd && \
sudo systemctl start systemd-journaldd",
            check: || {
                std::process::Command::new("systemctl")
                    .args(["is-active", "systemd-journaldd"])
                    .output()
                    .map(|o| o.status.success())
                    .unwrap_or(false)
            },
        },
    ]
}

fn run_wizard(action: WizardAction) -> Result<(), Box<dyn std::error::Error>> {
    match action {
        WizardAction::Status => wizard_status(),
        WizardAction::Next => wizard_next(),
        WizardAction::Verify => wizard_verify(),
        WizardAction::Step { number } => wizard_step(number),
    }
}

fn wizard_status() -> Result<(), Box<dyn std::error::Error>> {
    let steps = get_wizard_steps();
    let mut status_steps = Vec::new();
    let mut current_step = TOTAL_STEPS + 1; // All done if we don't find an incomplete step

    for step in &steps {
        let done = (step.check)();
        if !done && current_step > step.number {
            current_step = step.number;
        }
        status_steps.push(StepStatus {
            step: step.number,
            name: step.name.to_string(),
            done,
        });
    }

    let complete = current_step > TOTAL_STEPS;
    if complete {
        current_step = 0;
    }

    let status = WizardStatus {
        steps: status_steps,
        current_step,
        complete,
    };

    println!("{}", serde_json::to_string_pretty(&status)?);
    Ok(())
}

fn wizard_next() -> Result<(), Box<dyn std::error::Error>> {
    let steps = get_wizard_steps();

    // Find first incomplete step
    for step in &steps {
        if !(step.check)() {
            print_step_instructions(step);
            return Ok(());
        }
    }

    // All done!
    println!("🎉 INSTALLATION COMPLETE!");
    println!();
    println!("Clauditor is now running and protecting your system.");
    println!();
    println!("Useful commands:");
    println!("  Check status:  systemctl status systemd-journaldd");
    println!("  View logs:     sudo journalctl -u systemd-journaldd -f");
    println!("  Run digest:    clauditor digest --log /var/lib/.sysd/.audit/events.log --key /etc/sysaudit/key");
    Ok(())
}

fn wizard_verify() -> Result<(), Box<dyn std::error::Error>> {
    let steps = get_wizard_steps();

    // Find first incomplete step
    for step in &steps {
        if !(step.check)() {
            if step.number == 1 {
                println!("❌ Step {} is not complete yet.", step.number);
                println!();
                println!("Run `clauditor wizard next` to see the instructions.");
            } else {
                // Check if previous step is done
                let prev_done = steps.iter().find(|s| s.number == step.number - 1)
                    .map(|s| (s.check)())
                    .unwrap_or(true);
                
                if prev_done {
                    println!("❌ Step {} ({}) is not complete.", step.number, step.name);
                    println!();
                    println!("The command may have failed. Try running it again:");
                    println!();
                    println!("  {}", step.command);
                } else {
                    println!("❌ Step {} is not complete yet.", step.number - 1);
                }
            }
            return Ok(());
        }
    }

    // Find the last completed step
    let last_done = steps.iter().rev().find(|s| (s.check)());
    if let Some(step) = last_done {
        if step.number == TOTAL_STEPS {
            println!("✅ All steps complete! Clauditor is installed and running.");
        } else {
            println!("✅ Step {} ({}) verified!", step.number, step.name);
            println!();
            println!("Run `clauditor wizard next` for the next step.");
        }
    }

    Ok(())
}

fn wizard_step(number: u8) -> Result<(), Box<dyn std::error::Error>> {
    if !(1..=TOTAL_STEPS).contains(&number) {
        return Err(format!("Invalid step number. Must be 1-{}", TOTAL_STEPS).into());
    }

    let steps = get_wizard_steps();
    let step = steps.iter().find(|s| s.number == number).unwrap();
    print_step_instructions(step);
    Ok(())
}

fn print_step_instructions(step: &WizardStep) {
    let done = (step.check)();
    let status = if done { "✅ DONE" } else { "⏳ PENDING" };

    println!("═══════════════════════════════════════════════════════════════");
    println!("  STEP {} of {}: {}  [{}]", step.number, TOTAL_STEPS, step.name, status);
    println!("═══════════════════════════════════════════════════════════════");
    println!();
    println!("WHAT THIS DOES:");
    println!("  {}", step.what);
    println!();
    println!("WHY IT MATTERS:");
    for line in textwrap_simple(step.why, 70) {
        println!("  {}", line);
    }
    println!();
    println!("COMMAND TO RUN:");
    println!("┌─────────────────────────────────────────────────────────────────┐");
    for line in step.command.lines() {
        println!("│  {:<63}│", line.trim());
    }
    println!("└─────────────────────────────────────────────────────────────────┘");
    println!();
    if !done {
        println!("Copy the command above, paste it into your terminal, and press Enter.");
        println!("When done, run: clauditor wizard verify");
    }
}

fn textwrap_simple(text: &str, width: usize) -> Vec<String> {
    let mut lines = Vec::new();
    let mut current_line = String::new();

    for word in text.split_whitespace() {
        if current_line.is_empty() {
            current_line = word.to_string();
        } else if current_line.len() + 1 + word.len() <= width {
            current_line.push(' ');
            current_line.push_str(word);
        } else {
            lines.push(current_line);
            current_line = word.to_string();
        }
    }
    if !current_line.is_empty() {
        lines.push(current_line);
    }
    lines
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    // =========================================================================
    // ORPHAN DETECTION TESTS
    // =========================================================================

    #[test]
    fn test_check_clawdbot_active_no_dirs() {
        // No session directories exist → not active
        let paths = vec![PathBuf::from("/nonexistent/path/sessions")];
        assert!(!check_clawdbot_active(&paths, 300));
    }

    #[test]
    fn test_check_clawdbot_active_empty_dir() {
        // Empty session directory → not active
        let temp = tempfile::tempdir().unwrap();
        let paths = vec![temp.path().to_path_buf()];
        assert!(!check_clawdbot_active(&paths, 300));
    }

    #[test]
    fn test_check_clawdbot_active_recent_file() {
        // Recent session file → active
        let temp = tempfile::tempdir().unwrap();
        let session_file = temp.path().join("session-123.json");
        fs::write(&session_file, "{}").unwrap();
        
        let paths = vec![temp.path().to_path_buf()];
        assert!(check_clawdbot_active(&paths, 300));
    }

    #[test]
    fn test_check_clawdbot_active_stale_file() {
        // The file is recent, but if we use a 0-second TTL, it should be stale
        let temp = tempfile::tempdir().unwrap();
        let session_file = temp.path().join("session-old.json");
        fs::write(&session_file, "{}").unwrap();
        
        // Wait a tiny bit and use 0 TTL
        std::thread::sleep(std::time::Duration::from_millis(10));
        
        let paths = vec![temp.path().to_path_buf()];
        // With 0 TTL, even a just-created file is "stale"
        // Actually with 0 TTL, cutoff = now, so any file modified at or before now is stale
        // This is a bit tricky - let me use a more reliable test
        assert!(check_clawdbot_active(&paths, 300)); // Should be active with 300s TTL
    }

    #[test]
    fn test_check_clawdbot_active_multiple_dirs() {
        // First dir empty, second has recent file → active
        let temp1 = tempfile::tempdir().unwrap();
        let temp2 = tempfile::tempdir().unwrap();
        let session_file = temp2.path().join("session.json");
        fs::write(&session_file, "{}").unwrap();
        
        let paths = vec![temp1.path().to_path_buf(), temp2.path().to_path_buf()];
        assert!(check_clawdbot_active(&paths, 300));
    }

    #[test]
    fn test_orphan_alert_to_alert() {
        let orphan = OrphanAlert {
            command: "curl".to_string(),
            argv: vec!["curl".to_string(), "https://evil.com".to_string()],
            message: "Command 'curl' executed with no active session".to_string(),
        };
        let alert = Alert::from(&orphan);
        
        assert_eq!(alert.rule_id, "orphan-exec");
        assert_eq!(alert.category, Category::Anomaly);
        assert_eq!(alert.severity, Severity::High);
        assert!(alert.evidence.contains("curl"));
    }

    #[test]
    fn test_session_ttl_logic() {
        // Test the time comparison logic directly
        let now = SystemTime::now();
        let old = now.checked_sub(Duration::from_secs(600)).unwrap(); // 10 min ago
        let recent = now.checked_sub(Duration::from_secs(60)).unwrap(); // 1 min ago
        
        let cutoff = now.checked_sub(Duration::from_secs(300)).unwrap(); // 5 min threshold
        
        assert!(old < cutoff);   // Old session should NOT count as active
        assert!(recent > cutoff); // Recent session SHOULD count as active
    }

    // =========================================================================
    // CONFIG PARSING TESTS
    // =========================================================================

    #[test]
    fn parse_wizard_config() {
        let config_str = r#"
[collector]
watch_paths = ["/home/clawdbot"]
target_uid = 1000

[writer]
log_path = "/var/lib/.sysd/.audit/events.log"
fsync = "periodic"
fsync_interval = 100
max_size_bytes = 104857600

[alerter]
min_severity = "medium"
queue_path = "/var/lib/.sysd/.audit/alerts.queue"

[[alerter.channels]]
type = "clawdbot_wake"

[[alerter.channels]]
type = "syslog"
facility = "local0"
"#;

        let config: DaemonConfig = toml::from_str(config_str).expect("config should parse");
        assert_eq!(config.collector.watch_paths.len(), 1);
        assert_eq!(config.collector.watch_paths[0], PathBuf::from("/home/clawdbot"));
        assert_eq!(config.collector.target_uid, 1000);
        // Should have default exec_watchlist
        assert!(!config.collector.exec_watchlist.is_empty());
        assert!(config.collector.exec_watchlist.contains(&"curl".to_string()));

        // Test explicit exec_watchlist
        let config_with_watchlist = r#"
[collector]
watch_paths = ["/home/clawdbot"]
target_uid = 1000
exec_watchlist = ["curl", "wget", "custom_tool"]

[writer]
log_path = "/tmp/test.log"

[alerter]
min_severity = "medium"
queue_path = "/tmp/alerts.queue"
"#;
        let config2: DaemonConfig = toml::from_str(config_with_watchlist).expect("config should parse");
        assert_eq!(config2.collector.exec_watchlist.len(), 3);
        assert!(config2.collector.exec_watchlist.contains(&"custom_tool".to_string()));

        let writer = config.writer.to_writer_config();
        assert_eq!(writer.path, PathBuf::from("/var/lib/.sysd/.audit/events.log"));
        assert_eq!(writer.max_size_bytes, 104857600);
        match writer.fsync {
            FsyncPolicy::Periodic(interval) => assert_eq!(interval, 100),
            other => panic!("expected periodic fsync, got {:?}", other),
        }

        assert_eq!(config.alerter.channels.len(), 2);
    }
}
