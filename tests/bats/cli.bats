#!/usr/bin/env bats

# Test the main CLI functionality

setup() {
    # Set up test environment
    export PATH="$BATS_TEST_DIRNAME/../../cmd:$PATH"
    UBOPT_CMD="$BATS_TEST_DIRNAME/../../cmd/ubopt"
}

@test "ubopt command exists and is executable" {
    [ -x "$UBOPT_CMD" ]
}

@test "ubopt --help shows usage" {
    run "$UBOPT_CMD" --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage:" ]]
}

@test "ubopt --version shows version" {
    run "$UBOPT_CMD" --version
    [ "$status" -eq 0 ]
    [[ "$output" =~ "version" ]]
}

@test "ubopt without command shows error" {
    run "$UBOPT_CMD"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "No command specified" ]]
}

@test "ubopt with unknown command shows error" {
    run "$UBOPT_CMD" unknown-command
    [ "$status" -eq 1 ]
    [[ "$output" =~ "Unknown" ]]
}

@test "ubopt --json flag is recognized" {
    run "$UBOPT_CMD" --json --version
    [ "$status" -eq 0 ]
    [[ "$output" =~ "version" ]]
}

@test "ubopt version command works" {
    run "$UBOPT_CMD" version
    [ "$status" -eq 0 ]
    [[ "$output" =~ "version" ]]
}
