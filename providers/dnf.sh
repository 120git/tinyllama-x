#!/usr/bin/env bash
# dnf.sh - DNF package manager provider

# Update package metadata
pkg_update() {
    log_info "dnf" "Updating package metadata"
    
    if confirm_dry_run dnf check-update; then
        return 0
    fi
    
    # dnf check-update returns 100 if updates are available
    dnf check-update -q &>/dev/null || true
}

# Upgrade installed packages
pkg_upgrade() {
    local security_only="${1:-false}"
    
    if [[ "$security_only" == "true" ]]; then
        log_info "dnf" "Upgrading security packages only"
        
        if confirm_dry_run dnf upgrade --security -y; then
            return 0
        fi
        
        run_safely "dnf security upgrade" dnf upgrade --security -y
    else
        log_info "dnf" "Upgrading all packages"
        
        if confirm_dry_run dnf upgrade -y; then
            return 0
        fi
        
        run_safely "dnf upgrade" dnf upgrade -y
    fi
}

# Install specific package
pkg_install() {
    local package="$1"
    
    if package_installed "$package"; then
        log_info "dnf" "Package already installed: $package"
        return 0
    fi
    
    log_info "dnf" "Installing package: $package"
    
    if confirm_dry_run dnf install -y "$package"; then
        return 0
    fi
    
    run_safely "dnf install $package" dnf install -y "$package"
}

# Check if package is available
pkg_available() {
    local package="$1"
    dnf info "$package" &>/dev/null
}

# Check for security updates
security_updates_available() {
    log_debug "dnf" "Checking for security updates"
    
    local security_count
    security_count=$(dnf updateinfo list security 2>/dev/null | grep -c "^FEDORA-" || echo "0")
    
    if [[ "$security_count" -gt 0 ]]; then
        log_info "dnf" "Security updates available: $security_count"
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            json_log "INFO" "dnf" "Security updates available" "{\"count\": $security_count}"
        fi
        return 0
    else
        log_info "dnf" "No security updates available"
        return 1
    fi
}

# List available security updates
list_security_updates() {
    dnf updateinfo list security 2>/dev/null | awk '{print $3}' || true
}

# Check if reboot required
reboot_required() {
    # Check if kernel or systemd was updated
    needs-restarting -r &>/dev/null
    [[ $? -eq 1 ]]
}

# Clean package cache
pkg_clean() {
    log_info "dnf" "Cleaning package cache"
    
    if confirm_dry_run dnf clean all; then
        return 0
    fi
    
    run_safely "dnf clean" dnf clean all
    run_safely "dnf autoremove" dnf autoremove -y
}
