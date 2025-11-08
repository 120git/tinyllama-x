#!/usr/bin/env bash
# common.sh - Shared helper functions for ubopt

set -Eeuo pipefail

# Version
UBOPT_VERSION="0.1.0"

# Colors for output (disabled if NO_COLOR or non-interactive)
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]] && [[ -z "${UBOPT_NO_COLOR:-}" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Global flags
DRY_RUN="${UBOPT_DRY_RUN:-false}"
JSON_OUTPUT="${UBOPT_JSON_OUTPUT:-false}"
HEADLESS="${UBOPT_HEADLESS:-false}"
VERBOSE="${UBOPT_VERBOSE:-0}"
# LOG_LEVEL is read from env but not actively used in current implementation
# shellcheck disable=SC2034
LOG_LEVEL="${UBOPT_LOG_LEVEL:-info}"

# Detect OS and package manager
detect_os() {
    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        source /etc/os-release
        echo "${ID:-unknown}"
    else
        echo "unknown"
    fi
}

# Detect package manager
detect_package_manager() {
    local os
    os=$(detect_os)
    
    case "$os" in
        ubuntu|debian|linuxmint|pop)
            echo "apt"
            ;;
        fedora|rhel|centos|rocky|almalinux)
            echo "dnf"
            ;;
        arch|manjaro|endeavouros)
            echo "pacman"
            ;;
        *)
            # Fallback: check for available commands
            if command -v apt-get &> /dev/null; then
                echo "apt"
            elif command -v dnf &> /dev/null; then
                echo "dnf"
            elif command -v pacman &> /dev/null; then
                echo "pacman"
            else
                echo "unknown"
            fi
            ;;
    esac
}

# Check if running as root
require_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "common" "This operation requires root privileges. Please run with sudo."
        exit 1
    fi
}

# Confirm operation in dry-run mode
confirm_dry_run() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "common" "DRY-RUN mode: would execute: $*"
        return 0
    fi
    return 1
}

# Prompt for confirmation unless headless
confirm() {
    local prompt="${1:-Are you sure?}"
    
    if [[ "$HEADLESS" == "true" ]]; then
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "common" "DRY-RUN: would prompt: $prompt"
        return 0
    fi
    
    echo -ne "${YELLOW}${prompt} [y/N] ${NC}" >&2
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# JSON log function
json_log() {
    local level="$1"
    local module="$2"
    local message="$3"
    local fields="${4:-{}}"
    
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        local timestamp
        timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        # Build JSON object
        local json
        json=$(jq -n \
            --arg ts "$timestamp" \
            --arg lvl "$level" \
            --arg mod "$module" \
            --arg msg "$message" \
            --argjson flds "$fields" \
            '{
                timestamp: $ts,
                level: $lvl,
                module: $mod,
                message: $msg,
                fields: $flds
            }')
        echo "$json"
    fi
}

# Convenience logging functions
log_info() {
    local module="$1"
    local message="$2"
    local fields="${3:-{}}"
    
    json_log "INFO" "$module" "$message" "$fields"
    
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${GREEN}[INFO]${NC} $message" >&2
    fi
}

log_warn() {
    local module="$1"
    local message="$2"
    local fields="${3:-{}}"
    
    json_log "WARN" "$module" "$message" "$fields"
    
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${YELLOW}[WARN]${NC} $message" >&2
    fi
}

log_error() {
    local module="$1"
    local message="$2"
    local fields="${3:-{}}"
    
    json_log "ERROR" "$module" "$message" "$fields"
    
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${RED}[ERROR]${NC} $message" >&2
    fi
}

log_debug() {
    local module="$1"
    local message="$2"
    local fields="${3:-{}}"
    
    if [[ "$VERBOSE" -ge 1 ]]; then
        json_log "DEBUG" "$module" "$message" "$fields"
        
        if [[ "$JSON_OUTPUT" != "true" ]]; then
            echo -e "${BLUE}[DEBUG]${NC} $message" >&2
        fi
    fi
}

# Run command safely with logging
run_safely() {
    local description="$1"
    shift
    
    if confirm_dry_run "$@"; then
        return 0
    fi
    
    log_debug "common" "Executing: $*"
    
    if "$@"; then
        log_debug "common" "$description: success"
        return 0
    else
        local exit_code=$?
        log_error "common" "$description: failed with exit code $exit_code"
        return $exit_code
    fi
}

# Cleanup function for trap
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_warn "common" "Exiting with code $exit_code"
    fi
}

# Set up trap for cleanup
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Simple spinner for long operations
spinner() {
    local pid=$1
    local message="${2:-Working...}"
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    
    if [[ "$JSON_OUTPUT" == "true" ]] || [[ ! -t 1 ]]; then
        # No spinner in JSON mode or non-interactive
        wait "$pid"
        return $?
    fi
    
    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i+1) % 10 ))
        printf "\r${BLUE}%s${NC} %s" "${spin:$i:1}" "$message" >&2
        sleep 0.1
    done
    
    printf "\r%*s\r" $((${#message} + 3)) "" >&2
    wait "$pid"
    return $?
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if package is installed (generic)
package_installed() {
    local package="$1"
    local pm
    pm=$(detect_package_manager)
    
    case "$pm" in
        apt)
            dpkg -l "$package" 2>/dev/null | grep -q "^ii"
            ;;
        dnf)
            rpm -q "$package" &>/dev/null
            ;;
        pacman)
            pacman -Q "$package" &>/dev/null
            ;;
        *)
            return 1
            ;;
    esac
}

# Get version string
version() {
    echo "ubopt version $UBOPT_VERSION"
}

# Load provider
load_provider() {
    local pm
    pm=$(detect_package_manager)
    
    if [[ "$pm" == "unknown" ]]; then
        log_error "common" "Unable to detect package manager"
        return 1
    fi
    
    # Try multiple paths for provider
    local provider_path=""
    for path in \
        "$(dirname "${BASH_SOURCE[0]}")/../providers/${pm}.sh" \
        "/usr/local/share/ubopt/providers/${pm}.sh" \
        "${PROVIDERS_DIR:-}/${pm}.sh"; do
        if [[ -f "$path" ]]; then
            provider_path="$path"
            break
        fi
    done
    
    if [[ -z "$provider_path" ]]; then
        log_error "common" "Provider not found for: $pm"
        return 1
    fi
    
    # shellcheck source=/dev/null
    source "$provider_path"
    log_debug "common" "Loaded provider: $pm"
}

# Parse YAML config (simple key=value extraction)
parse_config() {
    local config_file="$1"
    local key="$2"
    
    if [[ ! -f "$config_file" ]]; then
        return 1
    fi
    
    # Simple YAML parsing - extracts key: value pairs
    # For complex YAML, would need yq or python
    grep "^[[:space:]]*${key}:" "$config_file" | sed 's/^[[:space:]]*[^:]*:[[:space:]]*//' | sed 's/[[:space:]]*$//'
}

# Get config file path
get_config_path() {
    if [[ -n "${UBOPT_CONFIG:-}" ]]; then
        echo "$UBOPT_CONFIG"
    elif [[ $EUID -eq 0 ]]; then
        echo "/etc/ubopt/ubopt.yaml"
    else
        echo "${HOME}/.config/ubopt/ubopt.yaml"
    fi
}

# Ensure directory exists
ensure_dir() {
    local dir="$1"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_debug "common" "DRY-RUN: would create directory $dir"
        return 0
    fi
    
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || {
            log_error "common" "Failed to create directory: $dir"
            return 1
        }
        log_debug "common" "Created directory: $dir"
    fi
}

# Write state file
write_state() {
    local state_file="$1"
    local state_data="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_debug "common" "DRY-RUN: would write state to $state_file"
        return 0
    fi
    
    local state_dir
    state_dir=$(dirname "$state_file")
    ensure_dir "$state_dir"
    
    echo "$state_data" > "$state_file" || {
        log_error "common" "Failed to write state file: $state_file"
        return 1
    }
    
    log_debug "common" "Wrote state to: $state_file"
}

# Read state file
read_state() {
    local state_file="$1"
    
    if [[ -f "$state_file" ]]; then
        cat "$state_file"
    else
        echo "{}"
    fi
}
