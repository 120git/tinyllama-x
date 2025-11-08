#!/usr/bin/env bash
# benchmark.sh - System benchmark module (stub/MVP)

# Check for benchmark tools
check_benchmark_tools() {
    local has_fio=false
    local has_sysbench=false
    
    if command_exists fio; then
        has_fio=true
    fi
    
    if command_exists sysbench; then
        has_sysbench=true
    fi
    
    if [[ "$has_fio" == "false" ]] && [[ "$has_sysbench" == "false" ]]; then
        log_warn "benchmark" "No benchmark tools found (fio, sysbench)"
        log_info "benchmark" "Install with: apt install fio sysbench (or dnf/pacman)"
        return 1
    fi
    
    echo "fio=$has_fio sysbench=$has_sysbench"
    return 0
}

# Run disk benchmark
benchmark_disk() {
    log_info "benchmark" "Disk I/O benchmark"
    
    if ! command_exists fio; then
        log_warn "benchmark" "fio not installed, skipping disk benchmark"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "benchmark" "DRY-RUN: Would run fio disk benchmark"
        cat >&2 <<EOF
  fio --name=random-read --ioengine=libaio --rw=randread \\
      --bs=4k --size=1G --numjobs=4 --time_based \\
      --runtime=60 --group_reporting
EOF
        return 0
    fi
    
    log_info "benchmark" "Running fio benchmark (this may take a minute)..."
    echo "Disk benchmark results would appear here" >&2
}

# Run CPU benchmark
benchmark_cpu() {
    log_info "benchmark" "CPU benchmark"
    
    if ! command_exists sysbench; then
        log_warn "benchmark" "sysbench not installed, skipping CPU benchmark"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "benchmark" "DRY-RUN: Would run sysbench CPU benchmark"
        cat >&2 <<EOF
  sysbench cpu --cpu-max-prime=20000 --threads=4 run
EOF
        return 0
    fi
    
    log_info "benchmark" "Running sysbench CPU test (this may take a minute)..."
    echo "CPU benchmark results would appear here" >&2
}

# Run memory benchmark
benchmark_memory() {
    log_info "benchmark" "Memory benchmark"
    
    if ! command_exists sysbench; then
        log_warn "benchmark" "sysbench not installed, skipping memory benchmark"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "benchmark" "DRY-RUN: Would run sysbench memory benchmark"
        cat >&2 <<EOF
  sysbench memory --memory-block-size=1K --memory-total-size=10G run
EOF
        return 0
    fi
    
    log_info "benchmark" "Running sysbench memory test (this may take a minute)..."
    echo "Memory benchmark results would appear here" >&2
}

# Main benchmark function
run_benchmark() {
    local run_disk="${1:-false}"
    local run_cpu="${2:-false}"
    local run_memory="${3:-false}"
    local run_all=false
    
    if [[ "$run_disk" == "false" ]] && [[ "$run_cpu" == "false" ]] && [[ "$run_memory" == "false" ]]; then
        run_all=true
    fi
    
    log_info "benchmark" "System benchmark module (MVP stub)"
    
    # Check for tools
    if ! check_benchmark_tools; then
        return 6
    fi
    
    if [[ "$run_all" == "true" ]] || [[ "$run_disk" == "true" ]]; then
        benchmark_disk
    fi
    
    if [[ "$run_all" == "true" ]] || [[ "$run_cpu" == "true" ]]; then
        benchmark_cpu
    fi
    
    if [[ "$run_all" == "true" ]] || [[ "$run_memory" == "true" ]]; then
        benchmark_memory
    fi
    
    log_info "benchmark" "Benchmark completed"
    return 0
}

# Export function for module
benchmark_module() {
    run_benchmark "$@"
}
