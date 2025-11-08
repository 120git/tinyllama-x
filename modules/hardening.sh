#!/usr/bin/env bash
#
# Hardening module - Security hardening rules
#

run_hardening() {
    log_info "Starting security hardening..."
    
    # Require root for hardening
    require_root
    
    local checks_passed=0
    local checks_failed=0
    
    # Check and configure SSH
    log_info "Checking SSH configuration..."
    if [[ -f /etc/ssh/sshd_config ]]; then
        # Check for PermitRootLogin
        if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config; then
            log_info "✓ SSH: PermitRootLogin is disabled"
            checks_passed=$((checks_passed + 1))
        else
            log_info "✗ SSH: PermitRootLogin should be disabled"
            checks_failed=$((checks_failed + 1))
            if [[ "${DRY_RUN:-false}" == "false" ]]; then
                # This is just a check, actual modification needs careful handling
                log_info "  To fix: Set 'PermitRootLogin no' in /etc/ssh/sshd_config"
            fi
        fi
        
        # Check for PasswordAuthentication
        if grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config; then
            log_info "✓ SSH: Password authentication is disabled (key-only)"
            checks_passed=$((checks_passed + 1))
        else
            log_info "⚠ SSH: Consider disabling password authentication"
        fi
    else
        log_info "SSH not configured or not installed"
    fi
    
    # Check firewall status
    log_info "Checking firewall status..."
    if command_exists ufw; then
        if ufw status | grep -q "Status: active"; then
            log_info "✓ Firewall: UFW is active"
            checks_passed=$((checks_passed + 1))
        else
            log_info "✗ Firewall: UFW is not active"
            checks_failed=$((checks_failed + 1))
            if [[ "${DRY_RUN:-false}" == "false" ]]; then
                log_info "  To fix: Run 'ufw enable'"
            fi
        fi
    elif command_exists firewall-cmd; then
        if firewall-cmd --state 2>/dev/null | grep -q "running"; then
            log_info "✓ Firewall: firewalld is running"
            checks_passed=$((checks_passed + 1))
        else
            log_info "✗ Firewall: firewalld is not running"
            checks_failed=$((checks_failed + 1))
        fi
    else
        log_info "⚠ No firewall detected (ufw/firewalld)"
    fi
    
    # Check automatic updates
    log_info "Checking automatic updates..."
    if [[ -f /etc/apt/apt.conf.d/20auto-upgrades ]]; then
        log_info "✓ Automatic updates: configured (APT)"
        checks_passed=$((checks_passed + 1))
    elif [[ -f /etc/dnf/automatic.conf ]]; then
        log_info "✓ Automatic updates: configured (DNF)"
        checks_passed=$((checks_passed + 1))
    else
        log_info "⚠ Automatic updates: not configured"
    fi
    
    # Summary
    log_success "Hardening check complete: $checks_passed passed, $checks_failed failed"
    
    if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
        echo "{\"checks_passed\":$checks_passed,\"checks_failed\":$checks_failed}"
    fi
    
    log_to_file "Security hardening check completed: $checks_passed passed, $checks_failed failed"
}
