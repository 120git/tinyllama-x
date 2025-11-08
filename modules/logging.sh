#!/usr/bin/env bash
#
# Logging module - View and manage logs
#

show_logs() {
    local logfile="${UBOPT_LOGFILE:-/var/log/ubopt.log}"
    local lines="${1:-50}"
    
    log_info "Showing ubopt logs (last $lines lines)..."
    
    if [[ ! -f "$logfile" ]]; then
        log_info "No log file found at $logfile"
        return 0
    fi
    
    if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
        echo "{\"logfile\":\"$logfile\",\"entries\":["
        tail -n "$lines" "$logfile" | while IFS= read -r line; do
            # Escape quotes in JSON
            line="${line//\"/\\\"}"
            echo "\"$line\","
        done | sed '$ s/,$//'
        echo "]}"
    else
        echo "=== ubopt logs (last $lines lines) ==="
        tail -n "$lines" "$logfile"
    fi
}
