#!/usr/bin/env bash
# hardening.sh - Security hardening module

# Apply SSH hardening
harden_ssh() {
    log_info "hardening" "Applying SSH hardening"
    
    local sshd_config="/etc/ssh/sshd_config"
    
    if [[ ! -f "$sshd_config" ]]; then
        log_warn "hardening" "SSH config not found, skipping SSH hardening"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "hardening" "DRY-RUN: Would apply SSH hardening:"
        echo "  - Disable root login" >&2
        echo "  - Disable password authentication" >&2
        echo "  - Restart sshd service" >&2
        return 0
    fi
    
    # Backup original config
    if [[ ! -f "${sshd_config}.ubopt.bak" ]]; then
        cp "$sshd_config" "${sshd_config}.ubopt.bak"
        log_info "hardening" "Backed up SSH config to ${sshd_config}.ubopt.bak"
    fi
    
    # Disable root login
    if grep -q "^PermitRootLogin" "$sshd_config"; then
        sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' "$sshd_config"
    else
        echo "PermitRootLogin no" >> "$sshd_config"
    fi
    
    # Disable password authentication
    if grep -q "^PasswordAuthentication" "$sshd_config"; then
        sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' "$sshd_config"
    else
        echo "PasswordAuthentication no" >> "$sshd_config"
    fi
    
    # Validate config
    if sshd -t; then
        log_info "hardening" "SSH config validated"
        
        # Restart SSH service
        if systemctl restart sshd 2>/dev/null || systemctl restart ssh 2>/dev/null; then
            log_info "hardening" "SSH service restarted"
        else
            log_warn "hardening" "Failed to restart SSH service"
        fi
    else
        log_error "hardening" "SSH config validation failed, reverting"
        cp "${sshd_config}.ubopt.bak" "$sshd_config"
        return 1
    fi
}

# Enable unattended upgrades (apt only)
enable_unattended_upgrades() {
    local pm
    pm=$(detect_package_manager)
    
    if [[ "$pm" != "apt" ]]; then
        log_info "hardening" "Unattended upgrades only supported on apt-based systems"
        return 0
    fi
    
    log_info "hardening" "Enabling unattended-upgrades"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "hardening" "DRY-RUN: Would install and enable unattended-upgrades"
        return 0
    fi
    
    # Install unattended-upgrades if not present
    if ! package_installed "unattended-upgrades"; then
        load_provider
        pkg_install "unattended-upgrades"
    fi
    
    # Configure for automatic security updates
    local config_file="/etc/apt/apt.conf.d/50unattended-upgrades"
    if [[ -f "$config_file" ]]; then
        # Enable automatic updates
        cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
        log_info "hardening" "Unattended upgrades enabled"
    fi
}

# Apply sysctl hardening
apply_sysctl_hardening() {
    log_info "hardening" "Applying sysctl hardening"
    
    local sysctl_file="/etc/sysctl.d/90-ubopt.conf"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "hardening" "DRY-RUN: Would create $sysctl_file with security settings"
        return 0
    fi
    
    cat > "$sysctl_file" <<EOF
# UbuntOptimizer security hardening
# Applied: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

# IP forwarding (disable if not a router)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# Ignore ICMP ping requests (optional, can break some monitoring)
# net.ipv4.icmp_echo_ignore_all = 1

# Log suspicious packets
net.ipv4.conf.all.log_martians = 1

# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Protect against time-wait assassination
net.ipv4.tcp_rfc1337 = 1
EOF
    
    # Apply settings
    if sysctl -p "$sysctl_file" &>/dev/null; then
        log_info "hardening" "Sysctl hardening applied"
    else
        log_warn "hardening" "Failed to apply some sysctl settings"
    fi
}

# Configure UFW firewall
configure_firewall() {
    log_info "hardening" "Configuring firewall (ufw)"
    
    if ! command_exists ufw; then
        log_info "hardening" "UFW not installed, skipping firewall configuration"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "hardening" "DRY-RUN: Would configure UFW:"
        echo "  - Set default deny incoming" >&2
        echo "  - Set default allow outgoing" >&2
        echo "  - Allow SSH (port 22)" >&2
        echo "  - Enable firewall" >&2
        return 0
    fi
    
    # Set defaults
    ufw --force default deny incoming
    ufw --force default allow outgoing
    
    # Allow SSH (don't lock yourself out!)
    ufw --force allow 22/tcp comment "SSH"
    
    # Enable firewall
    if confirm "Enable UFW firewall? (ensure SSH access is configured)"; then
        ufw --force enable
        log_info "hardening" "UFW firewall enabled"
    else
        log_info "hardening" "UFW firewall configuration skipped"
    fi
}

# Main hardening function
run_hardening() {
    local ssh_only="${1:-false}"
    local firewall_only="${2:-false}"
    local skip_ssh="${3:-false}"
    local skip_firewall="${4:-false}"
    
    require_root
    
    log_info "hardening" "Starting security hardening"
    
    local failed=0
    
    # Apply SSH hardening
    if [[ "$firewall_only" != "true" ]] && [[ "$skip_ssh" != "true" ]]; then
        if ! harden_ssh; then
            log_error "hardening" "SSH hardening failed"
            ((failed++))
        fi
    fi
    
    if [[ "$ssh_only" == "true" ]]; then
        if [[ $failed -gt 0 ]]; then
            return 3
        fi
        return 0
    fi
    
    # Enable unattended upgrades
    if [[ "$firewall_only" != "true" ]]; then
        if ! enable_unattended_upgrades; then
            log_error "hardening" "Unattended upgrades setup failed"
            ((failed++))
        fi
    fi
    
    # Apply sysctl hardening
    if [[ "$firewall_only" != "true" ]]; then
        if ! apply_sysctl_hardening; then
            log_error "hardening" "Sysctl hardening failed"
            ((failed++))
        fi
    fi
    
    # Configure firewall
    if [[ "$ssh_only" != "true" ]] && [[ "$skip_firewall" != "true" ]]; then
        if ! configure_firewall; then
            log_error "hardening" "Firewall configuration failed"
            ((failed++))
        fi
    fi
    
    if [[ $failed -gt 0 ]]; then
        log_warn "hardening" "Hardening completed with $failed failure(s)"
        return 3
    fi
    
    log_info "hardening" "Security hardening completed successfully"
    return 0
}

# Export function for module
hardening_module() {
    run_hardening "$@"
}
