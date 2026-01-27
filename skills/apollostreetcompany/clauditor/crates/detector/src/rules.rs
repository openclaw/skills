//! Default detection rules.

use regex::Regex;
use crate::{Category, FileOp, Severity};

/// Rule for exec events.
pub struct ExecRule {
    pub id: String,
    pub description: String,
    pub severity: Severity,
    pub category: Category,
    pub match_type: ExecMatch,
}

pub enum ExecMatch {
    /// Match on command name only.
    Command(Regex),
    /// Match on full argv string.
    Argv(Regex),
    /// Match on both command name and argv.
    CommandAndArgv { comm: Regex, argv: Regex },
}

/// Rule for file operations.
pub struct FileRule {
    pub id: String,
    pub description: String,
    pub severity: Severity,
    pub category: Category,
    pub ops: Vec<FileOp>,
    pub path_re: Regex,
}

/// Build default exec rules.
pub fn default_exec_rules() -> Vec<ExecRule> {
    vec![
        // === EXFIL ===
        ExecRule {
            id: "exfil-curl".to_string(),
            description: "curl execution (potential data exfiltration)".to_string(),
            severity: Severity::Medium,
            category: Category::Exfil,
            match_type: ExecMatch::Command(Regex::new(r"^curl$").unwrap()),
        },
        ExecRule {
            id: "exfil-wget".to_string(),
            description: "wget execution (potential data exfiltration)".to_string(),
            severity: Severity::Medium,
            category: Category::Exfil,
            match_type: ExecMatch::Command(Regex::new(r"^wget$").unwrap()),
        },
        ExecRule {
            id: "exfil-scp".to_string(),
            description: "scp execution (potential data exfiltration)".to_string(),
            severity: Severity::High,
            category: Category::Exfil,
            match_type: ExecMatch::Command(Regex::new(r"^scp$").unwrap()),
        },
        ExecRule {
            id: "exfil-rsync".to_string(),
            description: "rsync execution (potential data exfiltration)".to_string(),
            severity: Severity::Medium,
            category: Category::Exfil,
            match_type: ExecMatch::Command(Regex::new(r"^rsync$").unwrap()),
        },
        ExecRule {
            id: "exfil-nc".to_string(),
            description: "netcat execution (potential data exfiltration)".to_string(),
            severity: Severity::High,
            category: Category::Exfil,
            match_type: ExecMatch::Command(Regex::new(r"^(nc|ncat|netcat)$").unwrap()),
        },
        ExecRule {
            id: "exfil-ssh-outbound".to_string(),
            description: "ssh with data piping (potential exfil)".to_string(),
            severity: Severity::High,
            category: Category::Exfil,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^ssh$").unwrap(),
                argv: Regex::new(r"(cat|tar|zip|gzip)\s").unwrap(),
            },
        },

        // === CLAWDBOT-SPECIFIC EXFIL ===
        ExecRule {
            id: "exfil-gog-mail".to_string(),
            description: "gog mail command (email exfiltration)".to_string(),
            severity: Severity::Critical,
            category: Category::Exfil,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^gog$").unwrap(),
                argv: Regex::new(r"\bmail\s+(send|compose)").unwrap(),
            },
        },
        ExecRule {
            id: "exfil-himalaya".to_string(),
            description: "himalaya email client (email exfiltration)".to_string(),
            severity: Severity::Critical,
            category: Category::Exfil,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^himalaya$").unwrap(),
                argv: Regex::new(r"\b(send|write|reply|forward)").unwrap(),
            },
        },
        ExecRule {
            id: "exfil-wacli".to_string(),
            description: "wacli WhatsApp CLI (message exfiltration)".to_string(),
            severity: Severity::Critical,
            category: Category::Exfil,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^wacli$").unwrap(),
                argv: Regex::new(r"\b(send|message)").unwrap(),
            },
        },
        ExecRule {
            id: "exfil-bird".to_string(),
            description: "bird Twitter/X CLI (social media exfil)".to_string(),
            severity: Severity::High,
            category: Category::Exfil,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^bird$").unwrap(),
                argv: Regex::new(r"\b(post|tweet|send|dm)").unwrap(),
            },
        },

        // === INJECTION ===
        ExecRule {
            id: "inject-bash-c".to_string(),
            description: "bash -c execution (command injection risk)".to_string(),
            severity: Severity::Medium,
            category: Category::Injection,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^(bash|sh|zsh|dash)$").unwrap(),
                argv: Regex::new(r"\s-c\s").unwrap(),
            },
        },
        ExecRule {
            id: "inject-python-c".to_string(),
            description: "python -c execution (command injection risk)".to_string(),
            severity: Severity::Medium,
            category: Category::Injection,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^python[23]?$").unwrap(),
                argv: Regex::new(r"\s-c\s").unwrap(),
            },
        },
        ExecRule {
            id: "inject-base64-decode".to_string(),
            description: "base64 decode (potential obfuscated payload)".to_string(),
            severity: Severity::Medium,
            category: Category::Injection,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^base64$").unwrap(),
                argv: Regex::new(r"(-d|--decode)").unwrap(),
            },
        },
        ExecRule {
            id: "inject-eval".to_string(),
            description: "eval/exec in shell (dynamic code execution)".to_string(),
            severity: Severity::High,
            category: Category::Injection,
            match_type: ExecMatch::Argv(Regex::new(r"\beval\s|\bexec\s").unwrap()),
        },

        // === PERSISTENCE ===
        ExecRule {
            id: "persist-crontab".to_string(),
            description: "crontab modification".to_string(),
            severity: Severity::High,
            category: Category::Persistence,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^crontab$").unwrap(),
                argv: Regex::new(r"(-e|-r|-l|-)").unwrap(),
            },
        },
        ExecRule {
            id: "persist-systemctl-enable".to_string(),
            description: "systemctl enable (persistence mechanism)".to_string(),
            severity: Severity::High,
            category: Category::Persistence,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^systemctl$").unwrap(),
                argv: Regex::new(r"\benable\b").unwrap(),
            },
        },
        ExecRule {
            id: "persist-chmod-setuid".to_string(),
            description: "chmod with setuid/setgid (privilege escalation)".to_string(),
            severity: Severity::Critical,
            category: Category::Persistence,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^chmod$").unwrap(),
                argv: Regex::new(r"[ug]\+s|[4267][0-7]{3}").unwrap(),
            },
        },

        // === TAMPER ===
        ExecRule {
            id: "tamper-rm-rf".to_string(),
            description: "recursive forced removal".to_string(),
            severity: Severity::High,
            category: Category::Tamper,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^rm$").unwrap(),
                argv: Regex::new(r"-rf|-fr|--recursive.*--force|--force.*--recursive").unwrap(),
            },
        },
        ExecRule {
            id: "tamper-truncate".to_string(),
            description: "file truncation (log destruction)".to_string(),
            severity: Severity::High,
            category: Category::Tamper,
            match_type: ExecMatch::Command(Regex::new(r"^truncate$").unwrap()),
        },
        ExecRule {
            id: "tamper-chattr".to_string(),
            description: "chattr usage (attribute manipulation)".to_string(),
            severity: Severity::Critical,
            category: Category::Tamper,
            match_type: ExecMatch::Command(Regex::new(r"^chattr$").unwrap()),
        },
        ExecRule {
            id: "tamper-systemctl-stop".to_string(),
            description: "systemctl stop/disable (service disruption)".to_string(),
            severity: Severity::High,
            category: Category::Tamper,
            match_type: ExecMatch::CommandAndArgv {
                comm: Regex::new(r"^systemctl$").unwrap(),
                argv: Regex::new(r"\b(stop|disable)\b").unwrap(),
            },
        },
        ExecRule {
            id: "tamper-kill".to_string(),
            description: "kill signal to other processes".to_string(),
            severity: Severity::Medium,
            category: Category::Tamper,
            match_type: ExecMatch::Command(Regex::new(r"^(kill|pkill|killall)$").unwrap()),
        },
    ]
}

/// Build default file operation rules.
pub fn default_file_rules() -> Vec<FileRule> {
    vec![
        // === PERSISTENCE ===
        FileRule {
            id: "persist-ssh-keys".to_string(),
            description: "SSH authorized_keys modification".to_string(),
            severity: Severity::Critical,
            category: Category::Persistence,
            ops: vec![FileOp::Write, FileOp::Unlink, FileOp::Rename],
            path_re: Regex::new(r"\.ssh/authorized_keys").unwrap(),
        },
        FileRule {
            id: "persist-shell-rc".to_string(),
            description: "Shell RC file modification".to_string(),
            severity: Severity::High,
            category: Category::Persistence,
            ops: vec![FileOp::Write],
            path_re: Regex::new(r"\.(bash|zsh|profile|bashrc|zshrc|bash_profile)$").unwrap(),
        },
        FileRule {
            id: "persist-cron-files".to_string(),
            description: "Cron file modification".to_string(),
            severity: Severity::High,
            category: Category::Persistence,
            ops: vec![FileOp::Write, FileOp::Unlink],
            path_re: Regex::new(r"/etc/cron\.|/var/spool/cron").unwrap(),
        },
        FileRule {
            id: "persist-systemd-units".to_string(),
            description: "Systemd unit file modification".to_string(),
            severity: Severity::High,
            category: Category::Persistence,
            ops: vec![FileOp::Write, FileOp::Unlink],
            path_re: Regex::new(r"/etc/systemd/|\.config/systemd/|/lib/systemd/").unwrap(),
        },

        // === TAMPER ===
        FileRule {
            id: "tamper-log-deletion".to_string(),
            description: "Log file deletion".to_string(),
            severity: Severity::Critical,
            category: Category::Tamper,
            ops: vec![FileOp::Unlink],
            path_re: Regex::new(r"/var/log/|\.log$").unwrap(),
        },
        FileRule {
            id: "tamper-audit-dir".to_string(),
            description: "Audit directory access".to_string(),
            severity: Severity::Critical,
            category: Category::Tamper,
            ops: vec![FileOp::Write, FileOp::Unlink, FileOp::Rename],
            path_re: Regex::new(r"/var/lib/clauditor/|/var/lib/\.sysd/\.audit/").unwrap(),
        },
        FileRule {
            id: "tamper-history".to_string(),
            description: "Shell history manipulation".to_string(),
            severity: Severity::High,
            category: Category::Tamper,
            ops: vec![FileOp::Write, FileOp::Unlink],
            path_re: Regex::new(r"\.(bash_history|zsh_history|history)$").unwrap(),
        },

        // === INJECTION ===
        FileRule {
            id: "inject-script-write".to_string(),
            description: "Executable script creation".to_string(),
            severity: Severity::Medium,
            category: Category::Injection,
            ops: vec![FileOp::Write],
            path_re: Regex::new(r"\.(sh|py|pl|rb)$").unwrap(),
        },
    ]
}
