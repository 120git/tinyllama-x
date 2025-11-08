#!/usr/bin/env bash
#
# DNF provider for Fedora/RHEL
#

# Update package lists
provider_update_cache() {
    safe_exec "dnf check-update" || true
}

# Upgrade packages
provider_upgrade() {
    local flags="-y"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        flags="--assumeno"
    fi
    
    safe_exec "dnf upgrade $flags"
}

# Install package
provider_install() {
    local package="$1"
    local flags="-y"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        flags="--assumeno"
    fi
    
    safe_exec "dnf install $flags $package"
}

# Remove package
provider_remove() {
    local package="$1"
    local flags="-y"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        flags="--assumeno"
    fi
    
    safe_exec "dnf remove $flags $package"
}

# Check if package is installed
provider_is_installed() {
    local package="$1"
    rpm -q "$package" >/dev/null 2>&1
}

# List upgradable packages
provider_list_upgradable() {
    dnf list updates 2>/dev/null | tail -n +2
}

# Clean package cache
provider_clean() {
    safe_exec "dnf clean all"
    safe_exec "dnf autoremove -y"
}
