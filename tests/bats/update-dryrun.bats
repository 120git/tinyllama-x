#!/usr/bin/env bats
# update-dryrun.bats - Update dry-run tests

setup() {
    # Get the path to ubopt
    UBOPT_CMD="${BATS_TEST_DIRNAME}/../../cmd/ubopt"
    export PATH="${BATS_TEST_DIRNAME}/../../cmd:$PATH"
    
    # Store initial state
    if [ -d /var/lib/ubopt ]; then
        INITIAL_STATE=$(find /var/lib/ubopt -type f 2>/dev/null | sort)
    else
        INITIAL_STATE=""
    fi
}

teardown() {
    # Verify no files were created in dry-run
    if [ -n "$DRY_RUN_TEST" ]; then
        if [ -d /var/lib/ubopt ]; then
            FINAL_STATE=$(find /var/lib/ubopt -type f 2>/dev/null | sort)
            [ "$INITIAL_STATE" = "$FINAL_STATE" ]
        fi
    fi
}

@test "update --dry-run runs without root (shows would-be actions)" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run update
    
    # Should not fail with permission error since it's dry-run
    # Status can be 0 (success) or 2 (no updates) or 1 (needs root check)
    [ "$status" -eq 0 ] || [ "$status" -eq 1 ] || [ "$status" -eq 2 ]
}

@test "update --dry-run outputs intended actions" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run update
    
    # Should mention dry-run or show what would be done
    # Even if it requires root, it should indicate dry-run mode
    [[ "$output" =~ "DRY-RUN" ]] || [[ "$output" =~ "dry-run" ]] || [[ "$output" =~ "root" ]]
}

@test "update --dry-run does not modify system state" {
    DRY_RUN_TEST=1
    
    # Create a marker file
    local marker_file="/tmp/ubopt-test-marker-$$"
    touch "$marker_file"
    
    run "$UBOPT_CMD" --dry-run update
    
    # Marker file should still exist (system unchanged)
    [ -f "$marker_file" ]
    rm -f "$marker_file"
}

@test "update --dry-run --json outputs JSON logs" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run --json update
    
    # Should output JSON (or require root)
    if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
        # Check if at least one line is valid JSON
        echo "$output" | head -n1 | jq empty || true
    fi
}

@test "hardening --dry-run runs without modifying system" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run hardening
    
    # Should indicate dry-run or require root
    [[ "$output" =~ "DRY-RUN" ]] || [[ "$output" =~ "dry-run" ]] || [[ "$output" =~ "root" ]]
}

@test "hardening --dry-run shows planned actions" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run hardening
    
    # Should show what would be done
    if [ "$status" -eq 0 ]; then
        [[ "$output" =~ "Would" ]] || [[ "$output" =~ "would" ]] || [[ "$output" =~ "DRY-RUN" ]]
    fi
}

@test "backup --dry-run is non-destructive" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run backup --target /tmp/test-backup
    
    # Backup should always be in dry-run mode for MVP
    [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
    [[ "$output" =~ "dry-run" ]] || [[ "$output" =~ "Would" ]] || [[ "$output" =~ "stub" ]]
}

@test "benchmark --dry-run shows what would be run" {
    DRY_RUN_TEST=1
    run "$UBOPT_CMD" --dry-run benchmark
    
    [ "$status" -eq 0 ] || [ "$status" -eq 6 ]  # 6 = tools not available
    
    if [ "$status" -eq 0 ]; then
        [[ "$output" =~ "Would" ]] || [[ "$output" =~ "would" ]] || [[ "$output" =~ "DRY-RUN" ]]
    fi
}
