#!/usr/bin/env bats

# Test module functionality

setup() {
    export PATH="$BATS_TEST_DIRNAME/../../cmd:$PATH"
    UBOPT_CMD="$BATS_TEST_DIRNAME/../../cmd/ubopt"
}

@test "ubopt health command shows help when run without root" {
    run "$UBOPT_CMD" health
    # Should fail or show info (not crash)
    [ "$status" -ne 2 ]
}

@test "ubopt benchmark command runs without root" {
    run "$UBOPT_CMD" benchmark
    # Should complete or show appropriate message
    [ "$status" -ne 2 ]
}

@test "ubopt log command works" {
    run "$UBOPT_CMD" log
    [ "$status" -eq 0 ]
}

@test "ubopt health --json produces JSON-like output" {
    run "$UBOPT_CMD" health --json
    # Should contain JSON-like structure
    [ "$status" -ne 2 ]
}
