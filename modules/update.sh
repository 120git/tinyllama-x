#!/usr/bin/env bash
#
# Update module - System package updates
#

run_update() {
    log_info "Starting system update..."
    
    # Require root for updates
    require_root
    
    # Update package cache
    log_info "Updating package cache..."
    provider_update_cache
    
    # List upgradable packages
    log_info "Checking for available updates..."
    local upgradable
    upgradable=$(provider_list_upgradable)
    
    if [[ -z "$upgradable" ]]; then
        log_success "System is up to date"
        return 0
    fi
    
    if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
        echo "{\"status\":\"updates_available\",\"packages\":["
        echo "$upgradable" | while read -r line; do
            echo "\"$line\","
        done | sed '$ s/,$//'
        echo "]}"
    else
        echo "Available updates:"
        echo "$upgradable"
    fi
    
    # Perform upgrade
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "Dry-run mode: skipping actual upgrade"
    else
        log_info "Installing updates..."
        provider_upgrade
        log_success "System updated successfully"
    fi
    
    # Clean up
    log_info "Cleaning package cache..."
    provider_clean
    
    log_to_file "System update completed"
}
