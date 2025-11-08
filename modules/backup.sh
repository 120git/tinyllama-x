#!/usr/bin/env bash
# backup.sh - Backup module (stub/MVP)

# Main backup function
run_backup() {
    local target="${1:-}"
    local backup_type="${2:-full}"
    
    log_info "backup" "Backup module (MVP stub)"
    
    if [[ -z "$target" ]]; then
        log_error "backup" "Backup target not specified. Use --target /path/to/backup"
        return 1
    fi
    
    log_info "backup" "Backup strategy: rsync/tar to $target"
    log_info "backup" "Backup type: $backup_type"
    
    if [[ "$DRY_RUN" != "true" ]]; then
        log_warn "backup" "Backup module is currently in dry-run only mode (MVP)"
        log_info "backup" "Would backup the following:"
        echo "  - /etc (system configuration)" >&2
        echo "  - /home (user data)" >&2
        echo "  - /var/lib/ubopt (ubopt state)" >&2
        echo ""
        echo "Target: $target" >&2
        echo "Strategy: rsync with --archive --compress" >&2
        return 0
    fi
    
    log_info "backup" "DRY-RUN: Would execute backup with rsync:"
    cat >&2 <<EOF
  rsync -avz --delete \\
    --exclude='/home/*/.cache' \\
    --exclude='/home/*/tmp' \\
    /etc/ \\
    /home/ \\
    /var/lib/ubopt/ \\
    $target/
EOF
    
    log_info "backup" "Backup completed (dry-run)"
    return 0
}

# Export function for module
backup_module() {
    run_backup "$@"
}
