#!/usr/bin/env bash
#
# Backup module - System backup utilities
#

run_backup() {
    local backup_dir="${1:-/var/backups/ubopt}"
    
    log_info "Starting system backup to $backup_dir..."
    
    # Require root for backup
    require_root
    
    # Create backup directory
    if [[ ! -d "$backup_dir" ]]; then
        if [[ "${DRY_RUN:-false}" == "true" ]]; then
            log_info "[DRY-RUN] Would create directory: $backup_dir"
        else
            mkdir -p "$backup_dir"
            log_info "Created backup directory: $backup_dir"
        fi
    fi
    
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/system_backup_$timestamp.tar.gz"
    
    # Define what to backup
    local backup_paths=(
        "/etc"
        "/root/.ssh"
        "/home/*/.ssh"
    )
    
    log_info "Backing up system configuration..."
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY-RUN] Would create backup: $backup_file"
        log_info "[DRY-RUN] Would backup: ${backup_paths[*]}"
    else
        # Create tar archive
        local tar_cmd="tar -czf $backup_file"
        for path in "${backup_paths[@]}"; do
            if [[ -e $path ]]; then
                tar_cmd="$tar_cmd $path"
            fi
        done
        
        eval "$tar_cmd" 2>/dev/null || true
        
        if [[ -f "$backup_file" ]]; then
            local backup_size
            backup_size=$(du -h "$backup_file" | cut -f1)
            log_success "Backup created: $backup_file ($backup_size)"
            
            if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
                echo "{\"backup_file\":\"$backup_file\",\"size\":\"$backup_size\"}"
            fi
        else
            log_error "Backup failed"
            return 1
        fi
    fi
    
    # Clean old backups (keep last 5)
    log_info "Cleaning old backups..."
    if [[ "${DRY_RUN:-false}" == "false" ]]; then
        local backup_count
        backup_count=$(find "$backup_dir" -name "system_backup_*.tar.gz" | wc -l)
        
        if [[ $backup_count -gt 5 ]]; then
            find "$backup_dir" -name "system_backup_*.tar.gz" -type f -printf '%T+ %p\n' | \
                sort | head -n -5 | cut -d' ' -f2- | xargs rm -f
            log_info "Removed old backups (kept last 5)"
        fi
    fi
    
    log_to_file "Backup completed: $backup_file"
}
