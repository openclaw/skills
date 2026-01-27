//! Collector crate for clauditor.
//!
//! Provides two backends:
//! - `DevCollector`: uses inotify, runs unprivileged (dev mode)
//! - `PrivilegedCollector`: uses fanotify with UID filtering (requires CAP_SYS_ADMIN)

use chrono::Utc;
use inotify::{Inotify, WatchDescriptor, WatchMask};
use schema::{Event, EventKind};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::io;
use std::os::unix::ffi::OsStrExt;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread::{self, JoinHandle};

mod privileged;
pub use privileged::PrivilegedCollector;

/// Buffer size for inotify event reading.
/// 4KB is typically sufficient but we use 16KB for safety with many events.
const INOTIFY_BUFFER_SIZE: usize = 16384;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FileEventKind {
    Create,
    Modify,
    Delete,
    /// Executable opened for execution (FAN_OPEN_EXEC)
    Exec,
    /// File accessed (opened or closed without modification)
    Access,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileEvent {
    pub kind: FileEventKind,
    pub path: PathBuf,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcInfo {
    pub pid: u32,
    pub uid: u32,
    pub cmdline: Vec<String>,
    pub cwd: Option<PathBuf>,
}

impl ProcInfo {
    /// Try to get process info from /proc.
    /// Returns None if the process doesn't exist or can't be read.
    /// Note: uid is required - if we can't read it, we return None
    /// rather than defaulting to 0 (which would be root).
    pub fn from_pid(pid: u32) -> Option<Self> {
        let cmdline = read_cmdline(pid)?;
        let cwd = read_cwd(pid);
        // Don't default uid to 0 (root) - that's a security issue
        let uid = read_uid(pid)?;
        Some(Self {
            pid,
            uid,
            cmdline,
            cwd,
        })
    }
    
    /// Get process info with a fallback uid if reading fails.
    /// Use this when you have a known uid from another source.
    pub fn from_pid_with_fallback_uid(pid: u32, fallback_uid: u32) -> Self {
        let cmdline = read_cmdline(pid).unwrap_or_default();
        let cwd = read_cwd(pid);
        let uid = read_uid(pid).unwrap_or(fallback_uid);
        Self {
            pid,
            uid,
            cmdline,
            cwd,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CollectorEvent {
    pub event: Event,
    pub file: FileEvent,
    pub proc: Option<ProcInfo>,
}

/// Development mode collector using inotify.
/// 
/// **Important limitations (dev mode only):**
/// - Events are attributed to the collector process itself, not the actual
///   process that made the change. Use `PrivilegedCollector` with fanotify
///   for accurate process attribution.
/// - Cannot filter by UID - captures all file events in watched directories.
/// 
/// For production use with accurate process tracking, use `PrivilegedCollector`.
pub struct DevCollector {
    inotify: Inotify,
    buffer: Vec<u8>,
    session_id: String,
    key: Vec<u8>,
    last_event: Option<Event>,
    watch_paths: HashMap<WatchDescriptor, PathBuf>,
    /// PID of the collector process (used for dev mode attribution)
    default_pid: u32,
    /// UID of the collector process (used for dev mode attribution)
    default_uid: u32,
}

impl DevCollector {
    pub fn new(session_id: impl Into<String>, key: Vec<u8>) -> io::Result<Self> {
        let inotify = Inotify::init()?;
        eprintln!(
            "dev collector init: pid={} uid={}",
            std::process::id(),
            unsafe { libc::geteuid() as u32 }
        );
        Ok(Self {
            inotify,
            buffer: vec![0u8; INOTIFY_BUFFER_SIZE],
            session_id: session_id.into(),
            key,
            last_event: None,
            watch_paths: HashMap::new(),
            default_pid: std::process::id(),
            default_uid: unsafe { libc::geteuid() as u32 },
        })
    }

    pub fn add_watch(&mut self, path: impl AsRef<Path>) -> io::Result<WatchDescriptor> {
        let path = path.as_ref().to_path_buf();
        let mask = WatchMask::CREATE
            | WatchMask::MODIFY
            | WatchMask::DELETE
            | WatchMask::MOVED_FROM
            | WatchMask::MOVED_TO
            | WatchMask::CLOSE_WRITE;
        let wd = self.inotify.watches().add(&path, mask)?;
        eprintln!("dev collector watch added: path={path:?} wd={wd:?}");
        self.watch_paths.insert(wd.clone(), path);
        Ok(wd)
    }

    pub fn read_available(&mut self) -> io::Result<Vec<CollectorEvent>> {
        let mut output = Vec::new();
        eprintln!("dev collector read_available: waiting for inotify events...");
        let events = self.inotify.read_events_blocking(&mut self.buffer)?;
        let mut event_count = 0usize;

        for event in events {
            event_count += 1;
            eprintln!(
                "dev collector raw event: wd={:?} mask={:?} name={:?}",
                event.wd, event.mask, event.name
            );
            let kind = match mask_to_kind(event.mask) {
                Some(kind) => kind,
                None => {
                    eprintln!("dev collector skipping event: unhandled mask={:?}", event.mask);
                    continue;
                }
            };

            let base = match self.watch_paths.get(&event.wd) {
                Some(path) => path.clone(),
                None => {
                    eprintln!("dev collector skipping event: unknown watch descriptor");
                    continue;
                }
            };

            let raw_path = match event.name {
                Some(name) => base.join(name),
                None => base.clone(),
            };
            
            // Skip paths that can't be validated (null bytes, etc.)
            let path = match validate_path(&raw_path) {
                Some(p) => p,
                None => {
                    eprintln!("dev collector skipping event: invalid path {:?}", raw_path);
                    continue;
                }
            };

            let proc_info = ProcInfo::from_pid(self.default_pid);
            let (pid, uid) = match &proc_info {
                Some(info) => (info.pid, info.uid),
                None => (self.default_pid, self.default_uid),
            };

            let timestamp = Utc::now();
            let schema_event = match &self.last_event {
                None => Event::new_genesis(
                    &self.key,
                    timestamp,
                    pid,
                    uid,
                    EventKind::Message,
                    self.session_id.clone(),
                ),
                Some(prev) => Event::new_next(
                    &self.key,
                    prev,
                    timestamp,
                    pid,
                    uid,
                    EventKind::Message,
                    self.session_id.clone(),
                ),
            };

            self.last_event = Some(schema_event.clone());

            output.push(CollectorEvent {
                event: schema_event,
                file: FileEvent { kind, path },
                proc: proc_info,
            });
        }

        eprintln!("dev collector read_available: processed {event_count} events");
        Ok(output)
    }
}

/// Collector with start/stop lifecycle.
/// Runs the DevCollector in a background thread and delivers events via callback.
pub struct Collector {
    stop_flag: Arc<AtomicBool>,
    handle: Option<JoinHandle<()>>,
}

impl Collector {
    /// Start collecting file events.
    /// `watch_paths` - directories to watch
    /// `on_event` - callback invoked for each event (must be Send + 'static)
    pub fn start<F>(
        session_id: impl Into<String>,
        key: Vec<u8>,
        watch_paths: Vec<PathBuf>,
        on_event: F,
    ) -> io::Result<Self>
    where
        F: Fn(CollectorEvent) + Send + 'static,
    {
        let session_id = session_id.into();
        let stop_flag = Arc::new(AtomicBool::new(false));
        let stop_clone = Arc::clone(&stop_flag);

        let handle = thread::spawn(move || {
            let mut collector = match DevCollector::new(&session_id, key) {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("collector init failed: {e}");
                    return;
                }
            };

            for path in &watch_paths {
                if let Err(e) = collector.add_watch(path) {
                    eprintln!("watch {path:?} failed: {e}");
                }
            }

            while !stop_clone.load(Ordering::Relaxed) {
                match collector.read_available() {
                    Ok(events) => {
                        for event in events {
                            on_event(event);
                        }
                    }
                    Err(e) => {
                        eprintln!("read error: {e}");
                        break;
                    }
                }
            }
        });

        Ok(Self {
            stop_flag,
            handle: Some(handle),
        })
    }

    /// Signal the collector to stop and wait for the thread to finish.
    pub fn stop(mut self) {
        self.stop_flag.store(true, Ordering::Relaxed);
        if let Some(h) = self.handle.take() {
            let _ = h.join();
        }
    }

    /// Check if the collector is still running.
    pub fn is_running(&self) -> bool {
        self.handle.as_ref().is_some_and(|h| !h.is_finished())
    }
}

impl Drop for Collector {
    fn drop(&mut self) {
        self.stop_flag.store(true, Ordering::Relaxed);
    }
}

fn mask_to_kind(mask: inotify::EventMask) -> Option<FileEventKind> {
    if mask.contains(inotify::EventMask::CREATE) || mask.contains(inotify::EventMask::MOVED_TO) {
        return Some(FileEventKind::Create);
    }
    if mask.contains(inotify::EventMask::DELETE) || mask.contains(inotify::EventMask::MOVED_FROM) {
        return Some(FileEventKind::Delete);
    }
    if mask.contains(inotify::EventMask::MODIFY) || mask.contains(inotify::EventMask::CLOSE_WRITE) {
        return Some(FileEventKind::Modify);
    }
    None
}

fn read_cmdline(pid: u32) -> Option<Vec<String>> {
    let path = format!("/proc/{pid}/cmdline");
    let data = std::fs::read(path).ok()?;
    if data.is_empty() {
        return Some(Vec::new());
    }
    let parts = data
        .split(|b| *b == 0)
        .filter(|chunk| !chunk.is_empty())
        .map(|chunk| String::from_utf8_lossy(chunk).to_string())
        .collect::<Vec<_>>();
    Some(parts)
}

fn read_cwd(pid: u32) -> Option<PathBuf> {
    let path = format!("/proc/{pid}/cwd");
    // read_link handles non-UTF8 paths correctly (returns OsString)
    std::fs::read_link(path).ok()
}

/// Validate path is safe to process.
/// Returns None for paths with null bytes or other problematic patterns.
fn validate_path(path: &Path) -> Option<PathBuf> {
    // Reject paths with embedded null bytes
    if path.as_os_str().as_bytes().contains(&0) {
        return None;
    }
    Some(path.to_path_buf())
}

fn read_uid(pid: u32) -> Option<u32> {
    let path = format!("/proc/{pid}/status");
    let status = std::fs::read_to_string(path).ok()?;
    for line in status.lines() {
        if let Some(rest) = line.strip_prefix("Uid:") {
            let uid_str = rest.split_whitespace().next()?;
            return uid_str.parse::<u32>().ok();
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::OsString;
    use std::os::unix::ffi::OsStringExt;
    use std::fs::{File, OpenOptions};
    use std::io::Write;
    
    #[test]
    fn emits_create_modify_delete_events() {
        let temp = tempfile::tempdir().unwrap();
        let file_path = temp.path().join("sample.txt");

        let mut collector = DevCollector::new("sess-1", b"test-key".to_vec()).unwrap();
        collector.add_watch(temp.path()).unwrap();

        File::create(&file_path).unwrap();
        let events = collector.read_available().unwrap();
        assert!(events.iter().any(|event| {
            event.file.kind == FileEventKind::Create && event.file.path == file_path
        }));

        let mut handle = OpenOptions::new().append(true).open(&file_path).unwrap();
        writeln!(handle, "hello").unwrap();
        drop(handle);

        let events = collector.read_available().unwrap();
        assert!(events.iter().any(|event| {
            event.file.kind == FileEventKind::Modify && event.file.path == file_path
        }));

        std::fs::remove_file(&file_path).unwrap();
        let events = collector.read_available().unwrap();
        assert!(events.iter().any(|event| {
            event.file.kind == FileEventKind::Delete && event.file.path == file_path
        }));
    }

    // NEW TESTS for code review concerns

    #[test]
    fn proc_info_from_self() {
        let pid = std::process::id();
        let info = ProcInfo::from_pid(pid).expect("should read own process");
        assert_eq!(info.pid, pid);
        // UID should be our actual UID, not 0
        assert!(info.uid > 0 || unsafe { libc::geteuid() } == 0);
    }

    #[test]
    fn proc_info_from_invalid_pid() {
        // PID 0 is the idle task, we shouldn't be able to read it normally
        // Use a very high PID that's unlikely to exist
        let info = ProcInfo::from_pid(u32::MAX);
        assert!(info.is_none());
    }

    #[test]
    fn proc_info_with_fallback_uid() {
        // Use a nonexistent PID
        let info = ProcInfo::from_pid_with_fallback_uid(u32::MAX, 1000);
        assert_eq!(info.uid, 1000);
        assert!(info.cmdline.is_empty());
    }

    #[test]
    fn validate_path_allows_normal_paths() {
        let path = PathBuf::from("/home/user/file.txt");
        assert!(validate_path(&path).is_some());
    }

    #[test]
    fn validate_path_rejects_null_bytes() {
        let mut bytes = b"/tmp/clauditor".to_vec();
        bytes.push(0);
        bytes.extend_from_slice(b"bad");
        let os = OsString::from_vec(bytes);
        let path = PathBuf::from(os);
        assert!(validate_path(&path).is_none());
    }

    #[test]
    fn dev_collector_uses_own_pid_uid() {
        let temp = tempfile::tempdir().unwrap();
        let file_path = temp.path().join("test.txt");
        
        let mut collector = DevCollector::new("sess-1", b"test-key".to_vec()).unwrap();
        collector.add_watch(temp.path()).unwrap();
        
        File::create(&file_path).unwrap();
        let events = collector.read_available().unwrap();
        
        // DevCollector should use its own pid/uid
        let our_pid = std::process::id();
        let our_uid = unsafe { libc::geteuid() as u32 };
        
        for event in &events {
            assert_eq!(event.event.pid, our_pid);
            assert_eq!(event.event.uid, our_uid);
        }
    }

    #[test]
    fn events_have_valid_hashes() {
        let temp = tempfile::tempdir().unwrap();
        let file_path = temp.path().join("test.txt");
        
        let key = b"test-key".to_vec();
        let mut collector = DevCollector::new("sess-1", key.clone()).unwrap();
        collector.add_watch(temp.path()).unwrap();
        
        // Create multiple events to test chain
        File::create(&file_path).unwrap();
        let events1 = collector.read_available().unwrap();
        
        std::fs::write(&file_path, "content").unwrap();
        let events2 = collector.read_available().unwrap();
        
        // Collect all events
        let all_events: Vec<_> = events1.into_iter()
            .chain(events2.into_iter())
            .map(|e| e.event)
            .collect();
        
        // Verify the chain
        if !all_events.is_empty() {
            schema::verify_chain(&all_events, &key).expect("chain should verify");
        }
    }
}
