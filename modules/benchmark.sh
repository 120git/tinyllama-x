#!/usr/bin/env bash
#
# Benchmark module - Performance benchmarking
#

run_benchmark() {
    log_info "Running system performance benchmarks..."
    
    # CPU benchmark
    log_info "CPU benchmark..."
    if command_exists bc; then
        local start_time
        local end_time
        local duration
        
        start_time=$(date +%s.%N)
        echo "scale=5000; a(1)*4" | bc -l > /dev/null 2>&1
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        log_info "CPU calculation time: ${duration}s"
    else
        log_info "bc not available, skipping CPU benchmark"
    fi
    
    # Disk I/O benchmark
    log_info "Disk I/O benchmark..."
    local tmp_file="/tmp/ubopt_benchmark_$$"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_info "[DRY-RUN] Would run disk I/O test"
    else
        # Write test
        local write_start
        local write_end
        local write_speed
        
        write_start=$(date +%s.%N)
        dd if=/dev/zero of="$tmp_file" bs=1M count=100 2>/dev/null
        write_end=$(date +%s.%N)
        write_speed=$(echo "100 / ($write_end - $write_start)" | bc -l 2>/dev/null | head -c 5)
        
        log_info "Disk write speed: ${write_speed} MB/s"
        
        # Read test
        local read_start
        local read_end
        local read_speed
        
        read_start=$(date +%s.%N)
        dd if="$tmp_file" of=/dev/null bs=1M 2>/dev/null
        read_end=$(date +%s.%N)
        read_speed=$(echo "100 / ($read_end - $read_start)" | bc -l 2>/dev/null | head -c 5)
        
        log_info "Disk read speed: ${read_speed} MB/s"
        
        # Cleanup
        rm -f "$tmp_file"
    fi
    
    # Network benchmark (if possible)
    log_info "Network connectivity check..."
    if command_exists ping; then
        if ping -c 3 8.8.8.8 >/dev/null 2>&1; then
            log_info "✓ Network connectivity: OK"
        else
            log_info "✗ Network connectivity: Failed"
        fi
    fi
    
    # Memory info
    log_info "Memory information..."
    if command_exists free; then
        free -h
    fi
    
    if [[ "${OUTPUT_JSON:-false}" == "true" ]]; then
        echo "{\"benchmark\":\"completed\"}"
    fi
    
    log_success "Benchmark completed"
    log_to_file "Benchmark completed"
}
