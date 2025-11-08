#!/usr/bin/env bats
# health.bats - Health module tests

setup() {
    # Get the path to ubopt
    UBOPT_CMD="${BATS_TEST_DIRNAME}/../../cmd/ubopt"
    export PATH="${BATS_TEST_DIRNAME}/../../cmd:$PATH"
}

@test "health command runs without errors" {
    run "$UBOPT_CMD" health
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]  # 0 = healthy, 4 = critical issues
}

@test "health --json outputs valid JSON" {
    run "$UBOPT_CMD" --json health
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    # Check if output is valid JSON
    echo "$output" | jq empty
}

@test "health --json includes required fields" {
    run "$UBOPT_CMD" --json health
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    # Check for required top-level fields
    echo "$output" | jq -e '.timestamp' > /dev/null
    echo "$output" | jq -e '.system' > /dev/null
    echo "$output" | jq -e '.disks' > /dev/null
    echo "$output" | jq -e '.memory' > /dev/null
    echo "$output" | jq -e '.load' > /dev/null
}

@test "health --json system info includes hostname" {
    run "$UBOPT_CMD" --json health
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    echo "$output" | jq -e '.system.hostname' > /dev/null
    echo "$output" | jq -e '.system.kernel' > /dev/null
}

@test "health --json memory info is valid" {
    run "$UBOPT_CMD" --json health
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    echo "$output" | jq -e '.memory.total_kb' > /dev/null
    echo "$output" | jq -e '.memory.use_percent' > /dev/null
    echo "$output" | jq -e '.memory.status' > /dev/null
}

@test "health --json load info is valid" {
    run "$UBOPT_CMD" --json health
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    echo "$output" | jq -e '.load.load_1min' > /dev/null
    echo "$output" | jq -e '.load.cpu_count' > /dev/null
}

@test "health --format json works" {
    run "$UBOPT_CMD" health --format json
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    # Should output valid JSON
    echo "$output" | jq empty
}

@test "health --format text works" {
    run "$UBOPT_CMD" health --format text
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    [[ "$output" =~ "System Health Report" ]]
    [[ "$output" =~ "Hostname:" ]]
}

@test "health --format prometheus works" {
    run "$UBOPT_CMD" health --format prometheus
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    [[ "$output" =~ "# HELP" ]]
    [[ "$output" =~ "# TYPE" ]]
}

@test "health with --output writes to file" {
    local temp_file
    temp_file=$(mktemp)
    
    run "$UBOPT_CMD" health --format json --output "$temp_file"
    [ "$status" -eq 0 ] || [ "$status" -eq 4 ]
    
    # Check file exists and contains JSON
    [ -f "$temp_file" ]
    cat "$temp_file" | jq empty
    
    rm -f "$temp_file"
}
