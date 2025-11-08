#!/usr/bin/env bash
#
# Pacman provider for Arch Linux
#

# Update package lists
provider_update_cache() {
    safe_exec "pacman -Sy"
}

# Upgrade packages
provider_upgrade() {
    local flags="--noconfirm"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        echo "[DRY-RUN] Would run: pacman -Syu --noconfirm"
        return 0
    fi
    
    safe_exec "pacman -Syu $flags"
}

# Install package
provider_install() {
    local package="$1"
    local flags="--noconfirm"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        echo "[DRY-RUN] Would install: $package"
        return 0
    fi
    
    safe_exec "pacman -S $flags $package"
}

# Remove package
provider_remove() {
    local package="$1"
    local flags="--noconfirm"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        echo "[DRY-RUN] Would remove: $package"
        return 0
    fi
    
    safe_exec "pacman -R $flags $package"
}

# Check if package is installed
provider_is_installed() {
    local package="$1"
    pacman -Q "$package" >/dev/null 2>&1
}

# List upgradable packages
provider_list_upgradable() {
    pacman -Qu 2>/dev/null
}

# Clean package cache
provider_clean() {
    safe_exec "pacman -Sc --noconfirm"
}
