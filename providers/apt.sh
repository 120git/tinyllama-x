#!/usr/bin/env bash
#
# APT provider for Ubuntu/Debian
#

# Update package lists
provider_update_cache() {
    safe_exec "apt-get update -qq"
}

# Upgrade packages
provider_upgrade() {
    local flags="-y"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        flags="--dry-run"
    fi
    
    safe_exec "apt-get upgrade $flags"
}

# Install package
provider_install() {
    local package="$1"
    local flags="-y"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        flags="--dry-run"
    fi
    
    safe_exec "apt-get install $flags $package"
}

# Remove package
provider_remove() {
    local package="$1"
    local flags="-y"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        flags="--dry-run"
    fi
    
    safe_exec "apt-get remove $flags $package"
}

# Check if package is installed
provider_is_installed() {
    local package="$1"
    dpkg -l "$package" 2>/dev/null | grep -q "^ii"
}

# List upgradable packages
provider_list_upgradable() {
    apt list --upgradable 2>/dev/null | grep -v "^Listing"
}

# Clean package cache
provider_clean() {
    safe_exec "apt-get clean"
    safe_exec "apt-get autoclean"
    safe_exec "apt-get autoremove -y"
}
