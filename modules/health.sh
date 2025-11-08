#!/usr/bin/env bash
# health.sh - System health monitoring module

# Gather system information
gather_system_info() {
    local hostname
    local kernel
    local uptime_seconds
    local os_name
    local os_version
    
    hostname=$(hostname)
    kernel=$(uname -r)
    uptime_seconds=$(awk '{print int($1)}' /proc/uptime)
    
    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        source /etc/os-release
        os_name="${NAME:-unknown}"
        os_version="${VERSION_ID:-unknown}"
    else
        os_name="unknown"
        os_version="unknown"
    fi
    
    jq -n \
        --arg host "$hostname" \
        --arg kern "$kernel" \
        --argjson uptime "$uptime_seconds" \
        --arg os "$os_name" \
        --arg ver "$os_version" \
        '{
            hostname: $host,
            kernel: $kern,
            uptime_seconds: $uptime,
            os_name: $os,
            os_version: $ver
        }'
}

# Check disk space
check_disk_space() {
    local disks=()
    
    while IFS= read -r line; do
        local filesystem mountpoint used avail use_pct
        filesystem=$(echo "$line" | awk '{print $1}')
        mountpoint=$(echo "$line" | awk '{print $6}')
        used=$(echo "$line" | awk '{print $3}')
        avail=$(echo "$line" | awk '{print $4}')
        use_pct=$(echo "$line" | awk '{print $5}' | tr -d '%')
        
        local status="ok"
        if [[ "$use_pct" -gt 90 ]]; then
            status="critical"
        elif [[ "$use_pct" -gt 80 ]]; then
            status="warning"
        fi
        
        disks+=("$(jq -n \
            --arg fs "$filesystem" \
            --arg mp "$mountpoint" \
            --arg used "$used" \
            --arg avail "$avail" \
            --argjson pct "$use_pct" \
            --arg status "$status" \
            '{
                filesystem: $fs,
                mountpoint: $mp,
                used: $used,
                available: $avail,
                use_percent: $pct,
                status: $status
            }')")
    done < <(df -h | tail -n +2 | grep -E '^/dev/')
    
    # Combine into JSON array
    local json_array="["
    local first=true
    for disk in "${disks[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            json_array+=","
        fi
        json_array+="$disk"
    done
    json_array+="]"
    
    echo "$json_array"
}

# Check SMART status
check_smart_status() {
    if ! command_exists smartctl; then
        echo "[]"
        return
    fi
    
    local smart_devices=()
    
    # Find all block devices
    while IFS= read -r device; do
        local dev_name="/dev/$device"
        local status
        
        if smartctl -H "$dev_name" &>/dev/null; then
            status="passed"
        else
            status="unknown"
        fi
        
        smart_devices+=("$(jq -n \
            --arg dev "$dev_name" \
            --arg status "$status" \
            '{
                device: $dev,
                status: $status
            }')")
    done < <(lsblk -d -n -o NAME 2>/dev/null | grep -E '^sd|^nvme' || true)
    
    # Combine into JSON array
    local json_array="["
    local first=true
    for dev in "${smart_devices[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            json_array+=","
        fi
        json_array+="$dev"
    done
    json_array+="]"
    
    echo "$json_array"
}

# Check critical services
check_critical_services() {
    local services=("sshd" "ssh" "systemd-resolved" "cron" "atd")
    local service_status=()
    
    for service in "${services[@]}"; do
        if systemctl list-unit-files "$service.service" &>/dev/null; then
            local status
            local is_active
            local is_enabled
            
            if systemctl is-active "$service" &>/dev/null; then
                is_active="active"
            else
                is_active="inactive"
            fi
            
            if systemctl is-enabled "$service" &>/dev/null; then
                is_enabled="enabled"
            else
                is_enabled="disabled"
            fi
            
            status="ok"
            if [[ "$is_active" != "active" ]] && [[ "$is_enabled" == "enabled" ]]; then
                status="warning"
            fi
            
            service_status+=("$(jq -n \
                --arg name "$service" \
                --arg active "$is_active" \
                --arg enabled "$is_enabled" \
                --arg status "$status" \
                '{
                    name: $name,
                    active: $active,
                    enabled: $enabled,
                    status: $status
                }')")
        fi
    done
    
    # Combine into JSON array
    local json_array="["
    local first=true
    for svc in "${service_status[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            json_array+=","
        fi
        json_array+="$svc"
    done
    json_array+="]"
    
    echo "$json_array"
}

# Check memory usage
check_memory() {
    local total used available
    
    while IFS= read -r line; do
        case "$line" in
            MemTotal:*)
                total=$(echo "$line" | awk '{print $2}')
                ;;
            MemAvailable:*)
                available=$(echo "$line" | awk '{print $2}')
                ;;
        esac
    done < /proc/meminfo
    
    used=$((total - available))
    local use_pct=$((used * 100 / total))
    
    local status="ok"
    if [[ "$use_pct" -gt 90 ]]; then
        status="critical"
    elif [[ "$use_pct" -gt 80 ]]; then
        status="warning"
    fi
    
    jq -n \
        --argjson total "$total" \
        --argjson used "$used" \
        --argjson avail "$available" \
        --argjson pct "$use_pct" \
        --arg status "$status" \
        '{
            total_kb: $total,
            used_kb: $used,
            available_kb: $avail,
            use_percent: $pct,
            status: $status
        }'
}

# Check load average
check_load() {
    local load_1 load_5 load_15
    read -r load_1 load_5 load_15 _ < /proc/loadavg
    
    local cpu_count
    cpu_count=$(nproc)
    
    jq -n \
        --arg l1 "$load_1" \
        --arg l5 "$load_5" \
        --arg l15 "$load_15" \
        --argjson cpus "$cpu_count" \
        '{
            load_1min: $l1,
            load_5min: $l5,
            load_15min: $l15,
            cpu_count: $cpus
        }'
}

# Main health check function
run_health() {
    local format="${1:-json}"
    local output_file="${2:-}"
    
    log_debug "health" "Gathering system health information"
    
    # Gather all health data
    local system_info
    local disk_info
    local smart_info
    local service_info
    local memory_info
    local load_info
    
    system_info=$(gather_system_info)
    disk_info=$(check_disk_space)
    smart_info=$(check_smart_status)
    service_info=$(check_critical_services)
    memory_info=$(check_memory)
    load_info=$(check_load)
    
    # Combine into single JSON
    local health_report
    health_report=$(jq -n \
        --argjson sys "$system_info" \
        --argjson disk "$disk_info" \
        --argjson smart "$smart_info" \
        --argjson svc "$service_info" \
        --argjson mem "$memory_info" \
        --argjson load "$load_info" \
        --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        '{
            timestamp: $ts,
            system: $sys,
            disks: $disk,
            smart: $smart,
            services: $svc,
            memory: $mem,
            load: $load
        }')
    
    # Determine overall health status
    local critical_issues=0
    
    # Check for critical disk space
    if echo "$health_report" | jq -e '.disks[] | select(.status == "critical")' &>/dev/null; then
        ((critical_issues++))
    fi
    
    # Check for critical memory usage
    if echo "$health_report" | jq -e '.memory.status == "critical"' &>/dev/null; then
        ((critical_issues++))
    fi
    
    # Check for stopped critical services
    if echo "$health_report" | jq -e '.services[] | select(.status == "warning")' &>/dev/null; then
        ((critical_issues++))
    fi
    
    # Output based on format
    if [[ "$format" == "json" ]]; then
        if [[ -n "$output_file" ]]; then
            echo "$health_report" > "$output_file"
            log_info "health" "Health report written to $output_file"
        else
            echo "$health_report"
        fi
    elif [[ "$format" == "prometheus" ]]; then
        # Convert to Prometheus textfile format
        local prom_output=""
        prom_output+="# HELP ubopt_disk_usage_percent Disk usage percentage\n"
        prom_output+="# TYPE ubopt_disk_usage_percent gauge\n"
        
        while IFS= read -r disk; do
            local mp use_pct
            mp=$(echo "$disk" | jq -r '.mountpoint')
            use_pct=$(echo "$disk" | jq -r '.use_percent')
            prom_output+="ubopt_disk_usage_percent{mountpoint=\"$mp\"} $use_pct\n"
        done < <(echo "$health_report" | jq -c '.disks[]')
        
        prom_output+="# HELP ubopt_memory_usage_percent Memory usage percentage\n"
        prom_output+="# TYPE ubopt_memory_usage_percent gauge\n"
        local mem_pct
        mem_pct=$(echo "$health_report" | jq -r '.memory.use_percent')
        prom_output+="ubopt_memory_usage_percent $mem_pct\n"
        
        prom_output+="# HELP ubopt_load_average System load average\n"
        prom_output+="# TYPE ubopt_load_average gauge\n"
        local load_1
        load_1=$(echo "$health_report" | jq -r '.load.load_1min')
        prom_output+="ubopt_load_average{period=\"1min\"} $load_1\n"
        
        if [[ -n "$output_file" ]]; then
            echo -e "$prom_output" > "$output_file"
            log_info "health" "Prometheus metrics written to $output_file"
        else
            echo -e "$prom_output"
        fi
    else
        # Text format
        echo "System Health Report - $(date)"
        echo "===================================="
        echo ""
        echo "Hostname: $(echo "$health_report" | jq -r '.system.hostname')"
        echo "Kernel: $(echo "$health_report" | jq -r '.system.kernel')"
        echo "Uptime: $(($(echo "$health_report" | jq -r '.system.uptime_seconds') / 3600)) hours"
        echo ""
        echo "Memory: $(echo "$health_report" | jq -r '.memory.use_percent')% used ($(echo "$health_report" | jq -r '.memory.status'))"
        echo "Load: $(echo "$health_report" | jq -r '.load.load_1min') (1min)"
        echo ""
        echo "Disk Space:"
        echo "$health_report" | jq -r '.disks[] | "  \(.mountpoint): \(.use_percent)% used (\(.status))"'
        echo ""
        echo "Services:"
        echo "$health_report" | jq -r '.services[] | "  \(.name): \(.active)/\(.enabled) (\(.status))"'
    fi
    
    if [[ $critical_issues -gt 0 ]]; then
        log_warn "health" "Critical issues detected: $critical_issues"
        return 4
    fi
    
    return 0
}

# Export function for module
health_module() {
    run_health "$@"
}
