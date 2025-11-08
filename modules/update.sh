#!/usr/bin/env bash
# update.sh - System update module

# Main update function
run_update() {
    local security_only="${1:-false}"
    local reboot_if_required="${2:-false}"
    local no_reboot="${3:-false}"
    
    require_root
    load_provider
    
    log_info "update" "Starting system update"
    
    # State file
    local state_dir="/var/lib/ubopt"
    local state_file="$state_dir/state.json"
    
    ensure_dir "$state_dir"
    
    # Step 1: Update package metadata
    if ! pkg_update; then
        log_error "update" "Failed to update package metadata"
        return 1
    fi
    
    # Step 2: Check for security updates
    local has_security_updates=false
    if security_updates_available; then
        has_security_updates=true
    fi
    
    # Step 3: Check if any updates available
    local updates_available
    updates_available=$(list_security_updates 2>/dev/null | wc -l || echo "0")
    
    if [[ "$updates_available" -eq 0 ]]; then
        log_info "update" "No updates available"
        
        # Write state
        local state
        state=$(jq -n \
            --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
            --arg status "up-to-date" \
            '{
                last_update: $ts,
                status: $status,
                updates_available: 0,
                security_updates: 0
            }')
        write_state "$state_file" "$state"
        
        return 2
    fi
    
    log_info "update" "Updates available: $updates_available"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "update" "DRY-RUN: Would install the following updates:"
        list_security_updates | while read -r pkg; do
            echo "  - $pkg" >&2
        done
        return 0
    fi
    
    # Step 4: Confirm update
    if ! confirm "Apply $updates_available update(s)?"; then
        log_info "update" "Update cancelled by user"
        return 0
    fi
    
    # Step 5: Apply updates
    if ! pkg_upgrade "$security_only"; then
        log_error "update" "Failed to apply updates"
        return 1
    fi
    
    log_info "update" "Updates applied successfully"
    
    # Step 6: Clean cache
    pkg_clean || log_warn "update" "Failed to clean package cache"
    
    # Step 7: Check if reboot required
    local needs_reboot=false
    if reboot_required; then
        needs_reboot=true
        log_warn "update" "System reboot required"
        
        if [[ "$no_reboot" == "true" ]]; then
            log_info "update" "Skipping reboot (--no-reboot specified)"
        elif [[ "$reboot_if_required" == "true" ]]; then
            if [[ "$HEADLESS" == "true" ]]; then
                log_info "update" "Scheduling reboot in 5 minutes"
                shutdown -r +5 "System reboot required after updates" &
            else
                if confirm "Reboot now?"; then
                    log_info "update" "Rebooting system"
                    shutdown -r now "System reboot after updates"
                else
                    log_info "update" "Reboot postponed"
                fi
            fi
        fi
    fi
    
    # Step 8: Write state
    local state
    state=$(jq -n \
        --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        --arg status "updated" \
        --argjson updated "$updates_available" \
        --argjson needs_reboot "$needs_reboot" \
        '{
            last_update: $ts,
            status: $status,
            updates_applied: $updated,
            reboot_required: $needs_reboot
        }')
    write_state "$state_file" "$state"
    
    if [[ "$needs_reboot" == "true" ]]; then
        return 10
    fi
    
    return 0
}

# Export function for module
update_module() {
    run_update "$@"
}
