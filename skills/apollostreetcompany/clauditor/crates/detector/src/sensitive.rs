//! Sensitive path detection for prompt injection defense.

/// Check if a path is sensitive (credentials, keys, secrets)
pub fn is_sensitive_path(path: &str) -> bool {
    // All patterns are lowercase for case-insensitive matching
    let sensitive_patterns = [
        "/.ssh/",
        "/id_rsa",
        "/id_ed25519",
        "/.gnupg/",
        "/.aws/credentials",
        "/.config/gog/",
        "/.config/himalaya/",
        "/memory.md",
        "/.clawdbot/",
        "/.env",
        "/secrets",
        "/credentials",
        "/api_key",
        "/token",
    ];
    
    let path_lower = path.to_lowercase();
    sensitive_patterns.iter().any(|p| path_lower.contains(p))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ssh_key_is_sensitive() {
        assert!(is_sensitive_path("/home/user/.ssh/id_rsa"));
        assert!(is_sensitive_path("/home/user/.ssh/id_ed25519"));
    }

    #[test]
    fn test_memory_is_sensitive() {
        assert!(is_sensitive_path("/home/user/clawd/MEMORY.md"));
    }

    #[test]
    fn test_clawdbot_config_is_sensitive() {
        assert!(is_sensitive_path("/home/user/.clawdbot/clawdbot.json"));
    }

    #[test]
    fn test_normal_file_not_sensitive() {
        assert!(!is_sensitive_path("/usr/lib/libc.so.6"));
        assert!(!is_sensitive_path("/home/user/readme.txt"));
        assert!(!is_sensitive_path("/tmp/test.txt"));
    }

    #[test]
    fn test_env_files_sensitive() {
        assert!(is_sensitive_path("/home/user/project/.env"));
        assert!(is_sensitive_path("/app/.env.local"));
    }
}
