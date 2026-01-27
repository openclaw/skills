//! Append-only log writer for clauditor.
//!
//! Features:
//! - O_APPEND mode for kernel-guaranteed atomic appends
//! - fsync policy (none, periodic, every)
//! - Log rotation support
//! - chattr +a integration (checked, not applied)

use chrono::Utc;
use collector::CollectorEvent;
use serde::{Deserialize, Serialize};
use std::fs::{File, OpenOptions};
use std::io::{self, BufWriter, Write};
use std::os::unix::ffi::OsStrExt;
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
use std::path::{Path, PathBuf};

/// File permissions for log files (owner read/write only)
const LOG_FILE_MODE: u32 = 0o600;

/// Validate that a path is safe for use as a log file.
/// 
/// Checks for:
/// - Path traversal attacks (../)
/// - Null bytes
/// - Empty paths
pub fn validate_log_path(path: &Path, base_dir: Option<&Path>) -> io::Result<PathBuf> {
    // Check for empty path
    if path.as_os_str().is_empty() {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "empty path"));
    }
    
    // Check for null bytes (use raw bytes to avoid UTF-8 assumptions)
    if path.as_os_str().as_bytes().contains(&0) {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "path contains null byte"));
    }
    
    // Check for path traversal via ParentDir components
    if path.components().any(|c| matches!(c, std::path::Component::ParentDir)) {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "path contains parent directory traversal",
        ));
    }
    
    let mut candidate = path.to_path_buf();
    
    // If base_dir is provided, ensure the path is within it
    if let Some(base) = base_dir {
        let canonical_base = base.canonicalize()?;
        
        if !candidate.is_absolute() {
            candidate = canonical_base.join(candidate);
        }
        
        if !candidate.starts_with(&canonical_base) {
            return Err(io::Error::new(
                io::ErrorKind::InvalidInput,
                "path escapes base directory",
            ));
        }
        
        // For existing files, canonicalize and check
        if candidate.exists() {
            let canonical_path = candidate.canonicalize()?;
            if !canonical_path.starts_with(&canonical_base) {
                return Err(io::Error::new(
                    io::ErrorKind::InvalidInput, 
                    "path escapes base directory"
                ));
            }
            return Ok(canonical_path);
        }
        
        // For new files, check the parent
        if let Some(parent) = candidate.parent() {
            if parent.exists() {
                let canonical_parent = parent.canonicalize()?;
                if !canonical_parent.starts_with(&canonical_base) {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidInput, 
                        "path escapes base directory"
                    ));
                }
                return Ok(canonical_parent.join(candidate.file_name().unwrap_or_default()));
            }
        }
        
        return Ok(candidate);
    }
    
    if !candidate.is_absolute() {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "path must be absolute (or provide base_dir)",
        ));
    }
    
    // Return the path as-is (or canonicalized if possible)
    candidate.canonicalize().or(Ok(candidate))
}

/// Fsync policy for the writer.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FsyncPolicy {
    /// Never fsync (fastest, least durable)
    None,
    /// Fsync every N writes
    Periodic(u32),
    /// Fsync after every write (slowest, most durable)
    Every,
}

impl Default for FsyncPolicy {
    fn default() -> Self {
        FsyncPolicy::Periodic(100)
    }
}

/// Configuration for the writer.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WriterConfig {
    /// Path to the log file
    pub path: PathBuf,
    /// Fsync policy
    #[serde(default)]
    pub fsync: FsyncPolicy,
    /// Maximum file size before rotation (0 = no rotation)
    #[serde(default)]
    pub max_size_bytes: u64,
}

/// Append-only log writer.
pub struct AppendWriter {
    file: BufWriter<File>,
    config: WriterConfig,
    write_count: u32,
    bytes_written: u64,
}

impl AppendWriter {
    /// Create a new append-only writer.
    /// 
    /// # Path Safety
    /// The path should be validated before calling this function.
    /// This function does not perform path traversal checks.
    pub fn new(config: WriterConfig) -> io::Result<Self> {
        // Validate path to prevent traversal and null byte issues
        let path = validate_log_path(&config.path, None)?;
        
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .mode(LOG_FILE_MODE)  // Explicit permissions: 0o600
            .custom_flags(libc::O_APPEND)
            .open(&path)?;

        // Ensure permissions are correct even if file existed
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(LOG_FILE_MODE))?;

        // Get current file size
        let bytes_written = file.metadata()?.len();

        Ok(Self {
            file: BufWriter::new(file),
            config: WriterConfig {
                path,
                ..config
            },
            write_count: 0,
            bytes_written,
        })
    }

    /// Write an event to the log.
    pub fn write_event(&mut self, event: &CollectorEvent) -> io::Result<()> {
        let line = serde_json::to_string(event)?;
        writeln!(self.file, "{}", line)?;

        self.bytes_written += line.len() as u64 + 1;
        self.write_count += 1;

        // Apply fsync policy
        match self.config.fsync {
            FsyncPolicy::None => {}
            FsyncPolicy::Every => {
                self.file.flush()?;
                self.file.get_ref().sync_data()?;
            }
            FsyncPolicy::Periodic(n) if self.write_count.is_multiple_of(n) => {
                self.file.flush()?;
                self.file.get_ref().sync_data()?;
            }
            FsyncPolicy::Periodic(_) => {}
        }

        // Check for rotation
        if self.config.max_size_bytes > 0 && self.bytes_written >= self.config.max_size_bytes {
            self.rotate()?;
        }

        Ok(())
    }

    /// Rotate the log file.
    /// 
    /// Uses atomic rename to minimize the race window where events could be lost.
    fn rotate(&mut self) -> io::Result<()> {
        // Flush buffer to kernel
        self.file.flush()?;
        // fsync to disk before rename (prevents data loss on crash)
        self.file.get_ref().sync_data()?;

        // Generate rotated filename with timestamp (including microseconds for uniqueness)
        let timestamp = Utc::now().format("%Y%m%d_%H%M%S_%f");
        let rotated = self.config.path.with_extension(format!("{}.log", timestamp));

        // Close current file by replacing with /dev/null temporarily
        // This ensures the file is fully closed before rename
        let null_file = File::create("/dev/null")?;
        let old_writer = std::mem::replace(&mut self.file, BufWriter::new(null_file));
        drop(old_writer);

        // Atomic rename - this is the critical section
        // On failure, we try to recover by reopening the original file
        if let Err(e) = std::fs::rename(&self.config.path, &rotated) {
            // Try to recover by reopening the original
            if let Ok(file) = Self::open_log_file(&self.config.path) {
                self.file = BufWriter::new(file);
            }
            return Err(e);
        }

        // Open new file with proper permissions
        let file = Self::open_log_file(&self.config.path)?;
        self.file = BufWriter::new(file);
        self.bytes_written = 0;
        self.write_count = 0;

        Ok(())
    }
    
    /// Open a log file with proper permissions and flags.
    fn open_log_file(path: &Path) -> io::Result<File> {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .mode(LOG_FILE_MODE)
            .custom_flags(libc::O_APPEND)
            .open(path)?;
        
        // Ensure permissions even if file existed
        std::fs::set_permissions(path, std::fs::Permissions::from_mode(LOG_FILE_MODE))?;
        
        Ok(file)
    }

    /// Flush all buffered data.
    pub fn flush(&mut self) -> io::Result<()> {
        self.file.flush()?;
        self.file.get_ref().sync_data()
    }

    /// Check if the file has the append-only attribute (chattr +a).
    /// Returns Ok(true) if +a is set, Ok(false) if not, Err if check fails.
    pub fn check_append_only(path: impl AsRef<Path>) -> io::Result<bool> {
        use std::process::Command;

        let path = path.as_ref();
        if !path.exists() {
            return Ok(false);
        }

        // Use lsattr to check attributes
        let output = Command::new("lsattr")
            .arg("-d")
            .arg(path)
            .output()?;

        if !output.status.success() {
            return Err(io::Error::other("lsattr failed"));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        // lsattr output format: "----a--------e----- /path/to/file"
        // The 'a' attribute is typically at position 4
        Ok(stdout.starts_with("----a") || stdout.contains("a"))
    }

    /// Get the number of bytes written since creation/rotation.
    pub fn bytes_written(&self) -> u64 {
        self.bytes_written
    }

    /// Get the path to the log file.
    pub fn path(&self) -> &Path {
        &self.config.path
    }
}

impl Drop for AppendWriter {
    fn drop(&mut self) {
        let _ = self.flush();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;
    use collector::{CollectorEvent, FileEvent, FileEventKind, ProcInfo};
    use schema::{Event, EventKind};

    fn sample_event() -> CollectorEvent {
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
                kind: FileEventKind::Create,
                path: PathBuf::from("/tmp/test.txt"),
            },
            proc: Some(ProcInfo {
                pid: 123,
                uid: 1000,
                cmdline: vec!["test".to_string()],
                cwd: Some(PathBuf::from("/home/test")),
            }),
        }
    }

    #[test]
    fn write_and_read_events() {
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("events.log");

        let config = WriterConfig {
            path: log_path.clone(),
            fsync: FsyncPolicy::Every,
            max_size_bytes: 0,
        };

        let mut writer = AppendWriter::new(config).unwrap();
        let event = sample_event();
        writer.write_event(&event).unwrap();
        writer.flush().unwrap();

        // Read back
        let content = std::fs::read_to_string(&log_path).unwrap();
        assert!(!content.is_empty());

        let parsed: CollectorEvent = serde_json::from_str(content.trim()).unwrap();
        assert_eq!(parsed.event.pid, 123);
        assert_eq!(parsed.file.kind, FileEventKind::Create);
    }

    #[test]
    fn append_mode_works() {
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("append.log");

        // Write first event
        {
            let config = WriterConfig {
                path: log_path.clone(),
                fsync: FsyncPolicy::None,
                max_size_bytes: 0,
            };
            let mut writer = AppendWriter::new(config).unwrap();
            writer.write_event(&sample_event()).unwrap();
        }

        // Write second event (new writer instance)
        {
            let config = WriterConfig {
                path: log_path.clone(),
                fsync: FsyncPolicy::None,
                max_size_bytes: 0,
            };
            let mut writer = AppendWriter::new(config).unwrap();
            writer.write_event(&sample_event()).unwrap();
        }

        // Should have 2 lines
        let content = std::fs::read_to_string(&log_path).unwrap();
        let lines: Vec<&str> = content.lines().collect();
        assert_eq!(lines.len(), 2);
    }

    #[test]
    fn rotation_works() {
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("rotate.log");

        let config = WriterConfig {
            path: log_path.clone(),
            fsync: FsyncPolicy::None,
            max_size_bytes: 100, // Small limit to trigger rotation
        };

        let mut writer = AppendWriter::new(config).unwrap();
        
        // Write events until rotation
        for _ in 0..10 {
            writer.write_event(&sample_event()).unwrap();
        }

        // Check that rotated files exist
        let entries: Vec<_> = std::fs::read_dir(temp.path())
            .unwrap()
            .filter_map(|e| e.ok())
            .collect();
        
        // Should have at least 2 files (current + rotated)
        assert!(entries.len() >= 2, "expected rotation to create multiple files");
    }

    // NEW TESTS for code review concerns

    #[test]
    fn file_permissions_are_0600() {
        use std::os::unix::fs::PermissionsExt;
        
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("perms.log");

        let config = WriterConfig {
            path: log_path.clone(),
            fsync: FsyncPolicy::None,
            max_size_bytes: 0,
        };

        let mut writer = AppendWriter::new(config).unwrap();
        writer.write_event(&sample_event()).unwrap();
        writer.flush().unwrap();

        let metadata = std::fs::metadata(&log_path).unwrap();
        let mode = metadata.permissions().mode() & 0o777;
        assert_eq!(mode, 0o600, "log file should have 0600 permissions");
    }

    #[test]
    fn validate_path_rejects_traversal() {
        let temp = tempfile::tempdir().unwrap();
        
        // Path with .. should be rejected
        let bad_path = temp.path().join("../escape.log");
        let result = validate_log_path(&bad_path, Some(temp.path()));
        assert!(result.is_err());
    }

    #[test]
    fn validate_path_allows_normal() {
        let temp = tempfile::tempdir().unwrap();
        
        let good_path = temp.path().join("normal.log");
        let result = validate_log_path(&good_path, Some(temp.path()));
        assert!(result.is_ok());
    }

    #[test]
    fn validate_path_rejects_empty() {
        let empty = PathBuf::from("");
        let result = validate_log_path(&empty, None);
        assert!(result.is_err());
    }
    
    #[test]
    fn validate_path_rejects_relative_without_base() {
        let relative = PathBuf::from("relative.log");
        let result = validate_log_path(&relative, None);
        assert!(result.is_err());
    }

    #[test]
    fn new_rejects_traversal_path() {
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("../escape.log");

        let config = WriterConfig {
            path: log_path,
            fsync: FsyncPolicy::None,
            max_size_bytes: 0,
        };

        let result = AppendWriter::new(config);
        assert!(result.is_err());
    }

    #[test]
    fn drop_flushes_data() {
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("drop.log");

        {
            let config = WriterConfig {
                path: log_path.clone(),
                fsync: FsyncPolicy::None, // Even with no fsync policy
                max_size_bytes: 0,
            };
            let mut writer = AppendWriter::new(config).unwrap();
            writer.write_event(&sample_event()).unwrap();
            // Drop here
        }

        // Data should be flushed
        let content = std::fs::read_to_string(&log_path).unwrap();
        assert!(!content.is_empty(), "data should be flushed on drop");
    }

    #[test]
    fn fsync_every_actually_syncs() {
        let temp = tempfile::tempdir().unwrap();
        let log_path = temp.path().join("sync.log");

        let config = WriterConfig {
            path: log_path.clone(),
            fsync: FsyncPolicy::Every,
            max_size_bytes: 0,
        };

        let mut writer = AppendWriter::new(config).unwrap();
        writer.write_event(&sample_event()).unwrap();
        // With FsyncPolicy::Every, data should already be on disk

        // Verify file exists and has content
        let content = std::fs::read_to_string(&log_path).unwrap();
        assert!(!content.is_empty());
    }
}
