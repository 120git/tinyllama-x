#!/usr/bin/env bash
# apt.sh - APT package manager provider

# Update package metadata
pkg_update() {
    log_info "apt" "Updating package metadata"
    
    if confirm_dry_run apt-get update; then
        return 0
    fi
    
    run_safely "apt update" apt-get update -qq
}

# Upgrade installed packages
pkg_upgrade() {
    local security_only="${1:-false}"
    
    if [[ "$security_only" == "true" ]]; then
        log_info "apt" "Upgrading security packages only"
        
        if confirm_dry_run apt-get upgrade --with-new-pkgs -s; then
            return 0
        fi
        
        # Use unattended-upgrades for security-only updates
        if command_exists unattended-upgrade; then
            run_safely "apt security upgrade" unattended-upgrade -v
        else
            log_warn "apt" "unattended-upgrades not installed, performing full upgrade"
            run_safely "apt upgrade" apt-get upgrade -y
        fi
    else
        log_info "apt" "Upgrading all packages"
        
        if confirm_dry_run apt-get upgrade -y; then
            return 0
        fi
        
        run_safely "apt upgrade" apt-get upgrade -y
    fi
}

# Install specific package
pkg_install() {
    local package="$1"
    
    if package_installed "$package"; then
        log_info "apt" "Package already installed: $package"
        return 0
    fi
    
    log_info "apt" "Installing package: $package"
    
    if confirm_dry_run apt-get install -y "$package"; then
        return 0
    fi
    
    run_safely "apt install $package" apt-get install -y "$package"
}

# Check if package is available
pkg_available() {
    local package="$1"
    apt-cache show "$package" &>/dev/null
}

# Check for security updates
security_updates_available() {
    log_debug "apt" "Checking for security updates"
    
    # Update cache first
    apt-get update -qq 2>/dev/null || true
    
    # Check for security updates
    local security_count
    security_count=$(apt-get upgrade -s 2>/dev/null | grep -c "^Inst.*security" || echo "0")
    
    if [[ "$security_count" -gt 0 ]]; then
        log_info "apt" "Security updates available: $security_count"
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            json_log "INFO" "apt" "Security updates available" "{\"count\": $security_count}"
        fi
        return 0
    else
        log_info "apt" "No security updates available"
        return 1
    fi
}

# List available security updates
list_security_updates() {
    apt-get upgrade -s 2>/dev/null | grep "^Inst.*security" | awk '{print $2}' || true
}

# Check if reboot required
reboot_required() {
    [[ -f /var/run/reboot-required ]]
}

# Clean package cache
pkg_clean() {
    log_info "apt" "Cleaning package cache"
    
    if confirm_dry_run apt-get clean; then
        return 0
    fi
    
    run_safely "apt clean" apt-get clean
    run_safely "apt autoremove" apt-get autoremove -y
}
