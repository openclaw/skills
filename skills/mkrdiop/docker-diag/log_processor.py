import sys
import argparse
import collections

# Keywords to flag as high-signal
ERROR_KEYWORDS = ["ERROR", "EXCEPTION", "FAILED", "CRITICAL", "PANIC", "FATAL", "500"]

def process_logs(container_name, max_lines=1000, context_size=5):
    import subprocess
    
    # 1. Fetch the logs using shell
    try:
        cmd = f"docker logs --tail {max_lines} {container_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        lines = result.stderr.splitlines() + result.stdout.splitlines() # Docker logs often hit stderr
    except Exception as e:
        return f"Error fetching logs: {str(e)}"

    # 2. Extract Signal
    buffer = collections.deque(maxlen=context_size) # Keeps track of "pre-error" context
    findings = []
    seen_errors = set()

    for line in lines:
        upper_line = line.upper()
        if any(key in upper_line for key in ERROR_KEYWORDS):
            # Only record if we haven't seen this exact error recently (deduplication)
            error_id = line[-50:] # Use last 50 chars as a fuzzy ID
            if error_id not in seen_errors:
                findings.append("--- CONTEXT ---")
                findings.extend(list(buffer))
                findings.append(f"👉 {line}")
                seen_errors.add(error_id)
        buffer.append(line)

    if not findings:
        return "No clear errors found in the last 1000 lines. The container seems healthy."

    return "\n".join(findings[:50]) # Limit to 50 lines total for AI efficiency

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("container")
    args = parser.parse_args()
    print(process_logs(args.container))