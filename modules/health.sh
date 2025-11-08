#!/usr/bin/env bash
#
# Health module - System health checks
#

run_health() {
    log_info "Running system health checks..."
    
    local warnings=0
    local errors=0
    
    # Check disk space
    log_info "Checking disk space..."
    local disk_usage
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ $disk_usage -lt 70 ]]; then
        log_info "✓ Disk space: ${disk_usage}% used (healthy)"
    elif [[ $disk_usage -lt 90 ]]; then
        log_info "⚠ Disk space: ${disk_usage}% used (warning)"
        warnings=$((warnings + 1))
    else
        log_error "✗ Disk space: ${disk_usage}% used (critical)"
        errors=$((errors + 1))
    fi
    
    # Check memory usage
    log_info "Checking memory usage..."
    if command_exists free; then
        local mem_usage
        mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}' 2>/dev/null || echo "0")
        
        if [[ $mem_usage -lt 80 ]]; then
            log_info "✓ Memory usage: ${mem_usage}% (healthy)"
        elif [[ $mem_usage -lt 95 ]]; then
            log_info "⚠ Memory usage: ${mem_usage}% (warning)"
            warnings=$((warnings + 1))
        else
            log_error "✗ Memory usage: ${mem_usage}% (critical)"
            errors=$((errors + 1))
        fi
    fi
    
    # Check CPU load
    log_info "Checking CPU load..."
    if [[ -f /proc/loadavg ]]; then
        local load_avg
        load_avg=$(awk '{print $1}' /proc/loadavg)
        local cpu_count
        cpu_count=$(nproc)
        
        log_info "Load average: $load_avg (CPUs: $cpu_count)"
        
        # Simple check: load > 2*cpu_count is concerning
        local load_threshold=$((cpu_count * 2))
        # Use awk for floating point comparison if bc is not available
        local is_high=0
        if command_exists bc; then
            is_high=$(echo "$load_avg > $load_threshold" | bc -l 2>/dev/null || echo 0)
        else
            is_high=$(awk -v load="$load_avg" -v thresh="$load_threshold" 'BEGIN {print (load > thresh) ? 1 : 0}')
        fi
        
        if [[ $is_high -eq 1 ]]; then
            log_info "⚠ CPU load is high"
            warnings=$((warnings + 1))
        else
            log_info "✓ CPU load is normal"
        fi
    fi
    
    # Check for failed systemd services
    log_info "Checking failed services..."
    if command_exists systemctl; then
        local failed_services
        failed_services=$(systemctl --failed --no-legend 2>/dev/null | wc -l)
        
        if [[ $failed_services -eq 0 ]]; then
            log_info "✓ No failed services"
        else
            log_info "⚠ Failed services: $failed_services"
            warnings=$((warnings + 1))
            systemctl --failed --no-legend 2>/dev/null | head -5
        fi
    fi
    
    # Check system uptime
    log_info "System uptime: $(uptime -p 2>/dev/null || uptime)"
    
    # Summary
    if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
        log_success "System health: All checks passed"
    elif [[ $errors -eq 0 ]]; then
        log_info "System health: $warnings warnings"
    else
        log_error "System health: $errors errors, $warnings warnings"
    fi
    
    if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
        echo "{\"errors\":$errors,\"warnings\":$warnings,\"disk_usage\":${disk_usage}}"
    fi
    
    log_to_file "Health check completed: $errors errors, $warnings warnings"
}
