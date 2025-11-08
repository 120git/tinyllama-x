#!/usr/bin/env bash
#
# Common utility functions for ubopt
#

# Check if running as root
is_root() {
    [[ $EUID -eq 0 ]]
}

# Require root privileges
require_root() {
    if ! is_root; then
        echo "[ERROR] This command requires root privileges. Use sudo." >&2
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Safe execution wrapper
safe_exec() {
    local cmd="$*"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        echo "[DRY-RUN] Would execute: $cmd"
        return 0
    fi
    
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        echo "[EXEC] $cmd"
    fi
    
    eval "$cmd"
}

# JSON output helper
output_json() {
    local key="$1"
    local value="$2"
    
    if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
        echo "{\"$key\":\"$value\"}"
    fi
}

# Get timestamp
get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Log to file
log_to_file() {
    local message="$1"
    local logfile="${UBOPT_LOGFILE:-/var/log/ubopt.log}"
    
    if [[ -w "$(dirname "$logfile")" ]]; then
        echo "[$(get_timestamp)] $message" >> "$logfile"
    fi
}
