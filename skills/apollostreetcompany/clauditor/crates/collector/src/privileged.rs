//! Privileged collector using fanotify for file operations.
//! Requires CAP_SYS_ADMIN or root.

use crate::{CollectorEvent, FileEvent, FileEventKind, ProcInfo};
use chrono::Utc;
use schema::{Event, EventKind};
use std::collections::HashSet;
use std::ffi::CString;
use std::io;
use std::os::unix::io::{AsRawFd, FromRawFd, OwnedFd};
use std::path::{Path, PathBuf};

// fanotify constants (from linux headers)
const FAN_CLASS_NOTIF: libc::c_uint = 0x00;  // Notification only (non-blocking)
#[allow(dead_code)]
const FAN_CLASS_CONTENT: libc::c_uint = 0x04;  // Permission decisions (we don't use this)
const FAN_UNLIMITED_QUEUE: libc::c_uint = 0x10;
const FAN_UNLIMITED_MARKS: libc::c_uint = 0x20;
const FAN_CLOEXEC: libc::c_uint = 0x01;

const FAN_MARK_ADD: libc::c_uint = 0x01;
#[allow(dead_code)]
const FAN_MARK_MOUNT: libc::c_uint = 0x10;
// FAN_MARK_FILESYSTEM (Linux 4.20+) marks the entire filesystem, not just a mount.
// This is crucial when running in a mount namespace (e.g., with ProtectSystem=strict)
// because FAN_MARK_MOUNT would only mark the mount as seen from inside the namespace,
// missing events from processes in the parent namespace.
const FAN_MARK_FILESYSTEM: libc::c_uint = 0x100;

const FAN_OPEN: u64 = 0x20;
const FAN_CLOSE_WRITE: u64 = 0x08;
const FAN_CLOSE_NOWRITE: u64 = 0x10;
#[allow(dead_code)] // Reserved for future use in event monitoring
const FAN_CLOSE: u64 = FAN_CLOSE_WRITE | FAN_CLOSE_NOWRITE;
const FAN_OPEN_EXEC: u64 = 0x00001000;
const FAN_CREATE: u64 = 0x100;
const FAN_DELETE: u64 = 0x200;
const FAN_MOVED_FROM: u64 = 0x40000000;
const FAN_MOVED_TO: u64 = 0x80000000;

const AT_FDCWD: libc::c_int = -100;

/// Event metadata from fanotify
#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct FanotifyEventMetadata {
    event_len: u32,
    vers: u8,
    reserved: u8,
    metadata_len: u16,
    mask: u64,
    fd: i32,
    pid: i32,
}

/// Privileged collector using fanotify.
/// Only captures events for processes owned by `target_uid`.
pub struct PrivilegedCollector {
    fd: OwnedFd,
    buffer: Vec<u8>,
    session_id: String,
    key: Vec<u8>,
    last_event: Option<Event>,
    target_uid: u32,
    watch_paths: HashSet<PathBuf>,
    exec_watchlist: HashSet<String>,
}

impl PrivilegedCollector {
    /// Create a new privileged collector.
    /// Requires CAP_SYS_ADMIN.
    pub fn new(
        session_id: impl Into<String>,
        key: Vec<u8>,
        target_uid: u32,
    ) -> io::Result<Self> {
        // Use FAN_CLASS_NOTIF for pure monitoring (non-blocking)
        // FAN_CLASS_CONTENT would require responding to permission requests
        let flags = FAN_CLASS_NOTIF | FAN_UNLIMITED_QUEUE | FAN_UNLIMITED_MARKS | FAN_CLOEXEC;
        let event_flags = libc::O_RDONLY | libc::O_LARGEFILE;

        let fd = unsafe { libc::fanotify_init(flags, event_flags as u32) };
        if fd < 0 {
            return Err(io::Error::last_os_error());
        }

        let fd = unsafe { OwnedFd::from_raw_fd(fd) };

        Ok(Self {
            fd,
            buffer: vec![0u8; 8192],
            session_id: session_id.into(),
            key,
            last_event: None,
            target_uid,
            watch_paths: HashSet::new(),
            exec_watchlist: HashSet::new(),
        })
    }

    /// Add a path to watch (marks the entire filesystem containing the path).
    pub fn add_watch(&mut self, path: impl AsRef<Path>) -> io::Result<()> {
        let path = path.as_ref().to_path_buf();
        let c_path = CString::new(path.to_str().unwrap_or("")).map_err(|_| {
            io::Error::new(io::ErrorKind::InvalidInput, "invalid path")
        })?;

        // Exec-only mode: Much lower event volume, focused on what matters most.
        // FAN_OPEN_EXEC captures when executables are opened for execution.
        // This catches command execution which is the primary attack vector.
        let mask = FAN_OPEN_EXEC;
        // Use FAN_MARK_FILESYSTEM instead of FAN_MARK_MOUNT.
        // FAN_MARK_MOUNT only marks the specific mount point as seen from the current
        // mount namespace. When running with ProtectSystem=strict, this namespace is
        // isolated from the host, causing events from host processes to be missed.
        // FAN_MARK_FILESYSTEM marks the entire filesystem at the kernel level,
        // ensuring events are captured regardless of namespace boundaries.
        let flags = FAN_MARK_ADD | FAN_MARK_FILESYSTEM;

        eprintln!(
            "fanotify_mark: path={:?} flags={:#x} mask={:#x}",
            path, flags, mask
        );

        let ret = unsafe {
            libc::fanotify_mark(
                self.fd.as_raw_fd(),
                flags,
                mask,
                AT_FDCWD,
                c_path.as_ptr(),
            )
        };

        if ret < 0 {
            let err = io::Error::last_os_error();
            eprintln!(
                "fanotify_mark FAILED: path={:?} error={} (errno={})",
                path,
                err,
                err.raw_os_error().unwrap_or(-1)
            );
            return Err(err);
        }

        eprintln!("fanotify_mark OK: path={:?}", path);
        self.watch_paths.insert(path);
        Ok(())
    }

    /// Set the list of binary names to watch for exec events.
    /// If empty, all exec events pass through (debug mode).
    /// If non-empty, only binaries in the watchlist generate events.
    pub fn set_exec_watchlist(&mut self, binaries: Vec<String>) {
        self.exec_watchlist = binaries.into_iter().collect();
    }

    /// Read available events (blocking).
    pub fn read_available(&mut self) -> io::Result<Vec<CollectorEvent>> {
        let mut output = Vec::new();

        let n = unsafe {
            libc::read(
                self.fd.as_raw_fd(),
                self.buffer.as_mut_ptr() as *mut libc::c_void,
                self.buffer.len(),
            )
        };

        if n < 0 {
            let err = io::Error::last_os_error();
            eprintln!(
                "fanotify read FAILED: error={} (errno={})",
                err,
                err.raw_os_error().unwrap_or(-1)
            );
            return Err(err);
        }

        let mut offset = 0usize;
        while offset + std::mem::size_of::<FanotifyEventMetadata>() <= n as usize {
            let meta = unsafe {
                std::ptr::read(
                    self.buffer.as_ptr().add(offset) as *const FanotifyEventMetadata
                )
            };

            if meta.event_len == 0 {
                break;
            }

            // Read process info and filter by UID
            let proc_info = ProcInfo::from_pid(meta.pid as u32);
            let uid = proc_info.as_ref().map(|p| p.uid);

            // Filter by UID - but handle case where process already exited
            // If we can't determine UID, we must skip (can't verify it's our target user)
            let uid = match uid {
                Some(u) => u,
                None => {
                    // Process exited before we could check UID - skip silently
                    if meta.fd >= 0 {
                        unsafe { libc::close(meta.fd) };
                    }
                    offset += meta.event_len as usize;
                    continue;
                }
            };

            // Only process events from target UID
            if uid != self.target_uid {
                // Not our target user - skip silently
                if meta.fd >= 0 {
                    unsafe { libc::close(meta.fd) };
                }
                offset += meta.event_len as usize;
                continue;
            }

            // Process events from target UID
            {
                // Get the path from /proc/self/fd/N
                let path = if meta.fd >= 0 {
                    let fd_path = format!("/proc/self/fd/{}", meta.fd);
                    std::fs::read_link(&fd_path).ok()
                } else {
                    None
                };

                if let Some(path) = path {
                    if let Some(kind) = mask_to_kind(meta.mask) {
                        // Filter exec events by watchlist
                        if kind == FileEventKind::Exec && !self.exec_watchlist.is_empty() {
                            let binary_name = path
                                .file_name()
                                .map(|s| s.to_string_lossy().to_string());
                            if let Some(name) = binary_name {
                                if !self.exec_watchlist.contains(&name) {
                                    // Binary not in watchlist, skip this event
                                    offset += meta.event_len as usize;
                                    continue;
                                }
                            }
                        }

                        let timestamp = Utc::now();
                        let pid = meta.pid as u32;

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
                            proc: proc_info.clone(),
                        });
                    }
                }
            }

            // Close the event fd
            if meta.fd >= 0 {
                unsafe { libc::close(meta.fd) };
            }

            offset += meta.event_len as usize;
        }

        Ok(output)
    }

    /// Check if fanotify is available on this system.
    /// Returns (available, error_if_any) for diagnostics.
    pub fn is_available() -> bool {
        let fd = unsafe {
            libc::fanotify_init(FAN_CLASS_NOTIF | FAN_CLOEXEC, libc::O_RDONLY as u32)
        };
        if fd >= 0 {
            unsafe { libc::close(fd) };
            eprintln!("fanotify_init probe succeeded");
            true
        } else {
            let err = std::io::Error::last_os_error();
            eprintln!("fanotify_init probe failed: {} (errno={})", err, err.raw_os_error().unwrap_or(-1));
            false
        }
    }
}

fn mask_to_kind(mask: u64) -> Option<FileEventKind> {
    // Check FAN_OPEN_EXEC first - when an executable is opened for execution
    if mask & FAN_OPEN_EXEC != 0 {
        return Some(FileEventKind::Exec);
    }
    if mask & FAN_CREATE != 0 || mask & FAN_MOVED_TO != 0 {
        return Some(FileEventKind::Create);
    }
    if mask & FAN_DELETE != 0 || mask & FAN_MOVED_FROM != 0 {
        return Some(FileEventKind::Delete);
    }
    if mask & FAN_CLOSE_WRITE != 0 {
        return Some(FileEventKind::Modify);
    }
    // FAN_OPEN or FAN_CLOSE_NOWRITE = file was accessed but not modified
    if mask & FAN_OPEN != 0 || mask & FAN_CLOSE_NOWRITE != 0 {
        return Some(FileEventKind::Access);
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn check_fanotify_availability() {
        // This test just checks if fanotify is supported
        // It may fail without CAP_SYS_ADMIN, which is expected
        let available = PrivilegedCollector::is_available();
        println!("fanotify available: {available}");
    }
}
