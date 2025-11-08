#!/usr/bin/env bash
# pacman.sh - Pacman package manager provider

# Update package metadata
pkg_update() {
    log_info "pacman" "Updating package metadata"
    
    if confirm_dry_run pacman -Sy; then
        return 0
    fi
    
    run_safely "pacman update" pacman -Sy --noconfirm
}

# Upgrade installed packages
pkg_upgrade() {
    local security_only="${1:-false}"
    
    # Pacman doesn't distinguish security updates
    if [[ "$security_only" == "true" ]]; then
        log_warn "pacman" "Pacman does not support security-only updates, performing full upgrade"
    fi
    
    log_info "pacman" "Upgrading all packages"
    
    if confirm_dry_run pacman -Su --noconfirm; then
        return 0
    fi
    
    run_safely "pacman upgrade" pacman -Su --noconfirm
}

# Install specific package
pkg_install() {
    local package="$1"
    
    if package_installed "$package"; then
        log_info "pacman" "Package already installed: $package"
        return 0
    fi
    
    log_info "pacman" "Installing package: $package"
    
    if confirm_dry_run pacman -S --noconfirm "$package"; then
        return 0
    fi
    
    run_safely "pacman install $package" pacman -S --noconfirm "$package"
}

# Check if package is available
pkg_available() {
    local package="$1"
    pacman -Si "$package" &>/dev/null
}

# Check for security updates
security_updates_available() {
    log_debug "pacman" "Checking for updates (Pacman does not distinguish security updates)"
    
    local update_count
    update_count=$(pacman -Qu 2>/dev/null | wc -l)
    
    if [[ "$update_count" -gt 0 ]]; then
        log_info "pacman" "Updates available: $update_count"
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            json_log "INFO" "pacman" "Updates available" "{\"count\": $update_count}"
        fi
        return 0
    else
        log_info "pacman" "No updates available"
        return 1
    fi
}

# List available updates
list_security_updates() {
    pacman -Qu 2>/dev/null | awk '{print $1}' || true
}

# Check if reboot required
reboot_required() {
    # Check if kernel was updated
    local running_kernel
    local installed_kernel
    
    running_kernel=$(uname -r | cut -d'-' -f1)
    installed_kernel=$(pacman -Q linux 2>/dev/null | awk '{print $2}' | cut -d'-' -f1)
    
    if [[ -n "$installed_kernel" ]] && [[ "$running_kernel" != "$installed_kernel" ]]; then
        return 0
    fi
    
    return 1
}

# Clean package cache
pkg_clean() {
    log_info "pacman" "Cleaning package cache"
    
    if confirm_dry_run pacman -Sc --noconfirm; then
        return 0
    fi
    
    run_safely "pacman clean" pacman -Sc --noconfirm
}
