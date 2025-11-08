#!/usr/bin/env bash
# logging.sh - Logging module

# Initialize logging
init_logging() {
    local log_dir="${1:-/var/log/ubopt}"
    local log_file="${2:-ubopt.log}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_debug "logging" "DRY-RUN: Would initialize logging to $log_dir/$log_file"
        return 0
    fi
    
    # Create log directory
    ensure_dir "$log_dir"
    
    # Set permissions
    if [[ $EUID -eq 0 ]]; then
        chmod 750 "$log_dir"
        chown root:adm "$log_dir" 2>/dev/null || true
    fi
    
    log_debug "logging" "Logging initialized: $log_dir/$log_file"
}

# Write log entry to file
write_log() {
    local log_file="${1:-/var/log/ubopt/ubopt.log}"
    local level="$2"
    local module="$3"
    local message="$4"
    local fields="${5:-{}}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    local log_entry
    log_entry=$(jq -n \
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
    
    echo "$log_entry" >> "$log_file"
}

# Generate logrotate configuration
generate_logrotate_config() {
    local output_file="${1:-/tmp/ubopt.logrotate}"
    
    cat > "$output_file" <<'EOF'
/var/log/ubopt/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        # Reload or restart services if needed
    endscript
}
EOF
    
    log_info "logging" "Logrotate configuration generated: $output_file"
}

# Export functions
logging_module() {
    generate_logrotate_config "$@"
}
